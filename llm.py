from langchain_openai import ChatOpenAI
from langchain_core.prompts import (
    PromptTemplate,
    ChatPromptTemplate,
    FewShotChatMessagePromptTemplate,
    MessagesPlaceholder
)
from langchain_core.messages import (
    AIMessage,
    HumanMessage
)

import logging
import dotenv
from config import (
    DB_CONTEXT,
    DB_DIALECT,
    DB_COLLECTION_INFO,
)

from prompts import (
    DECIDE_RETRIEVAL_EXAMPLES, 
    DECIDE_RETRIEVAL_SYSTEM, 
    RETRIEVAL_SYSTEM,
    RETRIEVAL_EXAMPLES,
    CHAT_SYSTEM
)


from model import Context

import json

dotenv.load_dotenv()

logger = logging.getLogger()


def decide_retrieval(user_prompt: str):
    """Decide if a data retrieval request is present in the user prompt."""

    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=DECIDE_RETRIEVAL_EXAMPLES,
    )

    system_prompt = PromptTemplate(
        template=DECIDE_RETRIEVAL_SYSTEM, partial_variables={"db_context": DB_CONTEXT}
    ).format()

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    llm = ChatOpenAI(temperature=0.1, model='gpt-4o-mini')
    chain = final_prompt | llm
    response = chain.invoke(user_prompt).content
    logger.info(f"Retrieval Decision: {response}")
    return response

def write_nosql_query(user_prompt: str, access_purpose: str, k: int = 1):

    def parse(output: str):
        output_dict = json.loads(output)
        return output_dict
    
    def append_access_purpose(user_prompt: str, access_purpose: str):
        return f"{user_prompt} Access Purpose: '{access_purpose}'"
    
    example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=example_prompt,
        examples=RETRIEVAL_EXAMPLES,
    )
    system_prompt = PromptTemplate(
        template=RETRIEVAL_SYSTEM, partial_variables={"dialect": DB_DIALECT, "collection_info": DB_COLLECTION_INFO, "k": k}
    ).format()

    final_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            few_shot_prompt,
            ("human", "{input}"),
        ]
    )

    llm = ChatOpenAI(temperature=0, model='gpt-4o', model_kwargs={"response_format": {"type": "json_object"}})
    chain = final_prompt | llm
    output = chain.invoke(append_access_purpose(user_prompt, access_purpose)).content
    output_dict = parse(output)

    logger.info(f"NoSQL Action: {output_dict.get('action')}")
    logger.info(f"NoSQL Query: {output_dict.get('query')}")
    if output_dict.get('limit'):
        logger.info(f"Limit: {output_dict.get('limit')}")

    return Context(action=output_dict.get('action'), query=output_dict.get('query'), limit=output_dict.get('limit'))

def chat(user_prompt: str, chat_history: list = [], context: Context = Context()):
    chat = ChatOpenAI(temperature=0.2)

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", CHAT_SYSTEM),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )

    chain = prompt | chat
    response = chain.invoke(
        {"input": user_prompt, "chat_history": chat_history, "context": context, "db_context": DB_CONTEXT}).content
    
    logger.info(f"Chat Response: {response}")
    
    chat_history.extend([HumanMessage(content=user_prompt), AIMessage(content=response)])

    return response, chat_history, context


if __name__ == "__main__":
    pass
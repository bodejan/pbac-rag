import gradio as gr
from gradio import ChatMessage
from langchain_core.messages import AIMessage, HumanMessage, FunctionMessage
from dotenv import load_dotenv
import os

from backend.run import run
from backend.const import GRADIO_PURPOSES

load_dotenv()

with gr.Blocks(
    title="PBAC-RAG Bot",
    css=".content {text-align: left;}"
) as chat_app:

    gr.Markdown(
        "This chatbot allows you to interact with a PII extended version of the [California IMR Dataset](https://data.chhs.ca.gov/dataset/independent-medical-review-imr-determinations-trend).\n"
        "Information on the extension of the dataset is available [here](https://github.com/bodejan/california-imr-pii). "
        "The codebase is documented in the following [GitHub repository](https://github.com/bodejan/pbac-rag).\n"
        "Data access depends on the selected access purpose. Responses may include masked fields due to data access restrictions.",
        line_breaks=True
    )

    access_purpose = gr.Dropdown(
        choices=GRADIO_PURPOSES, interactive=True, label='Data Access Purpose', value='General-Purpose')

    chatbot = gr.Chatbot(type="messages", show_copy_button=True, bubble_full_width=False,
                         likeable=True, elem_classes=["style='text-align: left;"])
    msg = gr.Textbox(label="Type a message...",
                     placeholder="How many records are in the collection?")
    clear = gr.ClearButton([msg, chatbot])

    def predict(message, history, access_purpose):
        history_langchain_format = []
        for m in history:
            if m.get('role') == "user":
                history_langchain_format.append(
                    HumanMessage(content=m.get("content")))
            elif m.get('role') == "assistant" and m.get("metadata").get("title") == "🔍 Retrieval":
                history_langchain_format.append(FunctionMessage(
                    content=m.get("content"), name="retrieval"))
            elif m.get('role') == "assistant":
                history_langchain_format.append(
                    AIMessage(content=m.get("content")))
        history_langchain_format.append(HumanMessage(content=message))
        response = run(user_input=message, chat_history=history_langchain_format,
                       access_purpose=access_purpose)
        history.append(ChatMessage(role="user", content=message))

        if response.retrieval and not response.error_msg:
            history.append(ChatMessage(
                role="assistant", content=f"query: <code>{response.action} {response.query}</code>\nresult: <code>{response.result}</code>", metadata={"title": f"🔍 Retrieval"}))

        history.append(ChatMessage(role="assistant",
                       content=response.llm_response))

        return "", history

    def clear_history():
        return "", []

    access_purpose.change(clear_history, None, [msg, chatbot])
    msg.submit(predict, [msg, chatbot, access_purpose], [msg, chatbot])


if __name__ == "__main__":
    chat_app.launch()
    # chat_app.launch(auth=(os.getenv("GRADIO_USERNAME"), os.getenv("GRADIO_PASSWORD")))

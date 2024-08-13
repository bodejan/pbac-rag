import gradio as gr
from gradio import ChatMessage
from langchain.schema import AIMessage, HumanMessage
from run import run

from config import GRADIO_PURPOSES

with gr.Blocks(
    title="PBAC-enhanced Chatbot",
    css=".content {text-align: left;}"
) as chat_app:

    gr.Markdown(
        "# PBAC-enhanced Chatbot\n" +
        "This chatbot is designed to help you with your data access requests.\n" +
        "Remember to provide your data access purpose and signal a desired retrieval with keywords like *retrieve*, *query*, or *search*.\n",
        line_breaks=True
    )

    access_purpose = gr.Dropdown(
        choices=GRADIO_PURPOSES, interactive=True, label='Data Access Purpose', value='General-Purpose')
    
    chatbot = gr.Chatbot(type="messages", show_copy_button=True, bubble_full_width=False, likeable=True, elem_classes=["style='text-align: left;"])
    msg = gr.Textbox()
    clear = gr.ClearButton([msg, chatbot])
    
    def predict(message, history, access_purpose):
        history_langchain_format = []
        for m in history:
            if m.get('role') == "user":
                history_langchain_format.append(HumanMessage(content=m.get("content")))
            elif m.get('role') == "assistant" and m.get('content') != "":
                history_langchain_format.append(AIMessage(content=m.get("content")))
        history_langchain_format.append(HumanMessage(content=message))
        response, context = run(user_input=message, chat_history=history_langchain_format, access_purpose=access_purpose)
        history.append(ChatMessage(role="user", content=message))

        if context.action:
            history.append(ChatMessage(role="assistant", content=f"query: <code>{context.action} {context.query}</code>\nresult: <code>{context.result}</code>", metadata={"title": f"🔍 Retrieval"}))
        
        history.append(ChatMessage(role="assistant", content=response))

        return "", history


    msg.submit(predict, [msg, chatbot, access_purpose], [msg, chatbot])


if __name__ == "__main__":
    chat_app.launch()

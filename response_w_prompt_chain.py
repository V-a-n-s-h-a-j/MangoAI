from langchain_mistralai import ChatMistralAI

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)
import os

from dotenv import load_dotenv
load_dotenv()


from langchain_groq import ChatGroq
groq_api_key=os.environ['GROQ_API_KEY']

llm = ChatGroq(api_key=groq_api_key,model="mixtral-8x7b-32768")
# mistral_api_key  = os.environ["MISTRAL_API_KEY"]
# llm = ChatMistralAI(model="mistral-large-latest")

system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI assistant. Provide assistance based on the provided context"
)

def build_prompt_chain(history):
    prompt_sequence = [system_prompt]
    for msg in history:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    # print("promt sequence ----------------------------------------------->>>>.", "/n", prompt_sequence)
    # print("end ---------------------------------------------------------->>>>")
    return ChatPromptTemplate.from_messages(prompt_sequence)

def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | llm | StrOutputParser()
    return processing_pipeline.invoke({})

def respond(history):
    prompt_chain = build_prompt_chain(history)
    ai_response = generate_ai_response(prompt_chain)

    return ai_response

def generate_chat_title(user_message):
    prompt = f"Generate a short and relevant title (4-5 words) for the following message: {user_message}"
    try:
        title = llm.invoke(prompt)
        print(title)  # Call API only once
        return title.content  # Ensure clean title
    except Exception as e:
        print("Error generating chat title:", e)
        return "Untitled Chat"  # Fallback title

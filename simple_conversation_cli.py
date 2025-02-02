import time
import os
# from langchain_ollama import ChatOllama
from langchain_mistralai import ChatMistralAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import (
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
    AIMessagePromptTemplate,
    ChatPromptTemplate
)

from dotenv import load_dotenv
load_dotenv()

mistral_api_key  = os.environ["MISTRAL_API_KEY"]
# os.environ["MISTRAL_API_KEY"] = "vJ6LuLUeYqm1Uedzci7A2Fgh7tHnbS7p"
llm = ChatMistralAI(model="mistral-large-latest")


# System prompt configuration
system_prompt = SystemMessagePromptTemplate.from_template(
    "You are an expert AI assistant. Provide assistance based on the provided context"
)

# Initialize message log
message_log = [{"role": "ai", "content": "Hi! I'm DeepSeek. How can I help you today?"}]

def build_prompt_chain():
    prompt_sequence = [system_prompt]
    for msg in message_log:
        if msg["role"] == "user":
            prompt_sequence.append(HumanMessagePromptTemplate.from_template(msg["content"]))
        elif msg["role"] == "ai":
            prompt_sequence.append(AIMessagePromptTemplate.from_template(msg["content"]))
    print("promt sequence ----------------------------------------------->>>>.", "/n", prompt_sequence)
    print("end ---------------------------------------------------------->>>>")
    return ChatPromptTemplate.from_messages(prompt_sequence)

def generate_ai_response(prompt_chain):
    processing_pipeline = prompt_chain | llm | StrOutputParser()
    return processing_pipeline.invoke({})

def chat():
    print("DeepSeek: Hi! I'm DeepSeek. How can I help you code today? 💻")
    while True:
        user_message = input("You: ")
        if user_message.lower() in ["exit", "quit", "bye"]:
            print("DeepSeek: Goodbye! Happy coding! 🚀")
            break
        
        message_log.append({"role": "user", "content": user_message})
        
        # Generate AI response
        prompt_chain = build_prompt_chain()
        ai_response = generate_ai_response(prompt_chain)
        
        print(f"DeepSeek: {ai_response}")
        message_log.append({"role": "ai", "content": ai_response})

if __name__ == "__main__":
    chat()
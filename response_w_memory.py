from langchain.prompts.prompt import PromptTemplate
from langchain.chains import ConversationChain
from langchain_mistralai import ChatMistralAI
from langchain.memory import ConversationBufferMemory
import os
from dotenv import load_dotenv
load_dotenv()

mistral_api_key  = os.environ["MISTRAL_API_KEY"]
# os.environ["MISTRAL_API_KEY"] = "vJ6LuLUeYqm1Uedzci7A2Fgh7tHnbS7p"
llm = ChatMistralAI(model="mistral-large-latest")

template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.

Current conversation:
{history}
Human: {input}
AI Assistant:
"""

PROMPT = PromptTemplate(input_variables=["history", "input"], template=template)
conversation = ConversationChain(
    prompt=PROMPT,
    llm=llm,
    verbose=True,
    memory=ConversationBufferMemory(ai_prefix="AI Assistant"),
)
# history = "Human: whats ai?\nAI Assistant: Hello there! AI stands for Artificial Intelligence. It's a broad field of computer science dedicated to creating machines and software that can exhibit human-like intelligence, able to perform tasks that typically require human cognition. These tasks include learning, reasoning, problem-solving, perception, and language understanding.\n\nThere are different types of AI, ranging from narrow or weak AI, which is designed to do a narrow task (like facial recognition or internet searches), to general or strong AI, which understands, learns, and applies knowledge across various tasks at a level equal to or beyond human capabilities. There's also superintelligent AI, which is still a theoretical concept that surpasses human intelligence in every economically valuable work.\n\nSome examples of AI in use today include virtual assistants like me, recommendation algorithms on streaming services, self-driving cars, and fraud detection systems. It's a fascinating field with lots of growth and innovation! Do you have any specific questions about AI? I'm here to help!\nHuman: my name is bob?\nAI Assistant: Nice to meet you, Bob! It's great to have a name to call you by. How are you doing today? Is there something specific you would like to talk about or learn about? I'm here to help and chat about a wide range of topics. If you have more questions about AI or anything else, feel free to ask!"

def respond(query,history):
    response = conversation.invoke({"input": query,"history":history})
    # print(response['response'])
    return response['response']


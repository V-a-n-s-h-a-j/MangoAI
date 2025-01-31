from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import START, MessagesState, StateGraph
import os


# def setup_llm():

os.environ["MISTRAL_API_KEY"] = "vJ6LuLUeYqm1Uedzci7A2Fgh7tHnbS7p"
model = ChatMistralAI(model="mistral-large-latest")

workflow = StateGraph(state_schema=MessagesState)


# Define the function that calls the model
def call_model(state: MessagesState):
    system_prompt = (
        "You are a helpful assistant. "
        "Answer all questions to the best of your ability."
    )
    messages = [SystemMessage(content=system_prompt)] + state["messages"]
    response = model.invoke(messages)
    return {"messages": response}


# Define the node and edge
workflow.add_node("model", call_model)
workflow.add_edge(START, "model")

# Add simple in-memory checkpointer
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
    # return app

def generate_response(input_query, thread_id):
    # app = setup()
    config = {"configurable": {"thread_id": thread_id}}
    query = input_query

    input_messages = [HumanMessage(query)]
    
    output = app.invoke({"messages": input_messages}, config)
    return  output["messages"][-1].content

# if __name__ == "__main__":
#     print(generate_response("2+2?", '1'))
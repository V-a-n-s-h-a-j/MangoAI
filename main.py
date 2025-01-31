from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
from response import generate_response
from response_w_memory import respond
import datetime
import os
from dotenv import load_dotenv
load_dotenv()


app = FastAPI()

from pymongo import MongoClient

app = FastAPI()

# Connect to MongoDB
conn_str = os.getenv("MONGO_URI")
client = MongoClient(conn_str)
try:
    client.server_info()  # Checks connection
    print("Connected successfully!")
except Exception as e:
    print("Connection failed:", e)
db = client["MangoAI"]
collection = db["ChatHistories"]


# API to retrieve chat messages by thread_id
@app.get("/get-chat-history/{thread_id}/")
def get_chat_history(thread_id: str):
    chat_data = collection.find_one({"_id": ObjectId(thread_id)})
    
    if chat_data:
        return {"thread_id": thread_id, "history": chat_data["history"]}
    
    return {"error": "Chat not found"}


# Define request schema
class TextQuery(BaseModel):
    query: str
    thread_id: str

# def generate_response(input_data):
#     pass

# Define the POST endpoint
@app.post("/query_response/")
async def query_response(input_data: TextQuery):
    # Echo back the input query
    
    query = input_data.query
    thread_id = input_data.thread_id

    chat_data = collection.find_one({"_id": ObjectId(thread_id)})
    history = chat_data['history']
    response = respond(query,history)
    updated_history = history + "\nHuman: " + query + "\nAI Assistant: "+ response

    collection.update_one(
        {"_id": ObjectId(thread_id)},
        {"$set": {"history": updated_history}}
    )

    return {"response": response, "history": history, "updated_history": updated_history}



# Define Request Body Schema (No thread_id in input)
class ChatCreateRequest(BaseModel):
    uuid: str
    history: str =""

# API to create a new chat
@app.post("/create-chat/")
def create_chat(chat: ChatCreateRequest):
    # Create the chat object (MongoDB generates _id)
    chat_data = {
        "uuid": chat.uuid,
        "history": chat.history,
        # "created_at": datetime.datetime.now(),
        # "expires_at": datetime.utcnow() + timedelta(days=2)  # Chat expires in 2 days
    }
    # Insert into MongoDB
    result = collection.insert_one(chat_data)

    chat_data["_id"] = str(result.inserted_id)

    return {"message": "Chat created successfully!", "chat_data": chat_data}


#    uvicorn main:app --reload

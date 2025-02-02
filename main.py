from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
# from response import generate_response
from response_w_prompt_chain import respond
import datetime
import os
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Allow frontend URL
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, DELETE)
    allow_headers=["*"],  # Allow all headers
)


from pymongo import MongoClient

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

# Function to convert MongoDB ObjectId to string
def serialize_chat(chat):
    chat["_id"] = str(chat["_id"])  # Convert ObjectId to string
    return chat

@app.get("/get-user-chats/{uuid}/")
def get_all_chats(uuid: str):
    chat_data = collection.find({"uuid": uuid})
    chat_data = list(chat_data)
    chat_list = [serialize_chat(chat) for chat in chat_data]  # Convert MongoDB objects to JSON-serializable format
    
    return {"chats": chat_list}  # Return JSON response

# API to retrieve chat messages by thread_id
@app.get("/get-chat-history/{thread_id}/")
def get_chat_history(thread_id: str):
    chat_data = collection.find_one({"_id": ObjectId(thread_id)})
    
    if chat_data:
        return {"thread_id": thread_id, "chat_data": chat_data["history"]}

    return {"error": "Chat not found"}


# Define request schema
class TextQuery(BaseModel):
    query: str
    thread_id: str

@app.post("/query_response/")
async def query_response(input_data: TextQuery):

    query = input_data.query
    thread_id = input_data.thread_id
    
    #extract previous chat / [] for newly created chat
    chat_data = collection.find_one({"_id": ObjectId(thread_id)})
    print("retrieved chat data-------------------------------->","/n", chat_data)
    history = chat_data['history']
    print("end------------------------------------------------>")
    history.append({"role": "user", "content": query})

    response = respond(history)
    history.append({"role": "ai", "content": response})

    collection.update_one(
        {"_id": ObjectId(thread_id)},
        {"$set": {"history": history}}
    )

    return {"response": response, "history": history}



# Define Request Body Schema (No thread_id in input)
class ChatCreateRequest(BaseModel):
    uuid: str
    history: list =[{"role": "ai", "content": "Hi! I'm MistralAI. How can I help you today?"}]

# API to create a new chat
@app.post("/create-chat/")
def create_chat(chat: ChatCreateRequest):
    # Create the chat object (MongoDB generates _id)
    chat_data = {
        "uuid": chat.uuid,
        "history": chat.history,
        # "created_at": datetime.datetime.now(),
    }
    # Insert into MongoDB
    result = collection.insert_one(chat_data)

    chat_data["_id"] = str(result.inserted_id)

    return {"message": "Chat created successfully!", "chat_data": chat_data}

@app.delete ("/delete-chat/{thread_id}")
def delete_chat(thread_id: str):
    collection.delete_one({"_id": ObjectId(thread_id)})
    return{"message":"Chat successfully deleted", "thread_id":thread_id}


#    uvicorn main:app --reload

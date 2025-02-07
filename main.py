from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from bson import ObjectId
# from response import generate_response
from response_w_prompt_chain import respond
from response_w_prompt_chain import generate_chat_title
import datetime, timedelta
import bcrypt
import jwt
import uuid
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
users_collection = db["Users"]
collection = db["ChatHistories"]

# Hash password
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Verify password
def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

SECRET_KEY = "skdjflaisjfvbliequoskdnc"
ALGORITHM = "HS256"


def create_jwt_token(user_id: str):
    payload = {"user_id": user_id, "exp": datetime.utcnow() + timedelta(days=7)}
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


# User Schema
class UserSignup(BaseModel):
    name: str
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

@app.post("/signup/")
def signup(user: UserSignup):
    if users_collection.find_one({"email": user.email}):
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = hash_password(user.password)
    new_user = {"name": user.name, "email": user.email, "password": hashed_password}
    result = users_collection.insert_one(new_user)
    
    token = create_jwt_token(str(result.inserted_id))
    return {"message": "User created successfully", "token": token}

@app.post("/login/")
def login(user: UserLogin):
    existing_user = users_collection.find_one({"email": user.email})
    if not existing_user or not verify_password(user.password, existing_user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    token = create_jwt_token(str(existing_user["_id"]))
    return {"message": "Login successful", "token": token}


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

    if len(history) == 2 and chat_data.get("title", "Untitled Chat") == "Untitled Chat":
        chat_title = generate_chat_title(query)
        
        # Update chat title in MongoDB
        collection.update_one(
            {"_id": ObjectId(thread_id)},
            {"$set": {"title": chat_title}}
        )

    response = respond(history)
    history.append({"role": "ai", "content": response})

    collection.update_one(
        {"_id": ObjectId(thread_id)},
        {"$set": {"history": history}},
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
        "title" : "Untitled Chat",
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

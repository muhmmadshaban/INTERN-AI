from agent_team import chat
from agent_team import extract_text_from_pdf

from typing import Union,List
from uvicorn import run
from fastapi import FastAPI
from pydantic import BaseModel

class Request(BaseModel):
    message: Union[str, List[str]]

app = FastAPI(name="Agent Team")
@app.get("/")
def read_root():
    return {"Hello": "World"}
@app.post("/chat")
def chat_endpoint(request: Request):
    messages = request.message
    response = chat(messages)
    if isinstance(response, str):
        return {"response": response}
    elif isinstance(response, list):
        return {"response": response}
    if response is None:
        return {"response": "No response from agent."}
    elif not isinstance(response, str):
            response = str(response)
    return {"response": response}

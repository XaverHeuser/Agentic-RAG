from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .src.agent import Agent
from .src.config import Config
from .src.database import AgentStore


app = FastAPI()

# Allow Next.js frontend to talk to FastAPI backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000'],  # Next.js default port
    allow_methods=['*'],
    allow_headers=['*'],
)

config = Config()
store = AgentStore(config)
agent = Agent(config, search_func=store.search)


class ChatRequest(BaseModel):
    message: str


@app.post('/api/chat')
async def chat(request: ChatRequest):
    try:
        response_text = agent.ask(request.message)
        return {'answer': response_text}

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

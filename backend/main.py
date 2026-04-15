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

# Store agents by session_id to support multiple concurrent users
sessions: dict[str, Agent] = {}


class ChatRequest(BaseModel):
    message: str
    session_id: str = 'default'


@app.post('/api/chat')
async def chat(request: ChatRequest):
    try:
        # Get or create an agent instance for this specific session
        if request.session_id not in sessions:
            sessions[request.session_id] = Agent(config, search_func=store.search)

        current_agent = sessions[request.session_id]
        response_text = current_agent.ask(request.message)

        return {'answer': response_text}

    except Exception as err:
        raise HTTPException(status_code=500, detail=str(err)) from err

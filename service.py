from fastapi import Body, FastAPI
from aifori.agent import AIAgent
from aifori.core import AgentInfo
from pydantic import BaseModel, Field
from typing import Any

from aifori.memory import RawMemory

app = FastAPI()


class Response(BaseModel):
    code: int = Field(description="返回码,200为正常返回", default=200)
    msg: str = Field(description="返回消息", default="success")
    data: Any = Field(description="返回数据", default=None)

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "msg": "success",
            }
        }


def exception2resp(e: Exception) -> Response:
    resp = Response(code=500, msg="server internal error", data=str(e))
    return resp


@app.get("/health")
async def health():
    return Response(data=dict(status="ok"))


@app.post("/agent/create", tags=["agent"])
async def create_agent(agent_info: AgentInfo = Body(example=AgentInfo(
        name="Emohaa", desc="Emohaa是一款基于Hill助人理论的情感支持AI，拥有专业的心理咨询话术能力。能够和对方共情、安慰，并且记得对方说的所有话", role="assistant"))) -> Response:
    memory = RawMemory()
    assistant = AIAgent(agent_info=agent_info, memory=memory)
    assistant.save()
    return Response(data=assistant)


# @app.post("/session/create", tags=["session"])
# async def create_session(user_info: AgentInfo = Body(...),
#                          assistant_info: AgentInfo = Body(...)) -> Response:
#     session = Session(history=[], user_info=user_info, assistant_info=assistant_info)
#     session.save()
#     return Response(data=session.to_json())


# @app.post("/session/chat", tags=["session"])
# async def chat(session_id: str = Body(...),
#                message: str = Body(...)) -> Response:
#     session = get_session(session_id)
#     agent_info = session.assistant_info
#     memory = RawMemory(history=session.history)
#     assistant = AIAgent(agent_info=agent_info, memory=memory)
#     message = UserMessage(content=message)
#     resp_message = assistant.chat(message)
#     return Response(data=resp_message)

from functools import wraps
import itertools
import json
import shutil
from fastapi import Body, FastAPI, File, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from aifori.agent import AIAgent, HumanAgent
from aifori.session import SESSION_MANAGER
from aifori.config import *
from aifori.core import AssistantMessage, Message, UserMessage, Voice
from pydantic import BaseModel, Field
from typing import Any, List

import aifori.api as api
from loguru import logger
from aifori.tts import dump_voice
from snippets import load, add_callback2gen, log_function_info, set_logger
from hashlib import md5

set_logger(AIFORI_ENV, __name__, log_dir=os.path.join(LOG_HOME, "service"), show_process=True)
app = FastAPI(root_path="/api")
# app = FastAPI()


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
    resp = Response(code=500, msg=str(e), data=None)
    return resp


def try_wrapper(func):
    @wraps(func)
    async def wrapped(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.exception(e)
            return exception2resp(e)
    return wrapped


@app.get("/health", tags=["common"], description="检查服务是否正常")
async def health() -> Response:
    return Response(data=dict(status="ok"))


@app.post("/agent/create", tags=["agent"], description="创建一个Agent")
@try_wrapper
async def create_agent(
        id: str = Body(default=None, description="Agent的ID,唯一键，如果不传则自动生成", examples=["test_agent"]),
        name: str = Body(default=DEFAULT_AI_NAME, description="Agent的名字"),
        desc: str = Body(default=DEFAULT_AI_DESC, description="Agent的描述"),
        model: str = Body(default=DEFAULT_MODEL, description="Agent使用的模型"),
        voice_config: dict = Body(default=DEFAULT_VOICE_CONFIG, description="Agent的音色配置")) -> Response:
    assistant = api.create_assistant(id=id, name=name, desc=desc, model=model, exists_ok=False, do_save=True, voice_config=voice_config)
    return Response(data=assistant.get_config())


@app.post("/agent/get", tags=["agent"], description="获取一个Agent")
@try_wrapper
async def get_agent(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"], embed=True)) -> Response:
    assistant = api.get_assistant(id)
    return Response(data=assistant.get_config())


@app.post("/agent/delete", tags=["agent"], description="删除一个Agent")
@try_wrapper
async def delete_agent(id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"], embed=True)) -> Response:
    AIAgent.delete(id)
    return Response(data=dict(status="ok"))


@app.post("/user/create", tags=["user"], description="创建一个人类用户")
@try_wrapper
async def create_user(
        id: str = Body(default=None, description="User的ID,唯一键，如果不传则自动生成", examples=["test_user"]),
        name: str = Body(default=DEFAULT_USER_NAME, description="User的名字"),
        desc: str = Body(default=DEFAULT_USER_DESC, description="User的描述")) -> Response:
    user = api.create_user(id=id, name=name, desc=desc, exists_ok=False, do_save=True)
    return Response(data=user.get_config())


@app.post("/user/get", tags=["user"], description="获取一个人类用户")
@try_wrapper
async def get_user(id: str = Body(description="USER的ID,唯一键", examples=["test_user"], embed=True)) -> Response:
    user = api.get_user(id)
    return Response(data=user.get_config())


@app.post("/user/delete", tags=["user"], description="删除一个人类用户")
@try_wrapper
async def delete_user(id: str = Body(description="USER的ID,唯一键", examples=["test_user"], embed=True)) -> Response:
    HumanAgent.delete(id)
    return Response(data=dict(status="ok"))


@app.post("/agent/chat", tags=["agent"], description="和Agent进行对话, 批式")
@try_wrapper
@log_function_info(input_level="INFO", result_level=None)
async def chat_agent(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                     user_id: str = Body(description="用户的ID,唯一键", examples=["test_user"]),
                     session_id: str = Body(description="对话的ID,唯一键", examples=["test_session"]),
                     message: str = Body(description="用户发送的消息", examples=["你好呀，你叫什么名字？"]),
                     do_remember: bool = Body(default=True, description="Agent是否记忆这轮对话"),
                     recall_memory: bool = Body(default=False, description="是否唤起长期记忆")) -> Response:
    assistant = api.get_assistant(agent_id)
    user_message = UserMessage(content=message, user_id=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=False, temperature=0, recall_memory=recall_memory)

    if do_remember:
        SESSION_MANAGER.add_message(user_message, to_id=agent_id, to_role="assistant", session_id=session_id)
        SESSION_MANAGER.add_message(assistant_message, to_id=user_id, to_role="user", session_id=session_id)
    logger.info(f"agent {agent_id} reply {assistant_message} for user message:{user_message}")

    return Response(data=assistant_message)


@app.post("/agent/chat_stream", tags=["agent"], description="和Agent进行对话, 流式")
@try_wrapper
async def chat_agent_stream(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                            user_id: str = Body(description="用户的ID,唯一键", examples=["test_user"]),
                            session_id: str = Body(default=None, description="对话的ID,唯一键"),
                            message: str = Body(description="用户发送的消息", examples=["你好呀，你叫什么名字？"]),
                            do_remember: bool = Body(default=True, description="Agent是否记忆这轮对话"),
                            recall_memory: bool = Body(default=False, description="是否唤起长期记忆")) -> StreamingResponse:
    assistant = api.get_assistant(agent_id)
    user_message = UserMessage(content=message, user_id=user_id)
    assistant_message = assistant.chat(message=user_message,  stream=True, recall_memory=recall_memory, temperature=0)

    if do_remember:
        SESSION_MANAGER.add_message(user_message, to_id=agent_id, to_role="assistant", session_id=session_id)

    def stream2message(items):
        content = "".join(items)
        message = AssistantMessage(content=content, user_id=agent_id)
        logger.info(f"agent {agent_id} reply {message} for user message:{user_message}")
        if do_remember:
            SESSION_MANAGER.add_message(message, to_id=user_id, to_role="user", session_id=session_id)

    content_stream = add_callback2gen(items=assistant_message.content, callback=stream2message)
    content_stream = itertools.chain((json.dumps(dict(assistant_id=agent_id)) + "\n"),
                                     (json.dumps(dict(chunk=item), ensure_ascii=False) + "\n" for item in content_stream))

    return StreamingResponse(content_stream, media_type="application/x-ndjson")


@app.post("/agent/speak_stream", tags=["agent"], description="让Agent朗读文字, 流式返回")
@try_wrapper
async def speak_agent_stream(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                             message: str = Body(description="需要说出来的文字内容", examples=["你好呀，我的名字叫Aifori"]),
                             voice_config: dict = Body(default=DEFAULT_VOICE_CONFIG, description="tts的配置")) -> StreamingResponse:
    logger.info(f"agent {agent_id} speak {message} with {voice_config=}")
    assistant = api.get_assistant(agent_id)
    if not assistant:
        raise Exception(f"agent:{agent_id} not found")
    voice: Voice = assistant.speak(message=message, stream=True, **voice_config)
    voice_path = os.path.join(VOICE_DIR, "tmp_speak", f"{agent_id}_{md5(''.encode()).hexdigest()}.mp3")
    voice.content = add_callback2gen(items=voice.content, callback=dump_voice, path=voice_path)
    logger.info(f"dump agent {agent_id} speak {message} to {voice_path}")
    return StreamingResponse(voice.content, media_type="audio/mp3")


@app.post("/session/clear", tags=["session"], description="清空session的历史")
async def clear_session(session_id: str = Body(description="session_id", examples=["test_session"], embed=True)) -> Response:
    logger.info(f"clear session {session_id}")
    SESSION_MANAGER.clear_session(session_id)
    return Response(data=dict(status="ok"))


@app.post("/message/list", tags=["message"], description="列出最近的对话消息", summary="列出最近的对话消息")
async def list_messages(session_id: str = Body(description="按照session_id过滤message，不传则不按照session_id过滤", examples=["test_session"], default=None),
                        agent_id: str = Body(description="按照agent_id过滤message（所有agent_id发出或者收到的message），不传则不按照agent_id过滤",
                                             examples=["test_agent"], default=None),
                        limit: int = Body(default=10, description="限制返回的条数", examples=[10])) -> Response:
    logger.info(f"list messages, session_id:{session_id}, agent_id:{agent_id}, limit:{limit}")
    messages: List[Message] = SESSION_MANAGER.get_history(_from=agent_id, to=agent_id, operator="or", session_id=session_id, limit=limit)
    return Response(data=messages)


@app.post("/rule/update", tags=["rule"], description="更新规则", summary="更新规则")
@try_wrapper
async def update_rule(upload_file: UploadFile = File(description="更新文件, 支持后缀名jsonl")) -> Response:
    logger.info("update rule file with upload file")
    with open(DEFAULT_RULE_PATH, "wb") as f:
        shutil.copyfileobj(upload_file.file, f)
    return Response(data=f"update rule file:{upload_file.filename} success!")


@app.post("/rule/list", tags=["rule"], description="列出规则", summary="列出规则")
@try_wrapper
async def update_rule() -> Response:
    rules = load(DEFAULT_RULE_PATH)
    return Response(data=rules)


@app.get("/")
async def get():
    with open("assets/test_speak.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(html)


@app.post("/agent/speak_stream", tags=["agent"], description="让Agent朗读文字, 流式返回")
@try_wrapper
async def speak_agent_stream(agent_id: str = Body(description="Agent的ID,唯一键", examples=["test_agent"]),
                             message: str = Body(description="需要说出来的文字内容", examples=["你好呀，我的名字叫Aifori"]),
                             voice_config: dict = Body(default=DEFAULT_VOICE_CONFIG, description="tts的配置")) -> StreamingResponse:
    logger.info(f"agent {agent_id} speak {message} with {voice_config=}")
    assistant = api.get_assistant(agent_id)
    if not assistant:
        raise Exception(f"agent:{agent_id} not found")
    voice: Voice = assistant.speak(message=message, stream=True, **voice_config)
    voice_path = os.path.join(VOICE_DIR, "tmp_speak", f"{agent_id}_{md5(''.encode()).hexdigest()}.mp3")
    voice.content = add_callback2gen(items=voice.content, callback=dump_voice, path=voice_path)
    logger.info(f"dump agent {agent_id} speak {message} to {voice_path}")
    return StreamingResponse(voice.content, media_type="audio/mp3")


@app.websocket("/agent/speak_stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        data = await websocket.receive_text()
        logger.info(f"{data=}")
        data = json.loads(data)
        agent_id = data["agent_id"]
        message = data["message"]
        voice_config = data["voice_config"]

        assistant = api.get_assistant(agent_id)
        if not assistant:
            raise Exception(f"agent:{agent_id} not found")
        voice: Voice = assistant.speak(message=message, stream=True, **voice_config)
        voice_path = os.path.join(VOICE_DIR, "tmp_speak", f"{agent_id}_{md5(''.encode()).hexdigest()}.mp3")
        voice.content = add_callback2gen(items=voice.content, callback=dump_voice, path=voice_path)
        logger.info(f"dump agent {agent_id} speak {message} to {voice_path}")
        for chunk in voice.content:
            await websocket.send_bytes(chunk)
    except Exception as e:
        logger.info(f"Connection closed: {e}")
    finally:
        await websocket.close()

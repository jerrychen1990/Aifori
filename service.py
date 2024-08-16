from functools import wraps
import json
import shutil
from fastapi import Body, FastAPI, File, UploadFile, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from aifori.session import SESSION_MANAGER
from aifori.config import *
from aifori.core import AssistantMessage, ChatSpeakRequest, Message, ChatRequest, SpeakRequest
from pydantic import BaseModel, Field
from typing import Any, List

import aifori.api as api
from loguru import logger
from aifori.util import voice2api_stream
from liteai.core import Voice
from snippets import load, set_logger
from snippets.utils import jdumps

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


@app.post("/assistant/create", tags=["assistant"], description="创建一个assistant")
@try_wrapper
async def create_assistant(
        id: str = Body(default=None, description="assistant的ID,唯一键，如果不传则自动生成", examples=["test_assistant"]),
        name: str = Body(default=DEFAULT_AI_NAME, description="assistant的名字"),
        desc: str = Body(default=DEFAULT_AI_DESC, description="assistant的描述"),
        model: str = Body(default=DEFAULT_MODEL, description="assistant使用的模型"),
        voice_config: dict = Body(default=DEFAULT_VOICE_CONFIG, description="assistant的音色配置")) -> Response:
    assistant = api.create_assistant(id=id, name=name, desc=desc, model=model, exists_ok=False, do_save=True, voice_config=voice_config)
    return Response(data=assistant.get_config())


@app.post("/assistant/get", tags=["assistant"], description="获取一个assistant")
@try_wrapper
async def get_assistant(id: str = Body(description="assistant的ID,唯一键", examples=["test_assistant"], embed=True)) -> Response:
    assistant = api.get_assistant(id)
    return Response(data=assistant.get_config())


@app.post("/assistant/delete", tags=["assistant"], description="删除一个assistant")
@try_wrapper
async def delete_assistant(id: str = Body(description="assistant的ID,唯一键", examples=["test_assistant"], embed=True)) -> Response:
    api.delete_assistant(id=id)
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
    api.delete_user(id=id)
    return Response(data=dict(status="ok"))


@app.post("/assistant/chat", tags=["assistant"], description="和assistant进行对话, 批式")
@try_wrapper
async def chat_assistant(req: ChatRequest = Body(description="请求体")) -> Response:
    message: AssistantMessage = api.chat_assistant(req, stream=False)
    return Response(data=message)


@app.post("/assistant/chat_stream", tags=["assistant"], description="和Assistant进行对话,可以返回语音,sse流式")
@try_wrapper
async def chat_assistant_stream(req: ChatRequest = Body(description="请求体")) -> StreamingResponse:
    message: AssistantMessage = api.chat_assistant(req, stream=True)
    content_stream = (jdumps(dict(text_chunk=chunk), indent=None) + "\n" for chunk in message.content)
    return StreamingResponse(content_stream, media_type="application/x-ndjson")


@app.post("/assistant/speak_stream", tags=["assistant"], description="assistant返回文本对应的语音,sse流式")
@try_wrapper
async def speak_assistant_stream(req: SpeakRequest = Body(description="请求体")) -> StreamingResponse:
    req.voice_path = os.path.join(VOICE_DIR, req.voice_path) if req.voice_path else None
    voice: Voice = api.speak_assistant(req, stream=True)
    content_stream = (jdumps(dict(voice_chunk=chunk), indent=None) + "\n" for chunk in voice.byte_stream)
    return StreamingResponse(content_stream, media_type="application/x-ndjson")


@app.websocket("/assistant/speak_stream")
async def ws_speak_assistant_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        req = await websocket.receive_text()
        logger.debug(f"websocket {req=}")
        req = SpeakRequest.model_validate(json.loads(req))
        voice: Voice = api.speak_assistant(req, stream=True)
        for chunk in voice.byte_stream:
            b_chunk = jdumps(dict(voice_chunk=chunk), indent=None).encode("utf-8")
            await websocket.send_bytes(b_chunk)
    except Exception as e:
        logger.info(f"Connection closed: {e}")
    finally:
        await websocket.close()


@app.post("/assistant/chat_speak_stream", tags=["assistant"], description="assistant返回文本以及对应的语音,sse流式")
@try_wrapper
async def chat_speak_assistant_stream(req: ChatSpeakRequest = Body(description="请求体")) -> StreamingResponse:
    req.voice_path = os.path.join(VOICE_DIR, req.voice_path) if req.voice_path else None
    dict_stream = api.chat_speak_assistant(req)
    content_stream = (jdumps(chunk, indent=None) + "\n" for chunk in dict_stream)
    return StreamingResponse(content_stream, media_type="application/x-ndjson")


@app.websocket("/assistant/chat_speak_stream")
async def ws_chat_speak_assistant_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        req = await websocket.receive_text()
        logger.debug(f"websocket {req=}")
        req = ChatSpeakRequest.model_validate(json.loads(req))
        dict_stream = api.chat_speak_assistant(req, stream=True)
        for chunk in dict_stream:
            b_chunk = jdumps(chunk, indent=None).encode("utf-8")
            await websocket.send_bytes(b_chunk)
    except Exception as e:
        logger.info(f"Connection closed: {e}")
    finally:
        await websocket.close()


@app.post("/session/clear", tags=["session"], description="清空session的历史")
async def clear_session(session_id: str = Body(description="session_id", examples=["test_session"], embed=True)) -> Response:
    logger.info(f"clear session {session_id}")
    SESSION_MANAGER.clear_session(session_id)
    return Response(data=dict(status="ok"))


@app.post("/message/list", tags=["message"], description="列出最近的对话消息", summary="列出最近的对话消息")
async def list_messages(session_id: str = Body(description="按照session_id过滤message，不传则不按照session_id过滤", examples=["test_session"], default=None),
                        assistant_id: str = Body(description="按照assistant_id过滤message（所有assistant_id发出或者收到的message），不传则不按照assistant_id过滤",
                                                 examples=["test_assistant"], default=None),
                        limit: int = Body(default=10, description="限制返回的条数", examples=[10])) -> Response:
    logger.info(f"list messages, session_id:{session_id}, assistant_id:{assistant_id}, limit:{limit}")
    messages: List[Message] = SESSION_MANAGER.get_history(_from=assistant_id, to=assistant_id, operator="or", session_id=session_id, limit=limit)
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
async def list_rule() -> Response:
    rules = load(DEFAULT_RULE_PATH)
    return Response(data=rules)


@app.get("/index")
async def get():
    with open("assets/test_speak.html", "r", encoding="utf-8") as f:
        html = f.read()
    return HTMLResponse(html)


@app.post("/assistant/play_music_stream", tags=["music"], description="播放音乐")
async def play_music_stream(user_id: str = Body(description="user_id", examples=["test_user"], embed=True),
                            music_desc: str = Body(description="音乐描述", examples=["dnll"], embed=True)) -> StreamingResponse:
    voice = api.play_music(user_id=user_id, music_desc=music_desc)
    chunk_stream = voice2api_stream(voice)
    chunk_stream = (jdumps(chunk, indent=None) + "\n" for chunk in chunk_stream)
    return StreamingResponse(chunk_stream, media_type="application/x-ndjson")


@app.websocket("/assistant/play_music_stream")
async def ws_play_music_stream(websocket: WebSocket):
    await websocket.accept()
    try:
        req = await websocket.receive_text()
        req = json.loads(req)
        logger.debug(f"websocket {req=}")
        voice = api.play_music(**req)
        # chunk_stream = voice2api_stream(voice)
        for chunk in voice.byte_stream:
            logger.debug(f"send chunk, with size {len(chunk)}, {type(chunk)=}, {chunk[:10]=}")
            b_chunk = chunk
            # b_chunk = jdumps(chunk, indent=None).encode("utf-8")
            await websocket.send_bytes(b_chunk)
    except Exception as e:
        logger.exception(e)
        # logger.info(f"Connection closed: {e}")
    finally:
        await websocket.close()

from fastapi import Body, FastAPI

app = FastAPI()


@app.get("/health")
async def health():
    return {"status": "ok"}


async def chat(session_id: str = Body(...),
               message: str = Body(...)):

    return

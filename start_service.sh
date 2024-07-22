param=$@
uvicorn service:app --host 0.0.0.0 $param
reload=${1:-false}

cmd='uvicorn service:app --host 0.0.0.0 --ssl-keyfile=key.pem --ssl-certfile=cert.pem --port 9001'
if [ "$reload" = true ]; then
    cmd="$cmd --reload"
fi

echo "Running command: $cmd"
eval "$cmd"
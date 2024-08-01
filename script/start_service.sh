reload=${1:-false}

cmd='uvicorn service:app --host 0.0.0.0 --port 9001'
if [ "$reload" = true ]; then
    cmd="$cmd --reload"
fi

echo "Running command: $cmd"
eval "$cmd"
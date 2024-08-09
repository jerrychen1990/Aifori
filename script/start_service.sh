param=${@:='--port 9001'}

cmd='uvicorn service:app --host 0.0.0.0 '$param 

echo "Running command: $cmd"
eval "$cmd"
reload=$@

cmd='uvicorn service:app --host 0.0.0.0 --port 9001 '$reload 

echo "Running command: $cmd"
eval "$cmd"
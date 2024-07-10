port=${1:-80}
pelican --listen --port $port --bind 0.0.0.0 --output web/output --verbose --autoreload
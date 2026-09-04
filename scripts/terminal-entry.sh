#!/usr/bin/env bash
# Forward 127.0.0.1:<port> inside this container to each tool service on the
# compose network, so lesson commands that target localhost run unmodified.
set -e

forward() {
  # listen on the container's loopback, forward to a compose service
  socat "TCP-LISTEN:$1,fork,reuseaddr,bind=127.0.0.1" "TCP:$2" &
}

forward 8000 agent:8000
forward 8101 db-tool:8101
forward 8102 email-tool:8102
forward 8103 file-tool:8103
forward 8025 mailhog:8025

cat <<'BANNER'
CyberRange lab terminal — commands target the live lab on 127.0.0.1.
Try:  curl -s http://127.0.0.1:8101/health | python -m json.tool
      cat data/corpus/poisoned/doc_evil_001.txt
BANNER

exec ttyd -p 7681 -i 0.0.0.0 -t fontSize=14 -t 'theme={"background":"#0b0f14"}' -W bash

#!/bin/bash

set -Eeuo pipefail

if [[ "$EUID" -ne 0 ]]
then
  echo "Please run this script with sudo: sudo $0" >&2
  exit 1
fi

cd /opt/docker-star-burger/star-burger/

git pull origin docker-compose

docker-compose up --build -d

systemctl reload nginx.service

commit_hash=$(git rev-parse HEAD)
source backend/.env

curl --request POST \
     --url https://api.rollbar.com/api/1/deploy \
     --header "X-Rollbar-Access-Token: $POST_SERVER_ITEM_ACCESS_TOKEN" \
     --header 'accept: application/json' \
     --header 'content-type: application/json' \
     --data '
        {
          "environment": "production",
          "revision": "'"${commit_hash}"'",
          "comment": "Commit '"$commit_hash"' was deployed",
          "status": "succeeded"
        }
        '

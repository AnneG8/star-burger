#!/bin/bash

set -Eeuo pipefail

if [[ "$EUID" -ne 0 ]]
then
  echo "Please run this script with sudo: sudo $0" >&2
  exit 1
fi

cd /opt/star-burger/

git pull origin master

./venv/bin/pip install -r requirements.txt
npm ci

./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

./venv/bin/python3.10 manage.py collectstatic --noinput
./venv/bin/python3.10 manage.py migrate --noinput

systemctl daemon-reload
systemctl restart star-burger-django.service
systemctl reload nginx

commit_hash=$(git rev-parse HEAD)
source .env

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




#!/bin/bash

echo "Running."
ls /scripts

sudo -u vanessa /bin/bash /scripts/infinite-restart.sh "cd ~/web; npm install && npm run start-prod" &

wait

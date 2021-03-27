#!/bin/bash

echo "Running."
ls /scripts

sudo -u vanessa /bin/bash /scripts/infinite-restart.sh "cd ~/web; npm install && npm run start-prod" &
sudo -u vanessa /bin/bash /scripts/infinite-restart.sh "cd ~/discord-bot; python3 Gloomy3.py" &

wait

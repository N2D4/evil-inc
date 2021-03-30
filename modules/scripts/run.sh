#!/bin/bash

echo "Running."

sudo -u vanessa /bin/bash /scripts/infinite-restart.sh "cd ~/web; npm install && npm run start-prod" &
sudo -u vanessa /bin/bash /scripts/infinite-restart.sh "cd ~/discord-bot; python3 Gloomy3.py" &
/bin/bash /scripts/infinite-restart.sh "cd /home/norm/minecraft-server && java -Xms512M -Xmx512M -XX:+UseG1GC -jar spigot-1.16.5.jar nogui" &

wait

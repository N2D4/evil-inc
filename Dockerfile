FROM ubuntu:20.04

RUN apt-get update
RUN apt-get install -y sudo curl python3 python3-pip make

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update
RUN apt-get install -y nodejs

RUN useradd -ms /bin/bash vanessa
RUN chmod 700 /home/vanessa
RUN useradd -ms /bin/bash norm
RUN chmod 700 /home/norm
RUN useradd -ms /bin/bash heinz
RUN chmod 700 /home/heinz

COPY --chown=heinz:heinz modules/website /home/heinz

COPY --chown=vanessa:vanessa modules/website /home/vanessa/web

COPY --chown=vanessa:vanessa modules/discordbot /home/vanessa/discord-bot
RUN python3 -m pip install discord.py

WORKDIR /
COPY modules/scripts /scripts
CMD ["bash", "/scripts/run.sh"]

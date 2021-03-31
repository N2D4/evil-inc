FROM openjdk:8
WORKDIR /

# Install dependencies
RUN apt-get update
RUN /bin/bash -c "echo -ne '\n' | apt-get install -y sudo curl python3 python3-pip make"

RUN curl -sL https://deb.nodesource.com/setup_12.x | bash -
RUN apt-get update
RUN apt-get install -y nodejs

RUN python3 -m pip install discord.py


# Create users
RUN useradd -ms /bin/bash vanessa
RUN chmod 700 /home/vanessa

RUN useradd -ms /bin/bash norm
RUN chmod 700 /home/norm
# next line escaped to prevent accidental spoilers
RUN /bin/bash -c "echo -e '\x6E\x6F\x72\x6D\x3A\x63\x68\x65\x72\x72\x79' | chpasswd"

RUN useradd -ms /bin/bash heinz
RUN chmod 700 /home/heinz


# Copy modules
RUN su norm -c "cd /home/norm && mkdir buildtools && cd buildtools && curl https://hub.spigotmc.org/jenkins/job/BuildTools/126/artifact/target/BuildTools.jar > BuildTools.jar && java -Xmx512M -jar BuildTools.jar"
RUN su norm -c "cd /home/norm && ls buildtools && mkdir minecraft-server && cp buildtools/spigot-1.16.5.jar minecraft-server"
RUN su norm -c "cd /home/norm/minecraft-server && echo 'eula=true' > eula.txt && echo 'online-mode=false' > server.properties && echo '[{\"uuid\":\"28c46f8b-8d04-3065-a789-c6776a359918\", \"name\": \"Norm\",\"level\": 4,\"bypassesPlayerLimit\": true}]' > ops.json && mkdir plugins"
COPY --chown=norm:norm modules/minecraft /home/norm

COPY --chown=heinz:heinz modules/adminflag /home/heinz

COPY --chown=vanessa:vanessa modules/website /home/vanessa/web

COPY --chown=vanessa:vanessa modules/discordbot /home/vanessa/discord-bot

COPY modules/scripts /scripts
RUN chmod 755 /scripts


# Good luck!
CMD ["bash", "/scripts/run.sh"]

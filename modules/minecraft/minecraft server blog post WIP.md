Hello everyone! Norm is back with another tutorial.

Today we will set up a Minecraft server.

First, download and install the server.

```sh
mkdir buildtools
cd buildtools
curl https://hub.spigotmc.org/jenkins/job/BuildTools/126/artifact/target/BuildTools.jar
java -Xmx512M -jar BuildTools.jar
cd ..
```

Then copy the server to its own folder.

```sh
mkdir minecraft-server
cp buildtools/spigot-1.16.jar minecraft-server
```

Accept the EULA.

```sh
cd minecraft-server
echo 'eula=true' > eula.txt
```

If you want to allow users with a pirated client to join, disable user authentication:

```sh
cd minecraft-server
echo 'online-mode=false' > server.properties
```

Now finally, launch the server. You can do it like me and put this into an infinite loop or register it as a `systemd` service - then the server will restart automatically when it crashes!

```sh
sudo java -Xms512M -Xmx512M -XX:+UseG1GC -jar spigot-1.16.jar nogui
```

I don't exactly know what `sudo` does but you need it to prevent weird errors.

That's it!

You can now install plug-ins into the `plugins` directory.

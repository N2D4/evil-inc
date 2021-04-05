# evil-inc
Evil Incorporated is the world-leading manufacturer for both Evil and Incorporated.

## Set-Up
NOTE: The Dockerfile (and any other file in this directory, including this README) may contain spoilers.

First, make sure Docker is installed and the Docker daemon is running.

Start by navigating to this folder and running the Docker image using the following command:
```sh
docker build -t evil-inc . && docker run -p 8067:8067 -p 25565:25565 evil-inc
```
Then, navigate to `https://localhost:8067`.

## The Solution
- Open website
- Open Blog page, see a post by Norm promoting password reuse, and Vanessa mentioning she's the webmaster on a post about SQL injection (expert mode: no explicit mentions of SQL injection)
- Find commented out "Admin" link on main page in source code, linking to `/admin` (expert mode: no such link, link can be found in sitemap.xml and robots.txt)
- `/admin` requires a log-in
  - Go to Register page, where trying to register throws an SQL error (permission; db write not allowed)
  - SQL injection on the database to skip database authentication and log-in as an admin directly (expert mode: use the fact that hashing happens on the client and an SQL read injection to find Vanessa's hashed password)
- Find the server source code on the admin panel (expert mode: minified + obfuscated using JSF***)
- Find in the source code that the `/assets` folder is served, which is vulnerable to a path traversal attack (normal mode: query parameters, expert mode: URL)
- Use it to take a look at a discord bot source code in the same user folder
- Discord bot has an undocumented `!math` command which runs Python's `eval` (expert mode: no globals in `eval` call)
  - Notice that it's accessible only to admins, where admins are a list of users configured in a config file
  - Config file is also used to store quotes by the `!quote` command, which doesn't properly escape quotes so it can be used to overwrite the admins with any other list of Discord users
- Use the shitty hash algorithm to figure that Norm's password in the web database is fairly short, short enough to be brute-forced (expert mode: it's an SHA256 hash with substitution cipher this time, crack the substitution cipher and use a rainbow table)
- Use `eval` to open a shell and log-in to the user `norm` using Norm's password found in the database (he used the same one)
- Find that Norm has a Minecraft Spigot server running, and a text file tutorial on how to set up a Spigot server advocating running the server as `root`
  - Create a Spigot plug-in to remotely open a shell and install it on the server using Norm's account
  - Notice you need to restart the server first, which you can do by logging into the server as an OP from ops.json (as it is set to offline mode, you can choose any username with a cracked launcher)
- The file at `/home/heinz/SECRET_FLAG.txt` says `CURSE YOU, PERRY THE PLATYPUS!` - that's the flag!

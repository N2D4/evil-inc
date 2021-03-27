# evil-inc
Evil Incorporated is the world-leading manufacturer for both Evil and Incorporated.

## Set-Up
Start by running the Docker image using the following command:
```sh
cd evil-inc
docker build -t evil-inc . && docker run -p 8067:8067 evil-inc
```
Then, navigate to `https://localhost:8067`.

## The Solution
- Open website
- Open Blog page, see a post by Norm promoting password reuse, and Vanessa mentioning she's the webmaster on a post about SQL injection (expert mode: no explicit mentions of SQL injection)
- Find commented out "Admin" link on main page in source code, linking to `/admin` (expert mode: no such link, link can be found in sitemap.xml and robots.txt)
- `/admin` requires a log-in
  - Go to Register page, where trying to register throws an SQL error (permission; db write not allowed)
  - SQL injection on the database to find Vanessa and Norm's passwords
  - Find Vannessa's "hashed" password in the database (which is fairly long and complex), see that "hashing" is done client-side using a substitution cipher (expert mode: first sha256 without salt, then substitution cipher, but still client-side)
  - Log-in into the admin panel by disabling hashing on the client and instead submitting Vanessa's hashed password directly (Norm's shows access denied)
- Find the server source code on the admin panel (expert mode: minified + obfuscated using JSF***)
- Figure out that the reason DB write was denied is because write permissions were accidentally enabled on the table DISCORD_BOT instead of WEBSITE
- Find in the source code that the `/assets` folder is served, which is vulnerable to a path traversal attack (normal mode: query parameters, expert mode: URL)
- Use it to take a look at a discord bot source code in the same user folder
- Discord bot fails to start up trying to read a token, but it takes its token from the DISCORD_BOT table in the database so replace that using SQL injection with a valid Discord bot token
- Discord bot has an undocumented `bot!math` command which runs Python's `eval` (expert mode: no globals in `eval` call)
  - Notice that it's accessible only to admins, where admins are a list of users configured in a config file
  - Config file is also used to store quotes by the `bot!quote` command, which doesn't properly escape quotes so it can be used to overwrite the admins with any other list of Discord users
- Use the shitty hash algorithm to figure that Norm's password in the web database is fairly short, short enough to be brute-forced (expert mode: it's an SHA256 hash this time, crack the substitution cipher and use a rainbow table)
- Use `eval` to open a shell and log-in to the user `norm` using Norm's password found in the database (he used the same one)
- Find that Norm has a Minecraft Spigot server running, and a text file tutorial on how to set up a Spigot server advocating running the server as `root` and mentioning not to install "untrusted plug-ins" as they could be malicious
  - Create a Spigot plug-in to remotely open a shell and install it on the server using Norm's account
- The file at `/home/heinz/SECRET_FLAG.txt` says `CURSE YOU, PERRY THE PLATYPUS!` - that's the flag!

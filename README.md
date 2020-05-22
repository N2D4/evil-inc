# evil-inc
Evil Incorporated is the world-leading manufacturer for both Evil and Incorporated.

## The Solution
- Open website
- Open Blog page, see a post by Kyle promoting password reuse, and Vanessa mentioning she's the webmaster
- Find commented out "Admin" link on main page in source code, linking to `/admin`
- `/admin` requires a log-in
- Go to Register page, where trying to register throws an SQL error
- SQL injection on the database to find Vanessa and Kyle's passwords
- Find Vannessa's "hashed" password in the database (which is fairly long), see that "hashing" is done client-side using a substitution cipher
- Log into the admin panel by disabling hashing on the client and instead submitting the hashed password directly
- Find the server source code on the admin panel (minified + obfuscated using JSF***)
- Find in the source code that the `/assets` folder is served, which is vulnerable to a path traversal attack
- Use it to take a look at the Suppy2 source code, which has an undocumented `suppy 2 evaluate` command which runs Python's `eval`
- Use the shitty hash algorithm to figure that Kyle's password is fairly short, short enough to be brute-forced
- Use `eval` to open a shell and log-in to the user `kyle` using Kyle's password found in the database
- Find that Kyle has a Minecraft Spigot server running, and a text file tutorial on how to set up a Spigot server advocating running the server as `root` and mentioning not to install "untrusted plug-ins" as they could be malicious
- Create a Spigot plug-in which reads the file in `/home/admin/SECRET_FLAG.txt` and install it on the server using Kyle's account
- The file says `CURSE YOU, PERRY THE PLATYPUS!` - that's the flag!

require('core-js/stable');
require('regenerator-runtime/runtime');
const http = require('http');
const util = require('util');
const fs = require('fs');
const sqlite3 = require('sqlite3').verbose();
const db = new sqlite3.Database('db/website.db', sqlite3.OPEN_READONLY);

async function respondWithFile(res, filePath) {
    const file = await util.promisify(fs.readFile)(filePath);
    const fileType = filePath.endsWith('.html') ? 'text/html'
                    : filePath.endsWith('.css') ? 'text/css'
                    : filePath.endsWith('.txt') ? 'text/plain'
                    : filePath.endsWith('.js') ? 'text/javascript'
                    : 'application/octet-stream';
    res.writeHead(200, {'Content-Type': fileType});
    res.end(file);
}

async function checkToken(token, needsAdmin) {
    return (!needsAdmin || token.startsWith('vanessa:')) && await checkCredentials(...token.split(':'));
}

async function checkCredentials(username, hashedPassword) {
    const row = await util.promisify(db.get.bind(db))("SELECT hashedPassword FROM users WHERE name = '" + username + "'");
    return row && row.hashedPassword === hashedPassword;
}

async function respond(req, res) {
    const url = req.url;
    switch (url) {
        case '': case '/': {
            return await respondWithFile(res, 'src/client/index.html');
        }
        case '/about': {
            return await respondWithFile(res, 'src/client/about.html');
        }
        case '/blog': {
            return await respondWithFile(res, 'src/client/blog.html');
        }
        case '/admin': {
            const cookie = req.headers.cookie;
            if (cookie && await checkToken(cookie.split('=')[1], true)) {
                return await respondWithFile(res, 'src/client/admin.html');
            } else {
                return await respondWithFile(res, 'src/client/access-denied.html');
            }
        }
        case '/publish': {
            const cookie = req.headers.cookie;
            if (cookie && await checkToken(cookie.split('=')[1], true)) {
                return await respondWithFile(res, 'src/client/publish.html');
            } else {
                return await respondWithFile(res, 'src/client/access-denied.html');
            }
        }
        case '/stop-server': {
            const cookie = req.headers.cookie;
            if (cookie && await checkToken(cookie.split('=')[1], true)) {
                console.log('Server stop requested');
                process.exit(0);
            } else {
                return await respondWithFile(res, 'src/client/access-denied.html');
            }
        }
        case '/users': {
            const cookie = req.headers.cookie;
            if (cookie && await checkToken(cookie.split('=')[1], true)) {
                res.writeHead(200, {'Content-Type': 'application/json'});
                res.end(JSON.stringify(await util.promisify(db.all.bind(db))("SELECT name FROM users")));
                return;
            } else {
                return await respondWithFile(res, 'src/client/access-denied.html');
            }
        }
        case '/source': {
            const cookie = req.headers.cookie;
            if (cookie && await checkToken(cookie.split('=')[1], true)) {
                return await respondWithFile(res, __filename);
            } else {
                return await respondWithFile(res, 'src/client/access-denied.html');
            }
        }
        case '/register': {
            if (req.method === 'POST') {
                return new Promise((resolve, reject) => {
                    let body = '';
                    req.on('data', chunk => {
                        body += chunk.toString();
                    });
                    req.on('end', () => {
                        const [username, hash] = JSON.parse(body);
                        const query = "INSERT INTO users(name, hashedPassword) VALUES('" + username + "', '" + hash + "')";
                        db.run(query, (err) => {
                            if (err) {
                                reject(err);
                            } else {
                                res.writeHead(200, {'Content-Type': 'application/json'});
                                res.end('{"msg": "You have been registered!", "redirect": "/login"}');
                                resolve();
                            }
                        });
                    });
                });
            } else {
                return await respondWithFile(res, 'src/client/register.html');
            }
        }
        case '/login': {
            if (req.method === 'POST') {
                return new Promise((resolve, reject) => {
                    let body = '';
                    req.on('data', chunk => {
                        body += chunk.toString();
                    });
                    req.on('end', async () => {
                        const [username, hash] = JSON.parse(body);
                        if (await checkCredentials(username, hash)) {
                            const token = `${username}:${hash}`;
                            res.writeHead(200, {'Content-Type': 'application/json'});
                            res.end(`{"msg": "Log-in successful!", "token": "${token}", "redirect": "/"}`);
                        } else {
                            res.writeHead(200, {'Content-Type': 'application/json'});
                            res.end(`{"msg": "Error! Invalid credentials?"}`);
                        }
                        resolve();
                    });
                });
            } else {
                return await respondWithFile(res, 'src/client/login.html');
            }
        }
        case '/style.css': {
            return await respondWithFile(res, 'src/client/style.css');
        }
        case '/antivirus': {
            res.writeHead(301, {location: `/assets?asset=antivirus.sh`});
            return res.end();
        }
        default: {
            if (url.startsWith('/assets?asset=')) {
                let subUrl = url.split('?asset=')[1];
                if (subUrl.startsWith('/')) {
                    subUrl = subUrl.substring(1);
                }
                if (subUrl.startsWith('.')) {
                    throw new Error(`Path traversal attack alert`);
                }

                const filePath = './assets/' + subUrl;
                if ((await util.promisify(fs.stat)(filePath)).isDirectory()) {
                    let content = (await util.promisify(fs.readdir)(filePath));
                    res.writeHead(200, {'Content-Type': 'text/html'});
                    return res.end(`
                        <!DOCTYPE html>
                        <html>
                            <head>
                                <title>Folder</title>
                            </head>
                            <body>
                                ${content.join('<br>')}
                            </body>
                        </html>
                    `);
                } else {
                    return await respondWithFile(res, filePath);
                }
            } else {
                res.writeHead(404, {'Content-Type': 'text/plain'});
                return res.end(`404: Unknown URL ${url}!`);
            }
        }
    }
}


const port = process.env.PORT || 8067;

const server = http.createServer(async (req, res) => {
    try {
        await respond(req, res);
    } catch (e) {
        res.writeHead(500, {'Content-Type': 'application/json'});
        console.log(e);
        res.end(JSON.stringify({error: `${e.name}: ${e.message}`}));
    }
});

server.listen(port);

console.log(`Listening on http://localhost:${port}`);


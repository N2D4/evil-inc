const http = require('http');
const util = require('util');
const fs = require('fs');
const child_process = require('child_process');


async function respondWithFile(res, filePath) {
    const file = await util.promisify(fs.readFile)(filePath);
    const fileType = filePath.endsWith('.html') ? 'text/html'
                    : filePath.endsWith('.css') ? 'text/css'
                    : filePath.endsWith('.txt') ? 'text/plain'
                    : 'application/octet-stream';
    res.writeHead(200, {'Content-Type': fileType});
    res.end(file);
}

async function checkToken(token) {
    return checkCredentials(...token.split(':'));
}

async function checkCredentials(username, hashedPassword) {
    return true;
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
            if (cookie && checkToken(cookie.split('=')[1])) {
                return await respondWithFile(res, 'src/client/admin.html');
            } else {
                return await respondWithFile(res, 'src/client/access-denied.html');
            }
        }
        case '/register': {
            if (req.method === 'POST') {
                let body = '';
                req.on('data', chunk => {
                    body += chunk.toString();
                });
                req.on('end', () => {
                    const [username, hash] = JSON.parse(body);
                    res.writeHead(200, {'Content-Type': 'application/json'});
                    res.end('{"msg": "You have been registered!"}');
                });
            } else {
                return await respondWithFile(res, 'src/client/register.html');
            }
        }
        case '/login': {
            if (req.method === 'POST') {
                let body = '';
                req.on('data', chunk => {
                    body += chunk.toString();
                });
                req.on('end', () => {
                    const [username, hash] = JSON.parse(body);
                    if (checkCredentials(username, hash)) {
                        const token = `${username}:${hash}`;
                        res.writeHead(200, {'Content-Type': 'application/json'});
                        res.end(`{"msg": "Log-in successful!", "token": "${token}"}`);
                    } else {
                        res.writeHead(200, {'Content-Type': 'application/json'});
                        res.end(`{"msg": "Error! Invalid credentials?"}`);
                    }
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
                if (subUrl.startsWith('..')) {
                    throw new Error(`Security alert`);
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
        res.writeHead(500, {'Content-Type': 'text/plain'});
        console.log(e);
        res.end(`Error! ${e.name}: ${e.message}`);
    }
});

server.listen(port);

console.log(`Listening on http://localhost:${port}`);


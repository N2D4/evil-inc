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

async function respondToURL(url, res) {
    switch (url) {
        case '': case '/': {
            return await respondWithFile(res, 'index.html');
        }
        case '/about': {
            return await respondWithFile(res, 'about.html');
        }
        case '/blog': {
            return await respondWithFile(res, 'blog.html');
        }
        case '/admin': {
            return await respondWithFile(res, 'admin.html');
        }
        case '/register': {
            return await respondWithFile(res, 'register.html');
        }
        case '/style.css': {
            return await respondWithFile(res, 'style.css');
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
                if (subUrl.startsWith('.') || subUrl.startsWith('..')) {
                    // No directory traversal attacks!
                    throw new Error(`Not allowed!`);
                }

                const filePath = '../assets/' + subUrl;
                if ((await util.promisify(fs.stat)(filePath)).isDirectory()) {
                    let content = await util.promisify(child_process.exec)(`ls -a`, {cwd: filePath});
                    res.writeHead(200, {'Content-Type': 'text/html'});
                    return res.end(`
                        <!DOCTYPE html>
                        <html>
                            <head>
                                <title>Folder</title>
                            </head>
                            <body>
                                ${content.stdout.split('\n').join('<br>')}
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


const port = process.env.PORT || 8000;

const server = http.createServer(async (req, res) => {
    try {
        await respondToURL(req.url, res);
    } catch (e) {
        res.writeHead(500, {'Content-Type': 'text/plain'});
        console.log(e);
        res.end(`Error! ${e.name}: ${e.message}`);
    }
});

server.listen(port);

console.log(`Listening on http://localhost:${port}`);


// Serve the site locally for preview, with no dependencies:
//
//     npm run serve    # then open http://127.0.0.1:8000/  (PORT=8001 npm run serve for another port)

import { createReadStream } from 'node:fs';
import { stat } from 'node:fs/promises';
import { createServer } from 'node:http';
import { extname, join, normalize, sep } from 'node:path';

const ROOT = join(import.meta.dirname, '..');
const PORT = Number(process.env.PORT) || 8000;
const TYPES: Record<string, string> = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'text/javascript; charset=utf-8',
  '.json': 'application/json; charset=utf-8',
  '.svg': 'image/svg+xml',
  '.webp': 'image/webp',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
};

createServer(async (req, res) => {
  try {
    // normalize() on the absolute URL path can't climb above ROOT.
    let file = join(ROOT, normalize(decodeURIComponent(new URL(req.url ?? '/', 'http://x').pathname)));
    if (file !== ROOT && !file.startsWith(ROOT + sep)) throw new Error('outside the site');
    if ((await stat(file)).isDirectory()) file = join(file, 'index.html');
    const { size } = await stat(file);
    const type = TYPES[extname(file).toLowerCase()] ?? 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': type, 'Content-Length': size, 'Cache-Control': 'no-cache' });
    createReadStream(file).pipe(res);
  } catch {
    res.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' }).end('Not found\n');
  }
}).listen(PORT, '127.0.0.1', () => console.log(`Serving the site at http://127.0.0.1:${PORT}/`));

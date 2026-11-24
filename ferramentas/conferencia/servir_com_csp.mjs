// Serve web/out/ em http://localhost:4173 com a política de conteúdo de web/public/_headers, como o Cloudflare
// Pages faria, para testar no navegador se a CSP bloqueia algo que o site precisa (e se bloqueia o que deve).
//
// Uso, depois de `npm run build` em web/:  node ferramentas/conferencia/servir_com_csp.mjs
import http from "node:http"; import fs from "node:fs"; import path from "node:path";
const root = decodeURIComponent(new URL("../../web/out", import.meta.url).pathname);
const csp = fs.readFileSync(path.join(root, "_headers"), "utf8").split("\n").find((l) => l.trim().startsWith("Content-Security-Policy:")).trim().slice("Content-Security-Policy:".length).trim();
const tipos = { ".html": "text/html; charset=utf-8", ".js": "text/javascript", ".css": "text/css", ".woff2": "font/woff2", ".json": "application/json", ".txt": "text/plain", ".svg": "image/svg+xml", ".webp": "image/webp" };
http.createServer((req, res) => {
  let p = decodeURIComponent(req.url.split("?")[0]); if (p.endsWith("/")) p += "index.html";
  const f = path.join(root, p);
  if (!f.startsWith(root) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404, {"Content-Security-Policy": csp}); return res.end("404"); }
  res.writeHead(200, { "Content-Type": tipos[path.extname(f)] || "application/octet-stream", "Content-Security-Policy": csp });
  fs.createReadStream(f).pipe(res);
}).listen(4173, () => console.log("ok 4173"));

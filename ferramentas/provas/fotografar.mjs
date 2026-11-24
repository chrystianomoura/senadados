// Fotografa, num Chrome sem janela, os trechos das telas e das exportações do Senado usados como prova na
// página "Verificações" (docs/divergencias-nos-dados-do-senado.md). Só lê páginas públicas e esconde a foto do
// senador. Grava os recortes em ferramentas/saida/prints/; quem os junta é montar_provas.py.
//
// Uso (Node 22 ou mais novo; o Chrome padrão é o do macOS, ou defina CHROME=/caminho/do/chrome):
//   node ferramentas/provas/fotografar.mjs
import { spawn } from "node:child_process";
import fs from "node:fs";

const CHROME = process.env.CHROME ?? "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const SAIDA = decodeURIComponent(new URL("../saida/", import.meta.url).pathname);
const OUT = `${SAIDA}prints`;
const PORT = 9333;
fs.mkdirSync(OUT, { recursive: true });

const chrome = spawn(CHROME, [
  "--headless=new", `--remote-debugging-port=${PORT}`, `--user-data-dir=${SAIDA}chrome-prof`,
  "--hide-scrollbars", "--no-first-run", "--disable-gpu", "about:blank",
], { stdio: "ignore" });
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
for (let i = 0; i < 40; i++) { try { await fetch(`http://127.0.0.1:${PORT}/json/version`); break; } catch { await sleep(250); } }

async function aba() {
  const t = await (await fetch(`http://127.0.0.1:${PORT}/json/new?about:blank`, { method: "PUT" })).json();
  const ws = new WebSocket(t.webSocketDebuggerUrl);
  await new Promise((r) => (ws.onopen = r));
  let id = 0; const pend = new Map(); const eventos = [];
  ws.onmessage = (m) => { const d = JSON.parse(m.data); if (d.id && pend.has(d.id)) { pend.get(d.id)(d); pend.delete(d.id); } else eventos.push(d.method); };
  const send = (method, params = {}) => new Promise((res) => { const i = ++id; pend.set(i, res); ws.send(JSON.stringify({ id: i, method, params })); });
  return { send, eventos, fechar: () => ws.close() };
}

async function abrir(a, url, largura) {
  await a.send("Page.enable");
  await a.send("Emulation.setDeviceMetricsOverride", { width: largura, height: 1400, deviceScaleFactor: 1, mobile: false });
  a.eventos.length = 0;
  await a.send("Page.navigate", { url });
  for (let i = 0; i < 80 && !a.eventos.includes("Page.loadEventFired"); i++) await sleep(250);
  await sleep(2500);
}
async function js(a, expr) {
  const r = await a.send("Runtime.evaluate", { expression: expr, returnByValue: true, awaitPromise: true });
  if (r.result?.exceptionDetails) throw new Error(JSON.stringify(r.result.exceptionDetails).slice(0, 300));
  return r.result.result.value;
}
async function recortar(a, clip, arquivo) {
  const r = await a.send("Page.captureScreenshot", { format: "png", captureBeyondViewport: true, clip: { ...clip, scale: 1 } });
  fs.writeFileSync(`${OUT}/${arquivo}`, Buffer.from(r.result.data, "base64"));
}

// Esconde a foto, os dados pessoais e as caixas que não interessam; devolve onde recortar.
const PORTAL = (manter, comTitulo, semCabecalhoDaCaixa) => `(() => {
  const ocultar = (s) => document.querySelectorAll(s).forEach((e) => (e.style.display = "none"));
  ocultar(".ProfileSenadores .body");
  ["#accordion-ceaps", "#accordion-outros-gastos", "#accordion-outros", "#accordion-pessoal", "#accordion-subsidios"]
    .filter((s) => !${JSON.stringify(manter)}.includes(s)).forEach(ocultar);
  document.querySelectorAll("aside").forEach((e) => (e.style.visibility = "hidden"));
  ${comTitulo ? "" : 'ocultar("#conteudo_transparencia h1");'}
  ${semCabecalhoDaCaixa ? 'document.querySelectorAll(".accordion-heading, .accordion-inner > *:not(table), .accordion-inner thead, .accordion-inner tbody tr, .accordion-inner caption").forEach((e)=>e.style.display="none");' : ""}
  ocultar('#conteudo_transparencia div[style*="display:flex"]');
  const cab = document.querySelector(".ProfileSenadores .head").getBoundingClientRect();
  const fim = ${JSON.stringify(manter)}.map((s) => document.querySelector(s + (${semCabecalhoDaCaixa ? "true" : "false"} ? " table" : "")).getBoundingClientRect().bottom + (${semCabecalhoDaCaixa ? "true" : "false"} ? 16 : 0));
  const topo = ${comTitulo ? "document.querySelector('#conteudo_transparencia h1').getBoundingClientRect().top" : "0"};
  return { y: window.scrollY + cab.top, fim: window.scrollY + Math.max(...fim), h1: ${comTitulo ? "window.scrollY + topo" : "0"} };
})()`;

const jobs = [];
const base = "https://www6g.senado.leg.br/transparencia/sen";
jobs.push({ arq: "01-portal-camilo-pessoal.png", url: `${base}/6336/?ano=2026`, w: 1280, js: PORTAL(["#accordion-pessoal"], true, false), pad: 8, topo: 16 });
jobs.push({ arq: "03-portal-alan-pessoal.png", url: `${base}/5672/?ano=2026`, w: 1280, js: PORTAL(["#accordion-pessoal"], true, false), pad: 8, topo: 16 });
jobs.push({ arq: "09-portal-mourao-2026.png", url: `${base}/6341/?ano=2026`, w: 1280, js: PORTAL(["#accordion-ceaps"], true, false), pad: 8, topo: 16 });
const cinco = [[70, "renan"], [345, "arns"], [631, "magno"], [825, "paim"], [4531, "jayme"]];
for (const ano of [2008, 2009]) for (const [cod, n] of cinco)
{
  jobs.push({ arq: `p-${ano}-${n}.png`, url: `${base}/${cod}/?ano=${ano}`, w: 1200, js: PORTAL(["#accordion-ceaps"], false, true), pad: 6, topo: 16 });
  if (n === "renan") jobs.push({ arq: `t-${ano}-h1.png`, url: `${base}/${cod}/?ano=${ano}`, w: 1200, js: PORTAL(["#accordion-ceaps"], true, true), pad: 0, soh1: true });
}

const exportacoes = [["02-exportacao-camilo-pessoal.png", 6336], ["04-exportacao-alan-pessoal.png", 5672]];
const a = await aba();
for (const j of jobs) {
  await abrir(a, j.url, j.w);
  const r = await js(a, j.js);
  const inicio = r.y - (j.topo ?? 0);
  const clip = j.soh1 ? { x: 0, y: r.h1 - 4, width: j.w, height: 46 } : { x: 0, y: inicio, width: j.w, height: r.fim - inicio + j.pad };
  await recortar(a, clip, j.arq);
  console.log(j.arq, JSON.stringify(clip));
}
for (const [arq, cod] of exportacoes) {
  await abrir(a, `https://adm.senado.gov.br/ergon-ng-reports/api/v1/senadores/${cod}/recursos-utilizados?ano=2026&formato=html`, 1100);
  const r = await js(a, `(() => {
    const sy = window.scrollY;
    const tem = (t) => [...document.querySelectorAll("*")].filter((e) => e.children.length === 0 && e.textContent.trim().startsWith(t))[0];
    const ano = tem("Ano:"); const sec4 = tem("4. PESSOAL"); const tabelas = [...document.querySelectorAll("table")];
    const ultima = (tabelas.filter((t) => /comissionado/i.test(t.textContent)).pop() || tabelas[tabelas.length - 1]).getBoundingClientRect();
    const alvo = (e) => { let x = e; while (x.parentElement && x.parentElement.getBoundingClientRect().height < 400 && x.parentElement.tagName !== "BODY") x = x.parentElement; return x; };
    return { infoFim: sy + alvo(ano).getBoundingClientRect().bottom, secTopo: sy + alvo(sec4).getBoundingClientRect().top, fim: sy + ultima.bottom };
  })()`);
  await recortar(a, { x: 0, y: 0, width: 1100, height: r.infoFim + 16 }, `x-${cod}-topo.png`);
  await recortar(a, { x: 0, y: r.secTopo - 2, width: 1100, height: r.fim - r.secTopo + 3 }, `x-${cod}-pessoal.png`);
  console.log(arq, JSON.stringify(r));
}
a.fechar(); chrome.kill();

// Site estático (D003, D044): `next build` gera as páginas prontas em `out/`, sem servidor.
/** @type {import('next').NextConfig} */
const config = {
  output: "export",
  trailingSlash: true, // /senador/alan-rick/ vira uma pasta com index.html, como o Cloudflare Pages serve
  images: { unoptimized: true },
  reactStrictMode: true,
  // O `next dev` gera por conta própria um AGENTS.md com regras para agentes de código. As regras do
  // projeto estão no AGENTS.md da raiz; um segundo arquivo, escrito por uma dependência, só confunde.
  agentRules: false,
};

export default config;

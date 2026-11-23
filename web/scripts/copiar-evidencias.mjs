// Copia as imagens de prova de docs/evidencias/ para public/evidencias/, de onde o site as serve.
// Uma só cópia no git (a de docs/); esta pasta é gerada a cada dev e build (D038).
import { cpSync, mkdirSync, rmSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const raiz = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const origem = path.join(raiz, "..", "docs", "evidencias");
const destino = path.join(raiz, "public", "evidencias");

rmSync(destino, { recursive: true, force: true });
mkdirSync(destino, { recursive: true });
cpSync(origem, destino, { recursive: true });
console.log(`imagens de prova copiadas para ${path.relative(raiz, destino)}/`);

// Leitura dos arquivos JSON gerados pelo exportador do pipeline (web/dados/, fora do git).
// Roda só na hora do build: as páginas saem prontas, sem servidor.
import { existsSync, readFileSync } from "node:fs";
import path from "node:path";

import type { ItemLista, Metadados, Perfil } from "./types";

const PASTA = path.join(process.cwd(), "dados");

function ler<T>(...partes: string[]): T {
  const arquivo = path.join(PASTA, ...partes);
  if (!existsSync(arquivo)) {
    throw new Error(
      `Não achei ${arquivo}. Gere os arquivos antes do build, na pasta pipeline/: ` +
        "uv run --env-file ../.env python -m senadados_pipeline.exportar",
    );
  }
  return JSON.parse(readFileSync(arquivo, "utf-8")) as T;
}

export const metadados = (): Metadados => ler<Metadados>("metadados.json");
export const lista = (): ItemLista[] => ler<ItemLista[]>("senadores.json");
export const perfil = (slug: string): Perfil => ler<Perfil>("senadores", `${slug}.json`);
export const slugs = (): string[] => lista().map((s) => s.slug);

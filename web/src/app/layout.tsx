import type { Metadata, Viewport } from "next";
import type { ReactNode } from "react";

// Fontes hospedadas no próprio site (nenhuma visita contata o Google): D029 e D046.
import "@fontsource-variable/bricolage-grotesque";
import "@fontsource-variable/fraunces";
import "@fontsource-variable/hanken-grotesk";
import "./globals.css";

export const metadata: Metadata = {
  title: { default: "Senadados", template: "%s · Senadados" },
  description:
    "Os valores que o Senado publica sobre os senadores em exercício, explicados para qualquer pessoa.",
};

export const viewport: Viewport = {
  width: "device-width",
  initialScale: 1,
  themeColor: "#faf7f2",
};

export default function Layout({ children }: { children: ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        <a className="pular" href="#conteudo">
          Pular para o conteúdo
        </a>
        {children}
      </body>
    </html>
  );
}

// Tipos do contrato dos dados (docs/contrato-dos-dados.md, versão 1). O exportador do pipeline
// gera os arquivos; o site só os lê. Bloco `null` = não provado: o site não mostra nada no lugar.

export interface Metadados {
  versao_contrato: number;
  data_referencia: string; // AAAA-MM-DD
  carregado_em: string;
  anos: string;
  senadores: number;
  fonte: string;
}

export interface ItemLista {
  codigo: number;
  slug: string;
  nome: string;
  tipo: string; // "Titular" ou "1º Suplente"
  uf: string;
  partido: string;
  /** Endereço da foto oficial, só quando provado (D045). Ainda não existe nos dados reais. */
  foto_url?: string | null;
}

export interface Salario {
  ano: number;
  mes: number;
  basica_centavos: number;
  liquida_centavos: number;
}

export interface MesTotal {
  mes: number;
  total_centavos: number;
}

export interface CategoriaTotal {
  nome: string;
  nome_oficial: string;
  total_centavos: number;
}

export interface CotaAno {
  ano: number;
  parcial: boolean;
  total_centavos: number;
  meses: MesTotal[];
  categorias: CategoriaTotal[];
  maior_mes: MesTotal;
}

export interface Empresa {
  cnpj: string;
  nome: string;
  qtd_despesas: number;
  total_centavos: number;
}

export interface Agrupado {
  tipo: "pessoa_fisica" | "outro" | "sem_documento";
  qtd_despesas: number;
  total_centavos: number;
  maior_centavos: number;
}

export interface FornecedoresAno {
  ano: number;
  empresas: Empresa[];
  total_empresas: number;
  agrupados: Agrupado[];
}

export interface Equipe {
  ano: number;
  pessoas: number;
}

export interface Contato {
  endereco: string | null;
  telefones: string[];
  email: string | null;
}

export interface MesMoradia {
  mes: string; // AAAA-MM
  auxilio_moradia: boolean;
  imovel_funcional: boolean;
}

export interface Moradia {
  ano: number;
  meses: MesMoradia[];
}

export interface QuemE {
  foto: { url: string; credito: string } | null;
  mandato: { inicio: number; fim: number } | null;
}

export interface Perfil extends ItemLista {
  quem_e: QuemE | null; // foto e mandato: D045, ainda sem dados reais
  salario: Salario | null;
  cota: { anos: CotaAno[] } | null;
  fornecedores: { anos: FornecedoresAno[] } | null;
  equipe: Equipe | null;
  contato: Contato | null;
  moradia: Moradia | null;
}

export interface ResumoVerificacao {
  verificacao: string;
  ano: number;
  identicos: number;
  explicados: number;
  pendentes: number;
  ocultos: number;
  verificado_em: string;
}

export interface MotivoVerificacao {
  verificacao: string;
  ano: number;
  situacao: "pendente" | "oculto";
  motivo: string;
  qtd: number;
}

/** O que a página "Verificações" mostra: só contagens e motivos, nunca nomes (D042). */
export interface Verificacoes {
  resumo: ResumoVerificacao[];
  motivos: MotivoVerificacao[];
}

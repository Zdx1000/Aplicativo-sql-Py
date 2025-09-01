"""
Importa um XLSX (Código/Produto/Valor) e alimenta a tabela 'configuracoes_api' (Configurações dos APIs) no SQLite.

Formato esperado das colunas (tolerante a acentos e variações):
- Código ou Codigo
- Produto
- Valor (decimal; aceita vírgula e ponto)

Obs:
- Este script limpa a tabela e insere os novos registros (substituição total).
- Ajuste os caminhos de EXCEL_FILE, SHEET_NAME e DB_PATH conforme necessário.
"""

import sqlite3
from datetime import datetime
import unicodedata
from typing import Any

import pandas as pd

# Ajuste estes caminhos conforme sua necessidade
EXCEL_FILE = 'configuracoes.xlsx'
SHEET_NAME = 'Plan1'
# Caminho do banco usado pelo app Controle de estoque
DB_PATH = r"dados.db"


def _canon(s: str) -> str:
    s = (s or '').strip().lower()
    s = unicodedata.normalize('NFKD', s)
    s = ''.join(ch for ch in s if not unicodedata.combining(ch))
    return s


def _parse_valor(v: Any) -> float | None:
    if v is None or (isinstance(v, float) and pd.isna(v)):
        return None
    if isinstance(v, (int, float)):
        try:
            return float(v)
        except Exception:
            return None
    s = str(v).strip().replace('R$', '').replace('\u00A0', ' ').replace(' ', '')
    if not s:
        return None
    # 1.234,56 | 1,234.56 | 1234,56 | 1234.56 | 1234
    if ',' in s and '.' in s:
        if s.rfind(',') > s.rfind('.'):
            s = s.replace('.', '').replace(',', '.')
        else:
            s = s.replace(',', '')
    elif ',' in s:
        s = s.replace('.', '').replace(',', '.')
    try:
        return float(s)
    except Exception:
        return None


def main() -> None:
    df = pd.read_excel(EXCEL_FILE, sheet_name=SHEET_NAME)
    # Normaliza nomes de colunas
    cols_map = {c: _canon(str(c)) for c in df.columns}
    df.columns = [cols_map[c] for c in df.columns]

    # Mapeia possíveis variações
    col_codigo = None
    col_produto = None
    col_valor = None
    for c in df.columns:
        if c.startswith('codigo') or c == 'codigo' or c == 'cod' or c == 'codo' or c == 'cód' or c == 'código':
            col_codigo = c
        elif c.startswith('produto') or c == 'produto':
            col_produto = c
        elif c.startswith('valor') or c == 'valor':
            col_valor = c
    if not (col_codigo and col_produto and col_valor):
        raise SystemExit(f"Colunas obrigatórias não encontradas. Encontradas: {list(df.columns)}")

    # Seleciona e renomeia
    df = df[[col_codigo, col_produto, col_valor]].copy()
    df.columns = ['codigo', 'produto', 'valor']

    # Limpa linhas vazias e converte valor
    df['codigo'] = df['codigo'].astype(str).str.strip()
    df['produto'] = df['produto'].astype(str).str.strip()
    df['valor'] = df['valor'].apply(_parse_valor)
    df = df[(df['codigo'] != '') & (df['produto'] != '')]
    df['valor'] = df['valor'].fillna(0.0)

    # created_at obrigatório na tabela (sem default no DB); usar timestamp atual
    now_iso = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    df['created_at'] = now_iso

    # Substitui conteúdo da tabela mantendo o schema existente
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute('DELETE FROM configuracoes_api')
        # Inserção em lote via to_sql no estilo pedido
        df.to_sql('configuracoes_api', conn, if_exists='append', index=False)
    print(f"Importação concluída. Linhas salvas: {len(df)}")


if __name__ == '__main__':
    main()
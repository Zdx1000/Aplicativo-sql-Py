import pandas as pd
import sys
import os
from database import salvar_monitoramento

ARQUIVO_XLSX = sys.argv[1] if len(sys.argv) > 1 else "Dados.xlsx"

if not os.path.exists(ARQUIVO_XLSX):
    print(f"Arquivo não encontrado: {ARQUIVO_XLSX}")
    sys.exit(1)

df = pd.read_excel(ARQUIVO_XLSX)
campos = ["Onda", "Carga", "Container", "Responsável", "Data", "Usuário", "setor"]
for campo in campos:
    if campo not in df.columns:
        print(f"Coluna obrigatória não encontrada: {campo}")
        sys.exit(1)

sucesso = 0
for _, row in df.iterrows():
    try:
        salvar_monitoramento(
            onda=str(row["Onda"]),
            carga=str(row["Carga"]),
            container=str(row["Container"]),
            responsavel=str(row["Responsável"]),
            setor=str(row["setor"]),
            observacao="Reimpressões WMS"
        )
        # suario=str(row["Responsável"])
        sucesso += 1
    except Exception as e:
        print(f"Erro ao inserir linha: {e}")
print(f"Inserção concluída: {sucesso} registros inseridos.")

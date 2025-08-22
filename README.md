# Aplicação de Cadastro de Itens

Interface gráfica em PySide6 para inserir registros com Item, Quantidade, Motivo e Setor Responsável, persistindo em banco via SQLAlchemy (SQLite por padrão).

Agora inclui sistema de usuários (login/registro) com hash de senha (bcrypt via passlib) e associação de cada registro ao usuário que inseriu.

## Requisitos
- Python 3.11+

## Instalação
```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Execução
```powershell
python .\servidor.py
```

## Configurar outro banco
Defina a variável de ambiente `DATABASE_URL` (ex: PostgreSQL):
```powershell
$env:DATABASE_URL = "postgresql+psycopg://user:senha@localhost:5432/meubanco"
python .\servidor.py
```

## Estrutura
- `servidor.py`: UI
- `database.py`: camada de persistência (SQLAlchemy)
- `requirements.txt`: dependências
 - Autenticação: criação de usuário (ADMINISTRADOR ou USUARIO) e login antes de acessar o sistema.
 - Registro exige API Key: `REGISTRO_API_KEY_USUARIO` (ou legado `REGISTRO_API_KEY`) para usuários comuns e `REGISTRO_API_KEY_ADMINISTRADOR` (ou legado `REGISTRO_API_KEY_ADM`) para administradores.

### API Keys de Registro
Defina as chaves (exemplos):
```powershell
$env:REGISTRO_API_KEY_USUARIO = "MINHA_CHAVE_USUARIO"
$env:REGISTRO_API_KEY_ADM = "MINHA_CHAVE_ADMIN"
python .\servidor.py
```
No diálogo de registro informe a chave correta conforme o tipo selecionado (USUARIO ou ADMINISTRADOR). Se `REGISTRO_API_KEY_USUARIO` não for definida, será usada `REGISTRO_API_KEY` (legado) ou o padrão `MINHA_CHAVE_REGISTRO_123`.

## Próximos Passos (opcionais)
- Listagem e busca de registros
- Exportação CSV/Excel
- Validação avançada e logs estruturados

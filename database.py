"""Camada de persistência usando SQLAlchemy.

Objetivos:
 - Fornecer engine configurável via variável de ambiente DATABASE_URL.
 - Criar tabela de registros caso não exista.
 - Expor função salvar_registro para inserir dados.
 - Facilitar troca futura para outro SGBD (PostgreSQL, MySQL etc.) sem alterar UI.
"""

from __future__ import annotations

from datetime import datetime, date
from decimal import Decimal
from typing import Iterable, Optional, List
import os
import sys
from pathlib import Path

from sqlalchemy import (
    create_engine,
    String,
    Integer,
    DateTime,
    ForeignKey,
    text,
    Date,
    Text,
    Numeric,
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, sessionmaker, Session, relationship
from sqlalchemy import event

from passlib.context import CryptContext


try:  # pragma: no cover
    import passlib.handlers.bcrypt  # noqa: F401
except Exception:
    pass

try:  # pragma: no cover
    from dotenv import load_dotenv

    def _load_env() -> None:
        loaded = False
        # 1) Diretório atual (onde o app foi iniciado)
        try:
            loaded = load_dotenv(dotenv_path=Path.cwd() / ".env", override=False)
        except Exception:
            pass
        # 2) Ao lado do executável congelado (auto-py-to-exe / PyInstaller)
        try:
            if not loaded and getattr(sys, "frozen", False):
                exe_dir = Path(sys.executable).resolve().parent
                loaded = load_dotenv(dotenv_path=exe_dir / ".env", override=False)
        except Exception:
            pass
        # 3) Ao lado deste arquivo (modo desenvolvimento)
        try:
            if not loaded:
                loaded = load_dotenv(dotenv_path=Path(__file__).resolve().parent / ".env", override=False)
        except Exception:
            pass
        # 4) Diretório temporário do PyInstaller (_MEIPASS), caso .env seja empacotado
        try:
            if not loaded:
                base = getattr(sys, "_MEIPASS", None)
                if base:
                    load_dotenv(dotenv_path=Path(base) / ".env", override=False)
        except Exception:
            pass

    _load_env()
except Exception:
    pass


engine = create_engine(os.getenv("DATABASE_URL", "sqlite:///dados.db"), future=True, echo=False)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False, autocommit=False, future=True)

Base = declarative_base()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ---- Espelhamento automático do SQLite (opcional) ---- #
def _sqlite_db_path() -> str | None:
    try:
        if engine.url.get_backend_name() != "sqlite":
            return None
        return engine.url.database  # caminho do arquivo .db
    except Exception:
        return None


def _sqlite_online_backup(src_path: str, dst_path: str) -> None:
    """Copia o banco SQLite aberto para outro arquivo usando a API de backup.

    Cria diretórios do destino se necessário. Silencioso em caso de erro (melhor esforço).
    """
    try:
        import os
        import sqlite3
        if not src_path or not dst_path:
            return
        # Evita backup para o mesmo arquivo
        if os.path.abspath(src_path) == os.path.abspath(dst_path):
            return
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        with sqlite3.connect(src_path) as src, sqlite3.connect(dst_path) as dst:
            src.backup(dst)
    except Exception:
        # Melhor esforço: não interrompe o fluxo da aplicação
        pass


@event.listens_for(Session, "after_commit")
def _mirror_sqlite_after_commit(session):  # pragma: no cover - efeito colateral em runtime
    mirror_path = os.getenv("SQLITE_MIRROR_PATH") or ""
    if not mirror_path:
        return
    src = _sqlite_db_path()
    if not src:
        return
    _sqlite_online_backup(src, mirror_path)


class UserModel(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True, default="USUARIO")  # ADMINISTRADOR ou USUARIO
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    registros: Mapped[list["RegistroModel"]] = relationship(back_populates="usuario_rel", cascade="all,delete-orphan")

    def verificar_senha(self, senha: str) -> bool:
        return pwd_context.verify(senha, self.senha_hash)

    @staticmethod
    def hash_senha(senha: str) -> str:
        return pwd_context.hash(senha)


class RegistroModel(Base):
    __tablename__ = "registros"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    item: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    motivo: Mapped[str] = mapped_column(String(2000), nullable=False)
    setor_responsavel: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    usuario: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)  # nome do usuário que inseriu
    usuario_id: Mapped[Optional[int]] = mapped_column(ForeignKey("usuarios.id"), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    usuario_rel: Mapped[Optional[UserModel]] = relationship(back_populates="registros")

    def __repr__(self) -> str:  # pragma: no cover - representação simples
        return f"<RegistroModel id={self.id} item={self.item!r} qtd={self.quantidade}>"


class MonitoramentoModel(Base):
    __tablename__ = "MONITORAMENTO"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    onda: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    carga: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    container: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    responsavel: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    setor: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # Usuário que inseriu (igual ao padrão de RegistroModel)
    usuario: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Monitoramento id={self.id} onda={self.onda!r} carga={self.carga!r} container={self.container!r}>"


class AlmoxafireModel(Base):
    __tablename__ = "ALMOXAFIRE"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    setor: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    turno: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    matricula: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    responsavel: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    insumo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    usuario: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Almoxafire id={self.id} setor={self.setor!r} insumo={self.insumo!r} qtd={self.quantidade}>"


class EpiModel(Base):
    __tablename__ = "EPIS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    matricula: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    setor: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    turno: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    primeira: Mapped[str] = mapped_column(String(10), nullable=False)  # 'SIM' | 'NÃO'
    data_ref: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    responsavel: Mapped[int] = mapped_column(Integer, nullable=False, index=True)
    observacao: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    usuario: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    itens: Mapped[list["EpiItemModel"]] = relationship(back_populates="epi", cascade="all,delete-orphan")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<EPI id={self.id} mat={self.matricula} data={self.data_ref.isoformat()}>"


class EpiItemModel(Base):
    __tablename__ = "EPIS_ITENS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    epi_id: Mapped[int] = mapped_column(ForeignKey("EPIS.id"), nullable=False, index=True)
    codigo: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    produto: Mapped[str] = mapped_column(String(255), nullable=False)
    quantidade: Mapped[int] = mapped_column(Integer, nullable=False)
    uon: Mapped[Optional[str]] = mapped_column(String(10), nullable=True)  # PARES | UNID
    valor_unit: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    valor_total: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)

    epi: Mapped[EpiModel] = relationship(back_populates="itens")


class ConfiguracaoAPIEPI(Base):
    """Tabela para armazenar o catálogo de Código/Produto utilizado na página de EPIs.

    Nome da tabela conforme solicitado: 'configuracoes_api'.
    """
    __tablename__ = "configuracoes_api"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    produto: Mapped[str] = mapped_column(String(255), nullable=False)
    valor: Mapped[Decimal | None] = mapped_column(Numeric(14, 2), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ConfiguracaoAPIEPI id={self.id} codigo={self.codigo!r} produto={self.produto!r}>"


class AuditLogModel(Base):
    """Tabela de auditoria genérica para registrar ações do sistema.

    Campos principais:
     - usuario: quem executou (pode ser None)
     - transacao: nome da seção/feature (ex.: Bloqueado, Consultas, Grafico, Almoxarifado, EPIs, Consolidado)
     - tipo: tipo da ação (input | output | consulta | alteração)
     - created_at: timestamp UTC da ocorrência
    """
    __tablename__ = "AUDIT_LOGS"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario: Mapped[Optional[str]] = mapped_column(String(150), nullable=True, index=True)
    transacao: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    tipo: Mapped[str] = mapped_column(String(20), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

class ConsolidadoLinhaModel(Base):
    """Tabela detalhada com as colunas exatamente como no XLSX.

    Observação: nomes com espaços/acentos/símbolos são preservados na coluna
    do banco via "name"; os atributos Python usam nomes válidos (snake_case).
    """
    __tablename__ = "CONSOLIDADO"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    data_ref: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    # Colunas do XLSX (nomes preservados no banco):
    arm_: Mapped[int | None] = mapped_column("arm.", Integer, nullable=True, index=True)
    descricao_filial: Mapped[str | None] = mapped_column("Descrição Filial", String(255), nullable=True)
    r_estoque: Mapped[Decimal | None] = mapped_column("R$ Estoque", Numeric(14, 2), nullable=True)
    qtd_item_mix: Mapped[int | None] = mapped_column("Qtde Item Mix", Integer, nullable=True)
    qtd_item_com_estoque: Mapped[int | None] = mapped_column("Qtde Item com Estoque", Integer, nullable=True)
    qtd_item_sem_estoque: Mapped[int | None] = mapped_column("Qtde Item sem Estoque", Integer, nullable=True)
    r_bloq_total: Mapped[Decimal | None] = mapped_column("R$ Bloq. Total", Numeric(14, 2), nullable=True)
    r_bloq_no_estoque: Mapped[Decimal | None] = mapped_column("R$ Bloq. no ESTOQUE", Numeric(14, 2), nullable=True)
    r_bloq_em_negoc: Mapped[Decimal | None] = mapped_column("R$ Bloq. em Negoc.", Numeric(14, 2), nullable=True)
    r_bloq_saldo: Mapped[Decimal | None] = mapped_column("R$ Bloq. SALDO", Numeric(14, 2), nullable=True)
    pct_item_com_estoque: Mapped[Decimal | None] = mapped_column("% Item com Estoque", Numeric(7, 4), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<ConsolidadoLinhaModel id={self.id} data_ref={self.data_ref.isoformat()}>"


def init_db() -> None:
    """Cria as tabelas se não existirem e aplica pequenas migrações."""
    # Migração: se CONSOLIDADO existir no formato antigo (com coluna 'conteudo'), dropar
    with engine.begin() as conn:
        try:
            cols = conn.exec_driver_sql("PRAGMA table_info(CONSOLIDADO)").fetchall()
            col_names = {c[1] for c in cols}
            if col_names and ("conteudo" in col_names) and ("arm." not in col_names):
                conn.exec_driver_sql("DROP TABLE CONSOLIDADO")
        except Exception:
            pass
    # Cria tabelas
    Base.metadata.create_all(engine)
    # Adiciona coluna usuario se banco antigo não possuir
    with engine.begin() as conn:
        cols = conn.exec_driver_sql("PRAGMA table_info(registros)").fetchall()
        col_names = {c[1] for c in cols}
        if "usuario" not in col_names:
            conn.exec_driver_sql("ALTER TABLE registros ADD COLUMN usuario VARCHAR(150)")
        if "usuario_id" not in col_names:
            conn.exec_driver_sql("ALTER TABLE registros ADD COLUMN usuario_id INTEGER REFERENCES usuarios(id)")
        # Migrações leves para MONITORAMENTO (se a tabela existir)
        try:
            cols_m = conn.exec_driver_sql("PRAGMA table_info(MONITORAMENTO)").fetchall()
            if cols_m:
                col_m_names = {c[1] for c in cols_m}
                if "usuario" not in col_m_names:
                    conn.exec_driver_sql("ALTER TABLE MONITORAMENTO ADD COLUMN usuario VARCHAR(150)")
        except Exception:
            pass
        # Garante existência da tabela de auditoria
        try:
            conn.exec_driver_sql("""
                CREATE TABLE IF NOT EXISTS AUDIT_LOGS (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    usuario VARCHAR(150),
                    transacao VARCHAR(50) NOT NULL,
                    tipo VARCHAR(20) NOT NULL,
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
        except Exception:
            pass
        # Migrações leves para ALMOXAFIRE (se a tabela existir, garantir coluna usuario)
        try:
            cols_a = conn.exec_driver_sql("PRAGMA table_info(ALMOXAFIRE)").fetchall()
            if cols_a:
                col_a_names = {c[1] for c in cols_a}
                if "usuario" not in col_a_names:
                    conn.exec_driver_sql("ALTER TABLE ALMOXAFIRE ADD COLUMN usuario VARCHAR(150)")
        except Exception:
            pass
        # Migração leve para CONFIGURACOES_API (adicionar coluna valor se ausente)
        try:
            cols_cfg = conn.exec_driver_sql("PRAGMA table_info(configuracoes_api)").fetchall()
            if cols_cfg:
                col_cfg_names = {c[1] for c in cols_cfg}
                if "valor" not in col_cfg_names:
                    conn.exec_driver_sql("ALTER TABLE configuracoes_api ADD COLUMN valor NUMERIC(14,2)")
        except Exception:
            pass


def get_session() -> Session:
    return SessionLocal()


def salvar_auditoria(*, transacao: str, tipo: str) -> int:
    """Registra um evento de auditoria com usuário atual (se houver)."""
    transacao = (transacao or "").strip()
    tipo = (tipo or "").strip().lower()
    if not transacao or not tipo:
        raise ValueError("transacao/tipo obrigatórios")
    if tipo not in {"input", "output", "consulta", "alteração", "alteracao"}:
        # aceita 'alteracao' sem acento e normaliza
        tipo = "consulta"
    if tipo == "alteracao":
        tipo = "alteração"
    with get_session() as session:
        try:
            obj = AuditLogModel(
                usuario=_CurrentUser.username if _CurrentUser.username else None,
                transacao=transacao,
                tipo=tipo,
            )
            session.add(obj)
            session.commit()
            session.refresh(obj)
            return obj.id
        except Exception:
            # Não quebra o fluxo da aplicação por falha de auditoria
            return 0


def listar_auditoria(limit: int = 10) -> list[dict]:
    """Retorna os últimos logs de auditoria, mais recentes primeiro (limite padrão 10)."""
    with get_session() as session:
        try:
            q = session.query(AuditLogModel).order_by(AuditLogModel.created_at.desc()).limit(int(limit))
            out: list[dict] = []
            for r in q.all():
                out.append({
                    "usuario": r.usuario or "",
                    "transacao": r.transacao,
                    "tipo": r.tipo,
                    "created_at": r.created_at.isoformat(timespec="seconds"),
                })
            return out
        except Exception:
            return []


def salvar_registro(*, item: int, quantidade: int, motivo: str, setor_responsavel: str) -> int:
    """Salva um registro e retorna o ID gerado.

    Operação síncrona, adequada para inserções rápidas. Para alto volume em lote,
    preferir criar sessão externa e usar add_all + commit único.
    """
    with get_session() as session:
        modelo = RegistroModel(
            item=item,
            quantidade=quantidade,
            motivo=motivo,
            setor_responsavel=setor_responsavel,
            usuario=_CurrentUser.username if _CurrentUser.username else None,
            usuario_id=_CurrentUser.user_id,
        )
        session.add(modelo)
        session.commit()
        session.refresh(modelo)
        try:
            salvar_auditoria(transacao="Bloqueado", tipo="input")
        except Exception:
            pass
        return modelo.id


def salvar_registros_bulk(registros: Iterable[dict]) -> int:
    """Inserção em lote; retorna quantidade inserida."""
    with get_session() as session:
        objs = [RegistroModel(**r) for r in registros]
        session.add_all(objs)
        session.commit()
        return len(objs)


def salvar_monitoramento(*, onda: str, carga: str, container: str, responsavel: str, setor: str, observacao: Optional[str] = None) -> int:
    """Salva um registro na tabela MONITORAMENTO e retorna o ID gerado.

    Normalizações:
    - responsavel: armazenado em UPPER.
    - Campos são stripados para remover espaços supérfluos.
    """
    onda = (onda or "").strip()
    carga = (carga or "").strip()
    container = (container or "").strip()
    responsavel = (responsavel or "").strip().upper()
    setor = (setor or "").strip()
    observacao = (observacao or None)
    if not onda or not carga or not container or not responsavel or not setor:
        raise ValueError("Campos obrigatórios ausentes em Monitoramento")
    with get_session() as session:
        obj = MonitoramentoModel(
            onda=onda,
            carga=carga,
            container=container,
            responsavel=responsavel,
            setor=setor,
            observacao=observacao,
            usuario=_CurrentUser.username if _CurrentUser.username else None,
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        try:
            salvar_auditoria(transacao="Monitoramento", tipo="input")
        except Exception:
            pass
        return obj.id


def salvar_almoxafire(*, setor: str, turno: str, matricula: int, responsavel: str, insumo: str, quantidade: int, observacao: Optional[str] = None) -> int:
    """Salva um registro na tabela ALMOXAFIRE e retorna o ID gerado.

    Normalizações:
    - setor/responsavel/observacao: armazenados em UPPER (observacao pode ser None).
    - strings stripadas para remover espaços.
    """
    setor = (setor or "").strip().upper()
    turno = (turno or "").strip()
    responsavel = (responsavel or "").strip().upper()
    insumo = (insumo or "").strip()
    observacao = (observacao.strip().upper() if (observacao is not None and observacao.strip() != "") else None)
    try:
        matricula_int = int(matricula)
        quantidade_int = int(quantidade)
    except (TypeError, ValueError):
        raise ValueError("Matrícula/Quantidade inválidas")
    if not setor or not turno or not responsavel or not insumo or quantidade_int <= 0 or matricula_int <= 0:
        raise ValueError("Campos obrigatórios ausentes em Almoxafire")
    with get_session() as session:
        obj = AlmoxafireModel(
            setor=setor,
            turno=turno,
            matricula=matricula_int,
            responsavel=responsavel,
            insumo=insumo,
            quantidade=quantidade_int,
            observacao=observacao,
            usuario=_CurrentUser.username if _CurrentUser.username else None,
        )
        session.add(obj)
        session.commit()
        session.refresh(obj)
        try:
            salvar_auditoria(transacao="Almoxarifado", tipo="input")
        except Exception:
            pass
        return obj.id


def salvar_epi(
    *,
    matricula: int,
    setor: str,
    turno: str,
    primeira: str,
    data: str,
    responsavel: int,
    observacao: Optional[str],
    produtos: list[dict],
) -> int:
    """Salva um registro de EPIs (cabeçalho EPIS + itens EPIS_ITENS) e retorna o ID do cabeçalho.

    Normalizações:
    - setor/observacao uppercase (observacao pode ser None)
    - primeira mantém 'SIM'|'NÃO' conforme UI
    - data é string 'YYYY-MM-DD'
    - valor_unit/valor_total quando fornecidos são armazenados como Decimal
    - uon opcional ('PARES'|'UNID')
    """
    from datetime import date as _date
    setor_norm = (setor or "").strip().upper()
    turno_norm = (turno or "").strip()
    primeira_norm = (primeira or "").strip()
    observacao_norm = (observacao.strip().upper() if (observacao and observacao.strip() != "") else None)
    try:
        mat_int = int(matricula)
        resp_int = int(responsavel)
        data_dt = _date.fromisoformat(str(data))
    except (TypeError, ValueError):
        raise ValueError("Dados inválidos para EPIs (matricula/responsavel/data)")
    if not setor_norm or not turno_norm or mat_int <= 0 or resp_int <= 0:
        raise ValueError("Campos obrigatórios ausentes em EPIs")
    with get_session() as session:
        cab = EpiModel(
            matricula=mat_int,
            setor=setor_norm,
            turno=turno_norm,
            primeira=primeira_norm,
            data_ref=data_dt,
            responsavel=resp_int,
            observacao=observacao_norm,
            usuario=_CurrentUser.username if _CurrentUser.username else None,
        )
        session.add(cab)
        session.flush()  # obtém id para FK dos itens
        itens_objs: list[EpiItemModel] = []
        for p in produtos or []:
            codigo = str(p.get("codigo", "")).strip()
            produto = str(p.get("produto", "")).strip()
            try:
                quantidade = int(p.get("quantidade", 0))
            except Exception:
                quantidade = 0
            if not codigo or not produto or quantidade <= 0:
                continue
            uon = p.get("uon")
            if uon:
                uon = str(uon).strip().upper()
                if uon not in {"PARES", "UNID"}:
                    uon = None
            # valores (se existirem do front, podem vir apenas para exibição)
            valor_unit = try_decimal(p.get("valor_unit"))
            valor_total = try_decimal(p.get("valor_total"))
            itens_objs.append(
                EpiItemModel(
                    epi_id=cab.id,
                    codigo=codigo,
                    produto=produto,
                    quantidade=quantidade,
                    uon=uon,
                    valor_unit=valor_unit,
                    valor_total=valor_total,
                )
            )
        if itens_objs:
            session.add_all(itens_objs)
        session.commit()
        session.refresh(cab)
        try:
            salvar_auditoria(transacao="EPIs", tipo="input")
        except Exception:
            pass
        return cab.id


# ---------------- Autenticação & Usuários ---------------- #

class _CurrentUser:
    username: Optional[str] = None
    user_id: Optional[int] = None
    tipo: Optional[str] = None

    @classmethod
    def set(cls, *, username: str, user_id: int, tipo: str) -> None:
        cls.username = username
        cls.user_id = user_id
        cls.tipo = tipo

    @classmethod
    def clear(cls) -> None:
        cls.username = None
        cls.user_id = None
        cls.tipo = None


def criar_usuario(*, username: str, senha: str, tipo: str = "USUARIO", api_key: str) -> int:
    """Cria usuário; retorna id.

    Regras de API key:
    - Para tipo USUARIO: deve corresponder a REGISTRO_API_KEY_USUARIO.
    - Para tipo ADMINISTRADOR: deve corresponder a REGISTRO_API_KEY_ADMINISTRADOR.
    Aceita 'ADM' (legado) e normaliza para 'ADMINISTRADOR'.
    """
    # Normalização de tipo legado
    if tipo == "ADM":
        tipo = "ADMINISTRADOR"
    # Busca chaves do ambiente no momento do uso (sem hardcode nem globais)
    key_user_env = os.getenv("REGISTRO_API_KEY_USUARIO") or os.getenv("REGISTRO_API_KEY")
    key_admin_env = os.getenv("REGISTRO_API_KEY_ADMINISTRADOR") or os.getenv("REGISTRO_API_KEY_ADM")
    if tipo == "ADMINISTRADOR":
        if not key_admin_env or api_key != key_admin_env:
            raise ValueError("API key inválida para registro ADMINISTRADOR")
    elif tipo == "USUARIO":
        if not key_user_env or api_key != key_user_env:
            raise ValueError("API key inválida para registro USUARIO")
    else:
        raise ValueError("Tipo inválido")
    username = username.strip()
    if not username or not senha:
        raise ValueError("Usuário e senha obrigatórios")
    if tipo not in {"ADMINISTRADOR", "USUARIO"}:
        raise ValueError("Tipo inválido")
    with get_session() as session:
        if session.query(UserModel).filter_by(username=username).first():
            raise ValueError("Usuário já existe")
        user = UserModel(
            username=username,
            senha_hash=UserModel.hash_senha(senha),
            tipo=tipo,
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user.id


def autenticar_usuario(*, username: str, senha: str) -> bool:
    with get_session() as session:
        user = session.query(UserModel).filter_by(username=username).first()
        if not user:
            return False
        if not user.verificar_senha(senha):
            return False
        _CurrentUser.set(username=username, user_id=user.id, tipo=user.tipo)
        return True


def obter_usuario_atual() -> Optional[str]:
    return _CurrentUser.username


def obter_tipo_usuario_atual() -> Optional[str]:
    return _CurrentUser.tipo


def alterar_senha(*, username: str, senha_atual: str, nova_senha: str) -> bool:
    """Altera a senha do usuário se a senha atual estiver correta.

    Retorna True em caso de sucesso, False se credenciais inválidas.
    """
    if not nova_senha:
        raise ValueError("Nova senha vazia")
    with get_session() as session:
        user = session.query(UserModel).filter_by(username=username).first()
        if not user:
            return False
        if not user.verificar_senha(senha_atual):
            return False
        user.senha_hash = UserModel.hash_senha(nova_senha)
        session.commit()
        return True


# --------- Funções administrativas (apenas ADMINISTRADOR) --------- #

def _assert_admin() -> None:
    if _CurrentUser.tipo != "ADMINISTRADOR":  # pragma: no cover - segurança em runtime
        raise ValueError("Operação permitida apenas para ADMINISTRADOR")


def listar_usuarios(*, tipo: Optional[str] = None) -> list[dict]:
    """Retorna lista de usuários (cada um como dict). Se tipo for passado, filtra.

    Não retorna a hash da senha por segurança.
    """
    _assert_admin()
    with get_session() as session:
        query = session.query(UserModel)
        if tipo:
            query = query.filter(UserModel.tipo == tipo)
        dados = []
        for u in query.order_by(UserModel.username.asc()).all():
            dados.append({
                "id": u.id,
                "username": u.username,
                "tipo": u.tipo,
                "created_at": u.created_at.isoformat(),
            })
        return dados


def redefinir_senha_usuario(*, username: str, nova_senha: str) -> bool:
    """Admin redefine senha de um usuário sem precisar da senha atual.

    Retorna True se usuário encontrado e senha alterada.
    """
    if not nova_senha:
        raise ValueError("Nova senha vazia")
    _assert_admin()
    with get_session() as session:
        user = session.query(UserModel).filter_by(username=username).first()
        if not user:
            return False
        # Evita redefinir senha de outro ADMINISTRADOR inadvertidamente
        if user.tipo == "ADMINISTRADOR" and username != _CurrentUser.username:
            raise ValueError("Não é permitido redefinir senha de outro ADMINISTRADOR")
        user.senha_hash = UserModel.hash_senha(nova_senha)
        session.commit()
        return True


def excluir_usuario(*, username: str) -> bool:
    """Exclui usuário (somente tipo USUARIO). Retorna True se removido."""
    _assert_admin()
    with get_session() as session:
        user = session.query(UserModel).filter_by(username=username).first()
        if not user:
            return False
        if user.tipo != "USUARIO":
            raise ValueError("Só é permitido excluir usuários do tipo USUARIO")
        session.delete(user)
        session.commit()
        return True


# ---------------- Consultas ---------------- #

def consultar_registros_por_item(item: int) -> list[dict]:
    """Retorna lista de registros para o código de item informado.

    Ordena por created_at DESC (mais recentes primeiro).
    """
    try:
        item_int = int(item)
    except (TypeError, ValueError):  # pragma: no cover - validação defensiva
        raise ValueError("Item inválido para consulta")
    if item_int <= 0:
        raise ValueError("Item deve ser > 0")
    with get_session() as session:
        regs = (
            session.query(RegistroModel)
            .filter(RegistroModel.item == item_int)
            .order_by(RegistroModel.created_at.desc())
            .all()
        )
        out: list[dict] = []
        for r in regs:
            out.append(
                {
                    "id": r.id,
                    "item": r.item,
                    "quantidade": r.quantidade,
                    "motivo": r.motivo,
                    "setor_responsavel": r.setor_responsavel,
                    "usuario": r.usuario,
                    "created_at": r.created_at.isoformat(timespec="seconds"),
                }
            )
        return out

    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass

def editar_registro(registro_id: int, quantidade: Optional[int] = None, setor_responsavel: Optional[str] = None) -> bool:
    """Edita quantidade/setor de um registro, respeitando permissões:
    - ADMINISTRADOR pode editar qualquer registro
    - USUARIO só pode editar registros que ele mesmo inseriu
    Retorna True se editado, False se não encontrado ou sem permissão.
    """
    from sqlalchemy import select
    with get_session() as session:
        reg = session.get(RegistroModel, registro_id)
        if not reg:
            return False
        # Permissão: admin pode tudo, usuario só se for o autor
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        alterado = False
        if quantidade is not None:
            reg.quantidade = quantidade
            alterado = True
        if setor_responsavel is not None:
            reg.setor_responsavel = setor_responsavel
            alterado = True
        if alterado:
            session.commit()
            try:
                salvar_auditoria(transacao="Bloqueado", tipo="alteração")
            except Exception:
                pass
        return alterado


def excluir_registro(registro_id: int) -> bool:
    """Exclui um registro, respeitando permissões:
    - ADMINISTRADOR pode excluir qualquer registro
    - USUARIO só pode excluir registros que ele mesmo inseriu
    Retorna True se excluído, False se não encontrado ou sem permissão.
    """
    with get_session() as session:
        reg = session.get(RegistroModel, registro_id)
        if not reg:
            return False
        # Permissão: admin pode tudo, usuario só se for o autor
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        session.delete(reg)
        session.commit()
        try:
            salvar_auditoria(transacao="Bloqueado", tipo="alteração")
        except Exception:
            pass
        return True


def consultar_todos_registros(limit: Optional[int] = None) -> list[dict]:
    """Retorna todos os registros ordenados por created_at DESC.

    Parâmetros:
      limit: se informado, limita a quantidade de linhas retornadas (útil para evitar
              cargas muito grandes na interface). Se None, retorna todos.
    """
    with get_session() as session:
        query = session.query(RegistroModel).order_by(RegistroModel.created_at.desc())
        if limit is not None:
            query = query.limit(int(limit))
        regs = query.all()
        out: list[dict] = []
        for r in regs:
            out.append(
                {
                    "id": r.id,
                    "item": r.item,
                    "quantidade": r.quantidade,
                    "motivo": r.motivo,
                    "setor_responsavel": r.setor_responsavel,
                    "usuario": r.usuario,
                    "created_at": r.created_at.isoformat(timespec="seconds"),
                }
            )
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass


def consultar_registros_filtrados(*, data_ini: Optional[str] = None, data_fim: Optional[str] = None, motivo_sub: Optional[str] = None) -> List[dict]:
    """Consulta registros com filtros opcionais.

    Parâmetros:
      data_ini / data_fim: strings ISO (YYYY-MM-DD) limitando intervalo inclusive em created_at (UTC).
      motivo_sub: substring case-insensitive que deve estar contida em motivo.
    """
    with get_session() as session:
        query = session.query(RegistroModel)
        if data_ini:
            try:
                dt_ini = datetime.fromisoformat(data_ini)
            except ValueError:
                raise ValueError("data_ini inválida (use YYYY-MM-DD)")
            query = query.filter(RegistroModel.created_at >= dt_ini)
        if data_fim:
            try:
                # Considera final do dia (23:59:59) se só a data for passada
                dt_fim = datetime.fromisoformat(data_fim)
                if len(data_fim) == 10:
                    dt_fim = dt_fim.replace(hour=23, minute=59, second=59)
            except ValueError:
                raise ValueError("data_fim inválida (use YYYY-MM-DD)")
            query = query.filter(RegistroModel.created_at <= dt_fim)
        if motivo_sub:
            pad = f"%{motivo_sub.lower()}%"
            query = query.filter(text("lower(motivo) LIKE :pad")).params(pad=pad)
        regs = query.order_by(RegistroModel.created_at.desc()).all()
        out: List[dict] = []
        for r in regs:
            out.append({
                "id": r.id,
                "item": r.item,
                "quantidade": r.quantidade,
                "motivo": r.motivo,
                "setor_responsavel": r.setor_responsavel,
                "usuario": r.usuario,
                "created_at": r.created_at.isoformat(timespec="seconds"),
            })
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass


def consultar_monitoramento_por_campo(*, campo: str, valor: str) -> List[dict]:
    """Consulta MONITORAMENTO por um campo (onda, carga ou container).

    Regras:
    - campo deve ser um de {"onda", "carga", "container"}
    - valor: se "%%" retorna todos; caso contrário, comparação case-insensitive por igualdade.
    - Ordena por created_at DESC.
    """
    campo = (campo or "").strip().lower()
    valor = (valor or "").strip()
    if campo not in {"onda", "carga", "container"}:
        raise ValueError("Campo inválido (use onda, carga ou container)")
    with get_session() as session:
        query = session.query(MonitoramentoModel)
        if valor == "%":
            pass
        else:
            # Comparação case-insensitive: lower(col) = lower(valor)
            if campo == "onda":
                query = query.filter(text("lower(onda) = :v")).params(v=valor.lower())
            elif campo == "carga":
                query = query.filter(text("lower(carga) = :v")).params(v=valor.lower())
            else:
                query = query.filter(text("lower(container) = :v")).params(v=valor.lower())
        regs = query.order_by(MonitoramentoModel.created_at.desc()).all()
        out: List[dict] = []
        for r in regs:
            out.append({
                "id": r.id,
                "onda": r.onda,
                "carga": r.carga,
                "container": r.container,
                "responsavel": r.responsavel,
                "setor": r.setor,
                "observacao": r.observacao or "",
                "usuario": r.usuario,
                "created_at": r.created_at.isoformat(timespec="seconds"),
            })
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass


def listar_responsaveis(prefix: Optional[str] = None, limit: int = 100) -> list[str]:
    """Retorna lista de responsáveis distintos da tabela MONITORAMENTO.

    Se prefix for informado, filtra por início case-insensitive.
    """
    try:
        with get_session() as session:
            q = session.query(MonitoramentoModel.responsavel).filter(MonitoramentoModel.responsavel.isnot(None))
            # Exclui strings vazias
            q = q.filter(text("trim(responsavel) <> ''"))
            if prefix:
                pad = f"{str(prefix).strip().lower()}%"
                q = q.filter(text("lower(responsavel) LIKE :pad")).params(pad=pad)
            q = q.group_by(MonitoramentoModel.responsavel).order_by(MonitoramentoModel.responsavel.asc())
            if limit:
                q = q.limit(int(limit))
            vals = [row[0] for row in q.all() if row and row[0]]
            return vals
    except Exception:
        return []


def consultar_almoxafire(*, turno: Optional[str] = None, data_ini: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
    """Consulta a tabela ALMOXAFIRE com filtros opcionais de turno e período (created_at).

    Parâmetros:
      - turno: "1° Turno", "2° Turno" ou None para todos.
      - data_ini/data_fim: strings ISO (YYYY-MM-DD); se informadas, limitam o intervalo inclusivo.
    """
    from datetime import datetime
    dt_ini = None
    dt_fim = None
    if data_ini:
        try:
            if len(data_ini) == 10:
                dt = datetime.fromisoformat(data_ini)
                dt_ini = dt.replace(hour=0, minute=0, second=0, microsecond=0)
            else:
                dt_ini = datetime.fromisoformat(data_ini)
        except ValueError:
            raise ValueError("data_ini inválida (use YYYY-MM-DD)")
    if data_fim:
        try:
            if len(data_fim) == 10:
                dt = datetime.fromisoformat(data_fim)
                dt_fim = dt.replace(hour=23, minute=59, second=59, microsecond=999999)
            else:
                dt_fim = datetime.fromisoformat(data_fim)
        except ValueError:
            raise ValueError("data_fim inválida (use YYYY-MM-DD)")
    if dt_ini and dt_fim and dt_ini > dt_fim:
        raise ValueError("Período inválido: data inicial maior que a final")

    with get_session() as session:
        query = session.query(AlmoxafireModel)
        if turno:
            query = query.filter(AlmoxafireModel.turno == turno)
        if dt_ini:
            query = query.filter(AlmoxafireModel.created_at >= dt_ini)
        if dt_fim:
            query = query.filter(AlmoxafireModel.created_at <= dt_fim)
        regs = query.order_by(AlmoxafireModel.created_at.desc()).all()
        out: List[dict] = []
        for r in regs:
            out.append({
                "id": r.id,
                "setor": r.setor,
                "turno": r.turno,
                "matricula": r.matricula,
                "responsavel": r.responsavel,
                "insumo": r.insumo,
                "quantidade": r.quantidade,
                "observacao": r.observacao or "",
                "usuario": r.usuario,
                "created_at": r.created_at.isoformat(timespec="seconds"),
            })
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass

def consultar_epis_por_periodo(*, data_ini: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
    """Consulta EPIS (cabeçalho) por data_ref entre data_ini e data_fim (inclusive).

    Retorna lista de dicts com campos do cabeçalho e item_count (nº de itens em EPIS_ITENS).
    data_ini/data_fim: strings ISO (YYYY-MM-DD); se omitidos, não filtram a borda.
    """
    di = None
    df = None
    if data_ini:
        try:
            di = date.fromisoformat(data_ini)
        except ValueError:
            raise ValueError("data_ini inválida (use YYYY-MM-DD)")
    if data_fim:
        try:
            df = date.fromisoformat(data_fim)
        except ValueError:
            raise ValueError("data_fim inválida (use YYYY-MM-DD)")
    if di and df and di > df:
        raise ValueError("Período inválido: data inicial maior que a final")
    with get_session() as session:
        query = session.query(EpiModel)
        if di:
            query = query.filter(EpiModel.data_ref >= di)
        if df:
            query = query.filter(EpiModel.data_ref <= df)
        regs = query.order_by(EpiModel.data_ref.desc(), EpiModel.created_at.desc()).all()
        out: List[dict] = []
        for r in regs:
            try:
                cnt = session.query(EpiItemModel).filter(EpiItemModel.epi_id == r.id).count()
            except Exception:
                cnt = 0
            out.append({
                "id": r.id,
                "matricula": r.matricula,
                "setor": r.setor,
                "turno": r.turno,
                "primeira": r.primeira,
                "data_ref": r.data_ref.isoformat(),
                "responsavel": r.responsavel,
                "observacao": r.observacao or "",
                "usuario": r.usuario,
                "created_at": r.created_at.isoformat(timespec="seconds"),
                "item_count": cnt,
            })
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass

def consultar_epis_por_matricula(*, matricula: int, data_ini: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
    """Consulta EPIS por matrícula (opcionalmente limitando por período data_ref).

    Retorna campos do cabeçalho + item_count.
    """
    try:
        mat = int(matricula)
    except (TypeError, ValueError):
        raise ValueError("Matrícula inválida (use número)")
    di = None
    df = None
    if data_ini:
        try:
            di = date.fromisoformat(data_ini)
        except ValueError:
            raise ValueError("data_ini inválida (use YYYY-MM-DD)")
    if data_fim:
        try:
            df = date.fromisoformat(data_fim)
        except ValueError:
            raise ValueError("data_fim inválida (use YYYY-MM-DD)")
    if di and df and di > df:
        raise ValueError("Período inválido: data inicial maior que a final")
    with get_session() as session:
        query = session.query(EpiModel).filter(EpiModel.matricula == mat)
        if di:
            query = query.filter(EpiModel.data_ref >= di)
        if df:
            query = query.filter(EpiModel.data_ref <= df)
        regs = query.order_by(EpiModel.data_ref.desc(), EpiModel.created_at.desc()).all()
        out: List[dict] = []
        for r in regs:
            try:
                cnt = session.query(EpiItemModel).filter(EpiItemModel.epi_id == r.id).count()
            except Exception:
                cnt = 0
            out.append({
                "id": r.id,
                "matricula": r.matricula,
                "setor": r.setor,
                "turno": r.turno,
                "primeira": r.primeira,
                "data_ref": r.data_ref.isoformat(),
                "responsavel": r.responsavel,
                "observacao": r.observacao or "",
                "usuario": r.usuario,
                "created_at": r.created_at.isoformat(timespec="seconds"),
                "item_count": cnt,
            })
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consultas", tipo="consulta")
    except Exception:
        pass

def listar_itens_de_epi(epi_id: int) -> List[dict]:
    """Lista os itens de um EPI (EPIS_ITENS) por epi_id."""
    try:
        eid = int(epi_id)
    except (TypeError, ValueError):
        raise ValueError("epi_id inválido")
    with get_session() as session:
        itens = (
            session.query(EpiItemModel)
            .filter(EpiItemModel.epi_id == eid)
            .order_by(EpiItemModel.id.asc())
            .all()
        )
        out: List[dict] = []
        for it in itens:
            out.append({
                "id": it.id,
                "codigo": it.codigo,
                "produto": it.produto,
                "quantidade": it.quantidade,
                "uon": it.uon or "",
                "valor_unit": _dec_str(it.valor_unit) or "",
                "valor_total": _dec_str(it.valor_total) or "",
            })
        return out

## ---------------- Configurações API (EPIs) ---------------- ##

def listar_configuracoes_api() -> list[dict]:
    """Retorna todas as configurações (código/produto) ordenadas por código."""
    with get_session() as session:
        regs = session.query(ConfiguracaoAPIEPI).order_by(ConfiguracaoAPIEPI.codigo.asc()).all()
        return [{"codigo": r.codigo, "produto": r.produto, "valor": _dec_str(r.valor)} for r in regs]


def substituir_configuracoes_api(itens: list[dict]) -> int:
    """Substitui todo o catálogo de configurações por 'itens'.

    Cada item deve conter chaves 'codigo' e 'produto'.
    Retorna a quantidade inserida.
    """
    # Normalização e validação básica
    norm: list[tuple[str, str, Decimal | None]] = []
    for it in itens or []:
        cod = str(it.get("codigo", "")).strip()
        prod = str(it.get("produto", "")).strip()
        val = try_decimal(it.get("valor"))
        if not cod or not prod:
            # ignora linhas vazias
            continue
        norm.append((cod, prod, val))
    # Verifica duplicados
    cods = [c for c, _, __ in norm]
    if len(set(cods)) != len(cods):
        raise ValueError("Códigos duplicados não são permitidos")
    with get_session() as session:
        session.query(ConfiguracaoAPIEPI).delete()
        objs = [ConfiguracaoAPIEPI(codigo=c, produto=p, valor=v) for c, p, v in norm]
        session.add_all(objs)
        session.commit()
        return len(objs)


def upsert_configuracao_api(*, codigo: str, produto: str, valor: Decimal | None = None) -> None:
    """Insere ou atualiza uma configuração por código."""
    codigo = (codigo or "").strip()
    produto = (produto or "").strip()
    if not codigo or not produto:
        raise ValueError("Código e Produto são obrigatórios")
    with get_session() as session:
        obj = session.query(ConfiguracaoAPIEPI).filter(ConfiguracaoAPIEPI.codigo == codigo).first()
        if obj:
            obj.produto = produto
            obj.valor = valor
        else:
            session.add(ConfiguracaoAPIEPI(codigo=codigo, produto=produto, valor=valor))
        session.commit()


def excluir_configuracao_api(*, codigo: str) -> bool:
    with get_session() as session:
        obj = session.query(ConfiguracaoAPIEPI).filter(ConfiguracaoAPIEPI.codigo == codigo).first()
        if not obj:
            return False
        session.delete(obj)
        session.commit()
        return True


def obter_produto_por_codigo(*, codigo: str) -> Optional[str]:
    with get_session() as session:
        obj = session.query(ConfiguracaoAPIEPI).filter(ConfiguracaoAPIEPI.codigo == codigo).first()
        return obj.produto if obj else None

def obter_valor_por_codigo(*, codigo: str) -> Optional[Decimal]:
    with get_session() as session:
        obj = session.query(ConfiguracaoAPIEPI).filter(ConfiguracaoAPIEPI.codigo == codigo).first()
        return obj.valor if obj else None


def editar_monitoramento(monitoramento_id: int, *, responsavel: Optional[str] = None, setor: Optional[str] = None, observacao: Optional[str] = None) -> bool:
    """Edita campos de um registro de MONITORAMENTO, respeitando permissões:
    - ADMINISTRADOR pode editar qualquer registro
    - USUARIO só pode editar registros que ele mesmo inseriu
    Retorna True se alterado, False se não encontrado ou sem permissão.
    """
    with get_session() as session:
        reg = session.get(MonitoramentoModel, monitoramento_id)
        if not reg:
            return False
        # Permissão: admin pode tudo, usuario só se for o autor
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        alterado = False
        if responsavel is not None:
            novo_resp = (responsavel or "").strip().upper()
            reg.responsavel = novo_resp
            alterado = True
        if setor is not None:
            reg.setor = (setor or "").strip()
            alterado = True
        if observacao is not None:
            # aceita string vazia
            reg.observacao = observacao
            alterado = True
        if alterado:
            session.commit()
            try:
                salvar_auditoria(transacao="Monitoramento", tipo="alteração")
            except Exception:
                pass
        return alterado


def excluir_monitoramento(monitoramento_id: int) -> bool:
    """Exclui um registro de MONITORAMENTO, respeitando permissões:
    - ADMINISTRADOR pode excluir qualquer registro
    - USUARIO só pode excluir registros que ele mesmo inseriu
    Retorna True se excluído, False se não encontrado ou sem permissão.
    """
    with get_session() as session:
        reg = session.get(MonitoramentoModel, monitoramento_id)
        if not reg:
            return False
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        session.delete(reg)
        session.commit()
        try:
            salvar_auditoria(transacao="Monitoramento", tipo="alteração")
        except Exception:
            pass
        return True


def editar_almoxafire(
    almox_id: int,
    *,
    setor: Optional[str] = None,
    turno: Optional[str] = None,
    matricula: Optional[int] = None,
    responsavel: Optional[str] = None,
    insumo: Optional[str] = None,
    quantidade: Optional[int] = None,
    observacao: Optional[str] = None,
) -> bool:
    """Edita campos de um registro de ALMOXAFIRE, respeitando permissões:
    - ADMINISTRADOR pode editar qualquer registro
    - USUARIO só pode editar registros que ele mesmo inseriu
    Retorna True se alterado, False se não encontrado ou sem permissão.
    """
    with get_session() as session:
        reg = session.get(AlmoxafireModel, almox_id)
        if not reg:
            return False
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        alterado = False
        if setor is not None:
            reg.setor = (setor or "").strip().upper()
            alterado = True
        if turno is not None:
            reg.turno = (turno or "").strip()
            alterado = True
        if matricula is not None:
            try:
                reg.matricula = int(matricula)
            except (TypeError, ValueError):
                raise ValueError("Matrícula inválida")
            alterado = True
        if responsavel is not None:
            reg.responsavel = (responsavel or "").strip().upper()
            alterado = True
        if insumo is not None:
            reg.insumo = (insumo or "").strip()
            alterado = True
        if quantidade is not None:
            try:
                q = int(quantidade)
            except (TypeError, ValueError):
                raise ValueError("Quantidade inválida")
            if q <= 0:
                raise ValueError("Quantidade deve ser > 0")
            reg.quantidade = q
            alterado = True
        if observacao is not None:
            obs_norm = observacao.strip().upper() if observacao.strip() != "" else None
            reg.observacao = obs_norm
            alterado = True
        if alterado:
            session.commit()
            try:
                salvar_auditoria(transacao="Almoxarifado", tipo="alteração")
            except Exception:
                pass
        return alterado


def excluir_almoxafire(almox_id: int) -> bool:
    """Exclui um registro de ALMOXAFIRE, respeitando permissões.
    - ADMINISTRADOR pode excluir qualquer registro
    - USUARIO só pode excluir registros que ele mesmo inseriu
    Retorna True se excluído, False caso contrário.
    """
    with get_session() as session:
        reg = session.get(AlmoxafireModel, almox_id)
        if not reg:
            return False
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        session.delete(reg)
        session.commit()
        try:
            salvar_auditoria(transacao="Almoxarifado", tipo="alteração")
        except Exception:
            pass
        return True


def excluir_epi(epi_id: int) -> bool:
    """Exclui um registro de EPIS (cabeçalho e itens em cascata).
    - ADMINISTRADOR pode excluir qualquer registro
    - USUARIO só pode excluir registros que ele mesmo inseriu
    Retorna True se excluído, False caso contrário.
    """
    with get_session() as session:
        reg = session.get(EpiModel, epi_id)
        if not reg:
            return False
        if _CurrentUser.tipo != "ADMINISTRADOR":
            if reg.usuario != _CurrentUser.username:
                return False
        session.delete(reg)
        session.commit()
        try:
            salvar_auditoria(transacao="EPIs", tipo="alteração")
        except Exception:
            pass
        return True


# ---------------- Consolidado ---------------- #
# Removidos métodos de JSON consolidado.


def salvar_consolidado_linhas(*, data_ref: date, linhas: list[dict]) -> int:
    """Insere as linhas do consolidado para a data fornecida.

    Retorna quantidade de linhas inseridas.
    """
    with get_session() as session:
        objs: list[ConsolidadoLinhaModel] = []
        for r in linhas:
            obj = ConsolidadoLinhaModel(
                data_ref=data_ref,
                arm_=try_int(r.get("arm.")),
                descricao_filial=(r.get("Descrição Filial") or None),
                r_estoque=try_decimal(r.get("R$ Estoque")),
                qtd_item_mix=try_int(r.get("Qtde Item Mix")),
                qtd_item_com_estoque=try_int(r.get("Qtde Item com Estoque")),
                qtd_item_sem_estoque=try_int(r.get("Qtde Item sem Estoque")),
                r_bloq_total=try_decimal(r.get("R$ Bloq. Total")),
                r_bloq_no_estoque=try_decimal(r.get("R$ Bloq. no ESTOQUE")),
                r_bloq_em_negoc=try_decimal(r.get("R$ Bloq. em Negoc.")),
                r_bloq_saldo=try_decimal(r.get("R$ Bloq. SALDO")),
                pct_item_com_estoque=try_decimal(r.get("% Item com Estoque")),
            )
            objs.append(obj)
        session.add_all(objs)
        session.commit()
        return len(objs)


def substituir_consolidado_linhas_por_data(*, data_ref: date, linhas: list[dict]) -> int:
    """Apaga linhas da data e insere as novas; retorna quantidade inserida."""
    with get_session() as session:
        session.query(ConsolidadoLinhaModel).filter(ConsolidadoLinhaModel.data_ref == data_ref).delete()
        return salvar_consolidado_linhas(data_ref=data_ref, linhas=linhas)


def existe_consolidado_linhas_na_data(*, data_ref: date) -> bool:
    """Retorna True se existir pelo menos uma linha de consolidado para a data."""
    with get_session() as session:
        return (
            session.query(ConsolidadoLinhaModel.id)
            .filter(ConsolidadoLinhaModel.data_ref == data_ref)
            .first()
            is not None
        )


def consultar_consolidado_por_periodo(*, data_ini: Optional[str] = None, data_fim: Optional[str] = None) -> List[dict]:
    """Retorna linhas do CONSOLIDADO entre data_ini e data_fim (inclusive).

    data_ini/data_fim: strings ISO YYYY-MM-DD; se omitidos, não filtram a borda.
    """
    with get_session() as session:
        query = session.query(ConsolidadoLinhaModel)
        if data_ini:
            try:
                di = date.fromisoformat(data_ini)
            except ValueError:
                raise ValueError("data_ini inválida (use YYYY-MM-DD)")
            query = query.filter(ConsolidadoLinhaModel.data_ref >= di)
        if data_fim:
            try:
                df = date.fromisoformat(data_fim)
            except ValueError:
                raise ValueError("data_fim inválida (use YYYY-MM-DD)")
            query = query.filter(ConsolidadoLinhaModel.data_ref <= df)
        regs = (
            query.order_by(ConsolidadoLinhaModel.data_ref.desc(), ConsolidadoLinhaModel.descricao_filial.asc())
            .all()
        )
        out: List[dict] = []
        for r in regs:
            out.append({
                "data_ref": r.data_ref.isoformat(),
                "arm.": r.arm_,
                "Descrição Filial": r.descricao_filial,
                "R$ Estoque": _dec_str(r.r_estoque),
                "Qtde Item Mix": r.qtd_item_mix,
                "Qtde Item com Estoque": r.qtd_item_com_estoque,
                "Qtde Item sem Estoque": r.qtd_item_sem_estoque,
                "R$ Bloq. Total": _dec_str(r.r_bloq_total),
                "R$ Bloq. no ESTOQUE": _dec_str(r.r_bloq_no_estoque),
                "R$ Bloq. em Negoc.": _dec_str(r.r_bloq_em_negoc),
                "R$ Bloq. SALDO": _dec_str(r.r_bloq_saldo),
                "% Item com Estoque": _dec_str(r.pct_item_com_estoque),
            })
        return out
    # Auditoria de consulta
    try:
        salvar_auditoria(transacao="Consolidado", tipo="consulta")
    except Exception:
        pass


def _dec_str(val: Decimal | None) -> str | None:
    if val is None:
        return None
    # Representação simples com duas casas (ou 4 para porcentagem) fica à cargo do consumidor
    return f"{val}"


def try_int(val) -> int | None:
    try:
        if val is None or val == "":
            return None
        return int(str(val).replace(".", "").replace(",", ""))
    except Exception:
        return None


def try_decimal(val) -> Decimal | None:
    try:
        if val is None or val == "":
            return None
        if isinstance(val, (int, float, Decimal)):
            return Decimal(str(val))
        s = str(val).strip()
        # Remove símbolo de moeda e espaços
        s = s.replace("R$", "").replace("\u00A0", " ").strip()
        s = s.replace(" ", "")
        # Se contém vírgula e ponto, decide qual é decimal pelo último separador
        if "," in s and "." in s:
            if s.rfind(",") > s.rfind("."):
                # Formato 1.234,56 -> vírgula é decimal
                s = s.replace(".", "")
                s = s.replace(",", ".")
            else:
                # Formato 1,234.56 -> ponto é decimal
                s = s.replace(",", "")
                # mantém o ponto
        elif "," in s:
            # Apenas vírgula: tratar como decimal
            s = s.replace(".", "")  # quaisquer pontos seriam milhar
            s = s.replace(",", ".")
        else:
            # Apenas ponto (ou nenhum): considerar ponto como decimal
            # Não remover o ponto aqui
            pass
        return Decimal(s)
    except Exception:
        return None


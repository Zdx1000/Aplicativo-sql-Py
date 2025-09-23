from __future__ import annotations

from pathlib import Path
from datetime import datetime, timedelta
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QTabWidget,
    QFrame,
    QFileDialog,
    QWidget,
    QGraphicsDropShadowEffect,
)


def _resource_path(rel_path: str) -> str:
    import sys
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base) / rel_path)
    return str(Path(__file__).resolve().parent / rel_path)


def _get_app_icon():
    from PySide6.QtGui import QIcon
    for c in ("assets/app_icon.ico", "assets/app_icon.png", "assets/app_icon.svg"):
        p = Path(_resource_path(c))
        if p.exists():
            return QIcon(str(p))
    return QIcon()


class PerfilDialog(QDialog):
    """Painel de Perfil do usuário atual, com visão geral e atividade."""

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Perfil do Usuário")
        self.setWindowIcon(_get_app_icon())
        self.resize(920, 640)
        self._build()
        self._apply_style()
        self._carregar_dados()

    # ---------- UI ---------- #
    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(14, 14, 14, 14)
        root.setSpacing(10)

        # Hero com avatar e dados básicos
        hero = QFrame()
        hero.setObjectName("Hero")
        hl = QHBoxLayout(hero)
        hl.setContentsMargins(18, 16, 18, 16)
        hl.setSpacing(16)

        # Avatar (inicial do usuário)
        self.avatar = QLabel()
        self.avatar.setObjectName("Avatar")
        self.avatar.setFixedSize(72, 72)
        self.avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Nome + papel + últimas datas
        name_box = QVBoxLayout()
        self.lab_nome = QLabel("USUARIO")
        self.lab_nome.setObjectName("PerfilNome")
        self.lab_nome.setWordWrap(True)
        self.lab_papel = QLabel("USUARIO")
        self.lab_papel.setObjectName("PerfilPapel")
        self.lab_ultima_atividade = QLabel("Última atividade: -")
        self.lab_ultima_atividade.setObjectName("PerfilMeta")
        self.lab_primeira_atividade = QLabel("Primeiro registro: -")
        self.lab_primeira_atividade.setObjectName("PerfilMeta")
        name_box.addWidget(self.lab_nome)
        name_box.addWidget(self.lab_papel)
        name_box.addWidget(self.lab_ultima_atividade)
        name_box.addWidget(self.lab_primeira_atividade)

        hl.addWidget(self.avatar, 0, Qt.AlignmentFlag.AlignTop)
        hl.addLayout(name_box, 1)

        # Totais (cards) - um cartão grande + 4 médios
        cards_wrap = QGridLayout()
        cards_wrap.setHorizontalSpacing(12)
        cards_wrap.setVerticalSpacing(12)

        self.card_total = self._card("Total de ações", "0", accent="#0D47A1")
        self.card_input = self._card("Inputs", "0", icon="📥", accent="#1565C0")
        self.card_output = self._card("Outputs", "0", icon="📤", accent="#00897B")
        self.card_alt = self._card("Alterações", "0", icon="✏️", accent="#8E24AA")
        self.card_cons = self._card("Consultas", "0", icon="🔎", accent="#EF6C00")

        cards_wrap.addWidget(self.card_total["wrap"], 0, 0, 2, 1)
        cards_wrap.addWidget(self.card_input["wrap"], 0, 1)
        cards_wrap.addWidget(self.card_output["wrap"], 0, 2)
        cards_wrap.addWidget(self.card_alt["wrap"], 1, 1)
        cards_wrap.addWidget(self.card_cons["wrap"], 1, 2)

        hl.addLayout(cards_wrap, 2)
        root.addWidget(hero)

        # Abas: Visão Geral | Atividade
        tabs = QTabWidget()
        self.tabs = tabs

        # Aba Visão Geral
        tab_overview = QWidget()
        ov = QVBoxLayout(tab_overview)
        ov.setSpacing(8)
        ov.setContentsMargins(6, 6, 6, 6)
        ov.addWidget(self._section_title("Ranking por seção"))
        ranks_row = QHBoxLayout()
        self.tab_rank_inputs = self._mk_table(["Seção", "Inputs"], object_name="RankInputs")
        self.tab_rank_consultas = self._mk_table(["Seção", "Consultas"], object_name="RankConsultas")
        ranks_row.addWidget(self.tab_rank_inputs, 1)
        ranks_row.addWidget(self.tab_rank_consultas, 1)
        ov.addLayout(ranks_row)
        tabs.addTab(tab_overview, "Visão Geral")

        # Aba Atividade
        tab_activity = QWidget()
        ac = QVBoxLayout(tab_activity)
        ac.setSpacing(8)
        ac.setContentsMargins(6, 6, 6, 6)
        ac.addWidget(self._section_title("Últimos eventos"))
        self.tab_logs = self._mk_table(["Data/Hora", "Tipo", "Seção"], object_name="UltimosLogs")
        ac.addWidget(self.tab_logs)
        ac.addWidget(self._section_title("Atividade nos últimos 30 dias"))
        self.tab_dias = self._mk_table(["Data", "Total", "Inputs", "Consultas", "Alterações", "Outputs"], object_name="AtividadeDias")
        ac.addWidget(self.tab_dias)
        tabs.addTab(tab_activity, "Atividade")

        root.addWidget(tabs, 1)

        # Ações
        row = QHBoxLayout()
        row.addStretch(1)
        self.btn_export = QPushButton("Exportar Auditoria…")
        self.btn_refresh = QPushButton("Atualizar")
        self.btn_close = QPushButton("Fechar")
        self.btn_export.clicked.connect(self._exportar_auditoria_usuario)
        self.btn_refresh.clicked.connect(self._carregar_dados)
        self.btn_close.clicked.connect(self.accept)
        row.addWidget(self.btn_export)
        row.addWidget(self.btn_refresh)
        row.addWidget(self.btn_close)
        root.addLayout(row)

    def _apply_style(self) -> None:
        # QSS local com foco em tipografia, cartões e tabelas
        self.setStyleSheet(
            """
            QDialog { background: #f5f7fb; }
            #Hero { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #e3f2fd, stop:1 #e8eaf6); border:1px solid #d3deea; border-radius:12px; }
            #Avatar { background:#1565C0; color:#ffffff; border-radius:36px; font: 700 28px 'Segoe UI'; }
            #PerfilNome { font: 700 22px 'Segoe UI'; color:#0D47A1; }
            #PerfilPapel { font: 600 12px 'Segoe UI'; color:#455A64; background:#E3F2FD; border:1px solid #bbdefb; border-radius:10px; padding:3px 8px; width:fit-content; }
            #PerfilMeta { color:#546E7A; }

            /* Cards */
            QFrame[role='card'] { background:#ffffff; border:1px solid #dfe7ef; border-radius:12px; }
            QLabel[role='card-title'] { color:#546E7A; font: 600 12px 'Segoe UI'; }
            QLabel[role='card-value'] { color:#0D47A1; font: 800 28px 'Segoe UI'; }
            QLabel[role='card-icon'] { font: 20px 'Segoe UI Emoji'; }

            /* Títulos de seção */
            QLabel#SectionTitle { color:#263238; font: 700 14px 'Segoe UI'; padding: 2px 4px; }

            /* Tabelas */
            QTableWidget { background:#ffffff; border:1px solid #dfe7ef; border-radius:10px; gridline-color:#cfd8dc; }
            QHeaderView::section { background:#1976D2; color:#ffffff; padding:6px 8px; border:none; font-weight:600; }
            QTableWidget::item { padding: 2px 4px; }
            """
        )

    def _section_title(self, text: str) -> QLabel:
        lab = QLabel(text)
        lab.setObjectName("SectionTitle")
        return lab

    def _mk_table(self, headers: list[str], object_name: str = "") -> QTableWidget:
        tab = QTableWidget(0, len(headers))
        if object_name:
            tab.setObjectName(object_name)
        tab.setHorizontalHeaderLabels(headers)
        hdr = tab.horizontalHeader()
        hdr.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        hdr.setStretchLastSection(True)
        tab.setAlternatingRowColors(True)
        tab.setSortingEnabled(True)
        return tab

    def _card(self, titulo: str, valor: str, icon: str = "", accent: str = "#1976D2") -> dict:
        wrap = QFrame()
        wrap.setProperty("role", "card")
        lay = QVBoxLayout(wrap)
        lay.setContentsMargins(14, 10, 14, 12)
        lay.setSpacing(4)
        title = QLabel(titulo)
        title.setProperty("role", "card-title")
        value = QLabel(valor)
        value.setProperty("role", "card-value")
        if icon:
            ic = QLabel(icon)
            ic.setProperty("role", "card-icon")
            ic.setStyleSheet(f"color:{accent}")
            head = QHBoxLayout()
            head.addWidget(ic)
            head.addWidget(title)
            head.addStretch(1)
            lay.addLayout(head)
        else:
            lay.addWidget(title)
        # Destaque na borda esquerda
        wrap.setStyleSheet(f"QFrame[role='card']{{ border-left: 4px solid {accent}; }}")
        lay.addWidget(value)
        # Sombra sutil
        try:
            shadow = QGraphicsDropShadowEffect(wrap)
            shadow.setBlurRadius(14)
            shadow.setOffset(0, 2)
            shadow.setColor(QColor(0, 0, 0, 45))
            wrap.setGraphicsEffect(shadow)
        except Exception:
            pass
        return {"wrap": wrap, "title": title, "value": value}

    # ---------- Dados ---------- #
    def _carregar_dados(self) -> None:
        try:
            from sqlalchemy import func
            from database import get_session, AuditLogModel, obter_usuario_atual, obter_tipo_usuario_atual
            usuario = obter_usuario_atual() or None
            papel = obter_tipo_usuario_atual() or "USUARIO"
            if not usuario:
                self._set_basics("USUARIO", papel, None, None)
                self._set_totais({})
                self._fill_table(self.tab_rank_inputs, [])
                self._fill_table(self.tab_rank_consultas, [])
                self._fill_table(self.tab_logs, [])
                self._fill_table(self.tab_dias, [])
                return
            with get_session() as s:
                # Nome/Avatar
                self._set_basics(usuario.upper(), papel, s, usuario)

                # Totais por tipo
                rows = (
                    s.query(AuditLogModel.tipo, func.count(AuditLogModel.id))
                    .filter(AuditLogModel.usuario == usuario)
                    .group_by(AuditLogModel.tipo)
                    .all()
                )
                mapa = {str(t): int(c) for t, c in rows}
                self._set_totais(mapa)

                # Ranking Inputs (top 10)
                rank_in = (
                    s.query(AuditLogModel.transacao, func.count(AuditLogModel.id))
                    .filter(AuditLogModel.usuario == usuario, AuditLogModel.tipo == "input")
                    .group_by(AuditLogModel.transacao)
                    .order_by(func.count(AuditLogModel.id).desc())
                    .limit(10)
                    .all()
                )
                self._fill_table(self.tab_rank_inputs, [(t, int(c)) for t, c in rank_in])

                # Ranking Consultas (top 10)
                rank_co = (
                    s.query(AuditLogModel.transacao, func.count(AuditLogModel.id))
                    .filter(AuditLogModel.usuario == usuario, AuditLogModel.tipo == "consulta")
                    .group_by(AuditLogModel.transacao)
                    .order_by(func.count(AuditLogModel.id).desc())
                    .limit(10)
                    .all()
                )
                self._fill_table(self.tab_rank_consultas, [(t, int(c)) for t, c in rank_co])

                # Últimos eventos (20)
                logs = (
                    s.query(AuditLogModel.created_at, AuditLogModel.tipo, AuditLogModel.transacao)
                    .filter(AuditLogModel.usuario == usuario)
                    .order_by(AuditLogModel.created_at.desc())
                    .limit(20)
                    .all()
                )
                self._fill_table(self.tab_logs, [
                    (dt.strftime("%Y-%m-%d %H:%M:%S"), tp, tr) for dt, tp, tr in logs
                ])

                # Atividade por dia (últimos 30 dias)
                inicio = datetime.utcnow().date() - timedelta(days=29)
                # Agrupa por dia e tipo
                rows_dia = (
                    s.query(func.date(AuditLogModel.created_at), AuditLogModel.tipo, func.count(AuditLogModel.id))
                    .filter(AuditLogModel.usuario == usuario, AuditLogModel.created_at >= inicio)
                    .group_by(func.date(AuditLogModel.created_at), AuditLogModel.tipo)
                    .all()
                )
                # Constrói dicionário {dia: {tipo: count}}
                mapa_dia: dict[str, dict[str, int]] = {}
                for d, tp, cnt in rows_dia:
                    dia = str(d)
                    mapa_dia.setdefault(dia, {})[str(tp)] = int(cnt)
                # Linhas ordenadas por dia asc
                linhas = []
                for i in range(30):
                    dia = (inicio + timedelta(days=i)).strftime("%Y-%m-%d")
                    t_in = mapa_dia.get(dia, {}).get("input", 0)
                    t_co = mapa_dia.get(dia, {}).get("consulta", 0)
                    t_al = mapa_dia.get(dia, {}).get("alteração", 0)
                    t_ou = mapa_dia.get(dia, {}).get("output", 0)
                    total = t_in + t_co + t_al + t_ou
                    linhas.append((dia, total, t_in, t_co, t_al, t_ou))
                self._fill_table(self.tab_dias, linhas)
        except Exception:
            # Se algo falhar, evita quebrar a UI
            self._set_totais({})
            self._fill_table(self.tab_rank_inputs, [])
            self._fill_table(self.tab_rank_consultas, [])
            self._fill_table(self.tab_logs, [])
            self._fill_table(self.tab_dias, [])

    def _set_basics(self, username_up: str, papel: str, session=None, usuario: str | None = None) -> None:
        # Avatar: primeira letra
        letra = (username_up or "?").strip()[:1]
        self.avatar.setText(letra)
        self.lab_nome.setText(f"{username_up}")
        self.lab_papel.setText(papel.upper())
        # Última/primeira atividade
        try:
            if session and usuario:
                from database import AuditLogModel
                ult = (
                    session.query(AuditLogModel.created_at)
                    .filter(AuditLogModel.usuario == usuario)
                    .order_by(AuditLogModel.created_at.desc())
                    .first()
                )
                pri = (
                    session.query(AuditLogModel.created_at)
                    .filter(AuditLogModel.usuario == usuario)
                    .order_by(AuditLogModel.created_at.asc())
                    .first()
                )
                self.lab_ultima_atividade.setText(
                    f"Última atividade: {ult[0].strftime('%Y-%m-%d %H:%M:%S')}" if ult else "Última atividade: -"
                )
                self.lab_primeira_atividade.setText(
                    f"Primeiro registro: {pri[0].strftime('%Y-%m-%d %H:%M:%S')}" if pri else "Primeiro registro: -"
                )
            else:
                self.lab_ultima_atividade.setText("Última atividade: -")
                self.lab_primeira_atividade.setText("Primeiro registro: -")
        except Exception:
            self.lab_ultima_atividade.setText("Última atividade: -")
            self.lab_primeira_atividade.setText("Primeiro registro: -")

    def _set_totais(self, mapa: dict[str, int]) -> None:
        v_in = int(mapa.get("input", 0))
        v_ou = int(mapa.get("output", 0))
        v_al = int(mapa.get("alteração", 0))
        v_co = int(mapa.get("consulta", 0))
        total = v_in + v_ou + v_al + v_co
        self.card_total["value"].setText(str(total))
        self.card_input["value"].setText(str(v_in))
        self.card_output["value"].setText(str(v_ou))
        self.card_alt["value"].setText(str(v_al))
        self.card_cons["value"].setText(str(v_co))

    def _fill_table(self, tab: QTableWidget, rows: list[tuple]) -> None:
        tab.setSortingEnabled(False)
        tab.clearContents()
        tab.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem()
                # Usa DisplayRole para ints
                if isinstance(val, int):
                    try:
                        item.setData(Qt.ItemDataRole.DisplayRole, int(val))
                    except Exception:
                        item.setText(str(val))
                else:
                    item.setText("" if val is None else str(val))
                tab.setItem(r, c, item)
        tab.setSortingEnabled(True)

    # ---------- Exportação ---------- #
    def _exportar_auditoria_usuario(self) -> None:
        try:
            from database import get_session, AuditLogModel, obter_usuario_atual
            usuario = obter_usuario_atual() or None
            if not usuario:
                return
            path, _ = QFileDialog.getSaveFileName(self, "Exportar auditoria do usuário", f"auditoria_{usuario}.csv", "CSV (*.csv)")
            if not path:
                return
            with get_session() as s:
                rows = (
                    s.query(AuditLogModel.created_at, AuditLogModel.tipo, AuditLogModel.transacao)
                    .filter(AuditLogModel.usuario == usuario)
                    .order_by(AuditLogModel.created_at.desc())
                    .limit(2000)
                    .all()
                )
            import csv
            with open(path, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter=';')
                w.writerow(["data_hora", "tipo", "secao"]) 
                for dt, tp, tr in rows:
                    w.writerow([dt.strftime("%Y-%m-%d %H:%M:%S"), tp, tr])
        except Exception:
            # Silencia erros de exportação
            pass

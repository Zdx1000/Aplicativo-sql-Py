from __future__ import annotations

from typing import Optional, List
from datetime import datetime

from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QPushButton,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)

from style import QSS_HEADER_BLOQUEADO


class RegistrosPage(QWidget):
    """Página para exibir os 10 últimos registros de auditoria do sistema.

    Colunas:
      - USUÁRIO: quem executou
      - TRANSAÇÃO: seção/feature (Bloqueado, Consultas, Grafico, Almoxarifado, EPIs, Consolidado)
      - DATA: data local (Brasília)
      - HORA: horário local (Brasília)
      - TIPO: input | output | consulta | alteração
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PaginaRegistros")
        self._build()
        # refresh inicial
        self._carregar()

    def _build(self) -> None:
        root = QVBoxLayout(self)

        # Cabeçalho (padrão compartilhado com EPIs/Monitoramento/Bloqueado)
        head_frame = QFrame()
        head_frame.setObjectName("HeaderBloqueado")
        head_layout = QHBoxLayout(head_frame)
        head_layout.setContentsMargins(8, 0, 8, 6)
        head_layout.setSpacing(2)

        titulo_wrap = QFrame()
        titulo_wrap.setObjectName("TituloWrap")
        wrap_layout = QHBoxLayout(titulo_wrap)
        wrap_layout.setContentsMargins(16, 2, 16, 2)
        wrap_layout.setSpacing(8)

        line_left = QFrame()
        line_left.setObjectName("DecorLine")
        line_left.setFrameShape(QFrame.Shape.HLine)
        line_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        lab_titulo = QLabel("Registros")
        lab_titulo.setObjectName("TituloBloqueado")

        line_right = QFrame()
        line_right.setObjectName("DecorLine")
        line_right.setFrameShape(QFrame.Shape.HLine)
        line_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        wrap_layout.addWidget(line_left)

        titulo_container = QWidget()
        titulo_layout = QHBoxLayout(titulo_container)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo_layout.setSpacing(8)

        icone = QLabel("🗂️")
        icone.setObjectName("IconeBloqueado")
        icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_layout.addWidget(icone)
        titulo_layout.addWidget(lab_titulo)

        wrap_layout.addWidget(titulo_container)
        wrap_layout.addWidget(line_right)
        head_layout.addWidget(titulo_wrap, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        try:
            _title_shadow = QGraphicsDropShadowEffect(self)
            _title_shadow.setBlurRadius(20)
            _title_shadow.setOffset(0, 2)
            lab_titulo.setGraphicsEffect(_title_shadow)
        except Exception:
            pass

        head_layout.addStretch(1)
        self.btn_refresh = QPushButton("↻ Atualizar")
        self.btn_refresh.setObjectName("RefreshButton")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setToolTip("Recarregar últimos registros")
        self.btn_refresh.setMinimumHeight(34)
        try:
            _btn_shadow = QGraphicsDropShadowEffect(self)
            _btn_shadow.setBlurRadius(14)
            _btn_shadow.setOffset(0, 2)
            self.btn_refresh.setGraphicsEffect(_btn_shadow)
        except Exception:
            pass
        # Estilo visual do botão (verde elegante)
        try:
            self.btn_refresh.setStyleSheet(
                """
                QPushButton#RefreshButton {
                    background-color: #198754; /* verde bootstrap */
                    color: #ffffff;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    font-weight: 600;
                }
                QPushButton#RefreshButton:hover {
                    background-color: #157347;
                }
                QPushButton#RefreshButton:pressed {
                    background-color: #146c43;
                }
                """
            )
        except Exception:
            pass
        self.btn_refresh.clicked.connect(self._carregar)
        head_layout.addWidget(self.btn_refresh, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        head_frame.setMaximumHeight(116)

        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            head_frame.setGraphicsEffect(shadow)
        except Exception:
            pass
        try:
            head_frame.setStyleSheet("border-radius: 10px;")
            titulo_wrap.setStyleSheet("border-radius: 10px;")
        except Exception:
            pass

        root.addWidget(head_frame)
        if QSS_HEADER_BLOQUEADO:
            self.setStyleSheet(self.styleSheet() + QSS_HEADER_BLOQUEADO)

        # Tabela
        self.tab = QTableWidget(0, 5)
        self.tab.setObjectName("TabelaRegistros")
        self.tab.setHorizontalHeaderLabels(["USUÁRIO", "TRANSAÇÃO", "DATA", "HORA", "TIPO"])
        # Visual e comportamento
        try:
            from PySide6.QtWidgets import QHeaderView
            hdr = self.tab.horizontalHeader()
            hdr.setStretchLastSection(False)
            hdr.setSectionResizeMode(QHeaderView.ResizeToContents)
            # USUÁRIO e TRANSAÇÃO ocupam o espaço
            hdr.setSectionResizeMode(0, QHeaderView.Stretch)
            hdr.setSectionResizeMode(1, QHeaderView.Stretch)
            # DATA, HORA e TIPO ajustam ao conteúdo
            hdr.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            hdr.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            hdr.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        except Exception:
            pass
        self.tab.setAlternatingRowColors(True)
        self.tab.setSelectionBehavior(self.tab.SelectionBehavior.SelectRows)
        self.tab.setSelectionMode(self.tab.SelectionMode.SingleSelection)
        self.tab.setShowGrid(True)
        self.tab.setSortingEnabled(False)
        self.tab.verticalHeader().setVisible(False)
        self.tab.setStyleSheet(self._qss_tabela())
        root.addWidget(self.tab, 1)

    def _carregar(self) -> None:
        """Carrega os 10 últimos registros e popula a tabela."""
        try:
            from database import listar_auditoria
            limit = self._calc_visible_limit()
            linhas = listar_auditoria(limit=limit) or []
        except Exception:
            linhas = []
        # Limpa
        self.tab.setRowCount(0)
        for r in linhas:
            i = self.tab.rowCount()
            self.tab.insertRow(i)
            usuario = r.get("usuario", "") or "-"
            trans = r.get("transacao", "-")
            tipo = (r.get("tipo", "-") or "-").lower()
            # Converter created_at ISO (UTC) para horário de Brasília
            data_loc, hora_loc = self._to_brazil_time(r.get("created_at"))
            it_user = QTableWidgetItem(usuario)
            it_trans = QTableWidgetItem(trans)
            it_data = QTableWidgetItem(data_loc)
            it_hora = QTableWidgetItem(hora_loc)
            it_tipo = QTableWidgetItem(self._format_tipo(tipo))
            # Alinhamentos
            it_user.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            it_trans.setTextAlignment(Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft)
            it_data.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_hora.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            it_tipo.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
            # Destaque do tipo com cor de fundo
            self._apply_tipo_style(it_tipo, tipo)
            # Tooltips com timestamp original
            ts_iso = r.get("created_at") or ""
            it_data.setToolTip(ts_iso)
            it_hora.setToolTip(ts_iso)
            self.tab.setItem(i, 0, it_user)
            self.tab.setItem(i, 1, it_trans)
            self.tab.setItem(i, 2, it_data)
            self.tab.setItem(i, 3, it_hora)
            self.tab.setItem(i, 4, it_tipo)

    def _calc_visible_limit(self) -> int:
        """Estimativa do máximo de linhas que cabem na viewport da tabela."""
        try:
            vp_h = int(self.tab.viewport().height())
            row_h = int(self.tab.verticalHeader().defaultSectionSize())
            if row_h <= 0:
                # tenta usar a altura da primeira linha ou um padrão razoável
                row_h = int(self.tab.rowHeight(0)) if self.tab.rowCount() > 0 else 28
            if vp_h <= 0 or row_h <= 0:
                return 10
            # Reserva pequena margem para header/scroll, adiciona +1 de folga
            capacidade = max(1, (vp_h // row_h) + 1)
            return capacidade
        except Exception:
            return 10

    def _to_brazil_time(self, created_at_iso: Optional[str]) -> tuple[str, str]:
        """Converte ISO (UTC) para data e hora em America/Sao_Paulo.

        Se timezone não estiver disponível, aplica offset fixo -03:00 como fallback.
        """
        if not created_at_iso:
            return ("-", "-")
        try:
            # Preferir zoneinfo (Python 3.9+)
            try:
                from zoneinfo import ZoneInfo  # type: ignore
                tz_br = ZoneInfo("America/Sao_Paulo")
                dt_utc = datetime.fromisoformat(created_at_iso)
                if dt_utc.tzinfo is None:
                    from datetime import timezone
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                dt_br = dt_utc.astimezone(tz_br)
            except Exception:
                # Fallback: aplicar -3 horas (desconsidera horário de verão)
                from datetime import timedelta, timezone
                dt_utc = datetime.fromisoformat(created_at_iso)
                if dt_utc.tzinfo is None:
                    dt_utc = dt_utc.replace(tzinfo=timezone.utc)
                dt_br = dt_utc + timedelta(hours=-3)
            return (dt_br.strftime("%d/%m/%Y"), dt_br.strftime("%H:%M:%S"))
        except Exception:
            return ("-", "-")

    # ---------- Helpers de estilo/rotulagem ---------- #
    def _format_tipo(self, tipo: str) -> str:
        m = {
            "input": "⬇ INPUT",
            "output": "⬆ OUTPUT",
            "consulta": "🔍 CONSULTA",
            "alteração": "✏ ALTERAÇÃO",
            "alteracao": "✏ ALTERAÇÃO",
        }
        return m.get(tipo.lower(), tipo.upper())

    def _apply_tipo_style(self, item: QTableWidgetItem, tipo: str) -> None:
        try:
            from PySide6.QtGui import QColor
        except Exception:
            return
        cor_bg = QColor("#6c757d")  # padrão (consulta/cinza)
        cor_fg = QColor("#ffffff")
        t = tipo.lower()
        if t == "input":
            cor_bg = QColor("#0d6efd")  # azul
        elif t == "output":
            cor_bg = QColor("#20c997")  # teal
        elif t in ("alteração", "alteracao"):
            cor_bg = QColor("#fd7e14")  # laranja
        elif t == "consulta":
            cor_bg = QColor("#6f42c1")  # roxo
        item.setForeground(cor_fg)
        item.setBackground(cor_bg)
        f = item.font()
        f.setBold(True)
        item.setFont(f)

    def _qss_tabela(self) -> str:
        # QSS leve para header e zebra
        return (
            """
            #TabelaRegistros { gridline-color: #bdbdbd; }
            #TabelaRegistros::item { padding: 6px; }
            #TabelaRegistros QHeaderView::section {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #001d2e, stop:1 #001724);
                color: #ffffff;
                padding: 6px 8px;
                border: 1px solid #002336;
                font-weight: 600;
            }
            """
        )

from __future__ import annotations

from typing import Dict, List, Optional

from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QColor, QBrush, QPen
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
)
try:
    from PySide6.QtCharts import QChart, QChartView, QPieSeries
    HAS_QTCHARTS = True
except Exception:  # Fallback quando PySide6-Addons (QtCharts) não está instalado
    HAS_QTCHARTS = False
    QChart = QChartView = QPieSeries = None  # type: ignore


class GraficoPage(QWidget):
    """Página de gráficos com filtro por período e agrupamento.

    - Filtro: Data inicial e final (obrigatórios), formato yyyy-MM-dd
    - Agrupar por (X): Motivo | Setor | Usuário
    - Métrica (Y): Soma de Quantidade (padrão e única por requisito)
    - Gráfico: Pizza (QPieSeries)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PaginaGrafico")
        self._build()

    # ---------------- UI ---------------- #
    def _build(self) -> None:
        lay = QVBoxLayout(self)
        lay.setContentsMargins(32, 24, 32, 24)
        lay.setSpacing(16)

        # Filtros
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        self.ed_data_ini = QDateEdit()
        self.ed_data_ini.setDisplayFormat("yyyy-MM-dd")
        self.ed_data_ini.setCalendarPopup(True)
        # Default: primeiro dia do mês corrente
        hoje = QDate.currentDate()
        self.ed_data_ini.setDate(QDate(hoje.year(), hoje.month(), 1))

        self.ed_data_fim = QDateEdit()
        self.ed_data_fim.setDisplayFormat("yyyy-MM-dd")
        self.ed_data_fim.setCalendarPopup(True)
        self.ed_data_fim.setDate(hoje)

        row_ini = QHBoxLayout()
        row_ini.addWidget(self.ed_data_ini)
        row_fim = QHBoxLayout()
        row_fim.addWidget(self.ed_data_fim)

        wrap_ini = QWidget(); wrap_ini.setLayout(row_ini)
        wrap_fim = QWidget(); wrap_fim.setLayout(row_fim)

        self.cb_agrup = QComboBox()
        self.cb_agrup.addItems(["Motivo", "Setor", "Usuário"])  # Dimensão (X)

        # Métrica (Y)
        self.cb_metric = QComboBox()
        self.cb_metric.addItems([
            "Soma de Quantidade",
            "Média de Quantidade",
            "Contagem de Registros",
            "Contagem Única de Item",
            "Contagem Única de Usuário",
            "Contagem Única de Motivo",
            "Contagem Única de Setor",
        ])

        self.btn_atualizar = QPushButton("Atualizar")
        self.btn_atualizar.clicked.connect(self._on_update)

        form.addRow("Data inicial:", wrap_ini)
        form.addRow("Data final:", wrap_fim)
        form.addRow("Agrupar por:", self.cb_agrup)
        form.addRow("Métrica:", self.cb_metric)

        top_actions = QHBoxLayout()
        top_actions.addStretch(1)
        top_actions.addWidget(self.btn_atualizar)

        lay.addLayout(form)
        lay.addLayout(top_actions)

        # Chart (ou aviso caso QtCharts não esteja disponível)
        if HAS_QTCHARTS:
            self.chart = QChart()
            self.chart.legend().setAlignment(Qt.AlignRight)
            self.chart.setAnimationOptions(QChart.SeriesAnimations)
            self.chart.setTitle("Distribuição por categoria (Quantidade)")

            self.chart_view = QChartView(self.chart)
            self.chart_view.setRenderHint(self.chart_view.renderHints())
            lay.addWidget(self.chart_view, 1)
            # Aplica tema inicial (claro por padrão; será atualizado pelo MainWindow se necessário)
            try:
                self.aplicar_tema("claro")
            except Exception:
                pass
        else:
            warn = QLabel(
                "Gráfico indisponível: instale o pacote 'PySide6-Addons' para habilitar QtCharts."
            )
            warn.setWordWrap(True)
            lay.addWidget(warn)

        # Mensagem de status
        self.lab_status = QLabel("")
        self.lab_status.setObjectName("GraficoStatusLabel")
        lay.addWidget(self.lab_status)

        # Carrega inicial
        self._on_update()

    # ---------------- Lógica ---------------- #
    def _on_update(self) -> None:
        if self.ed_data_ini.date() > self.ed_data_fim.date():
            self.lab_status.setText("Data inicial não pode ser maior que a final.")
            return
        data_ini = self.ed_data_ini.date().toString("yyyy-MM-dd")
        data_fim = self.ed_data_fim.date().toString("yyyy-MM-dd")
        agrup = self.cb_agrup.currentText()
        metric = self.cb_metric.currentText()
        self._last_agrup = agrup
        self._last_metric = metric

        try:
            from database import consultar_registros_filtrados
            regs = consultar_registros_filtrados(data_ini=data_ini, data_fim=data_fim, motivo_sub=None)
        except Exception as exc:
            self.lab_status.setText(f"Erro ao consultar: {exc}")
            self._render_pie([])
            return

        # Agregar por agrup
        chaves = {
            "Motivo": "motivo",
            "Setor": "setor_responsavel",
            "Usuário": "usuario",
        }
        key = chaves.get(agrup, "motivo")
        valores: Dict[str, float] = {}
        # Suporte a média: manter soma e contagem
        somas: Dict[str, float] = {}
        conts: Dict[str, int] = {}
        # Suporte a contagem distinta
        sets_distintos: Dict[str, set] = {}

        unique_fields = {
            "Contagem Única de Item": "item",
            "Contagem Única de Usuário": "usuario",
            "Contagem Única de Motivo": "motivo",
            "Contagem Única de Setor": "setor_responsavel",
        }

        for r in regs or []:
            cat = r.get(key) or "(vazio)"
            if metric == "Soma de Quantidade":
                try:
                    q = float(int(r.get("quantidade", 0)))
                except Exception:
                    q = 0.0
                valores[cat] = valores.get(cat, 0.0) + q
            elif metric == "Média de Quantidade":
                try:
                    q = float(int(r.get("quantidade", 0)))
                except Exception:
                    q = 0.0
                somas[cat] = somas.get(cat, 0.0) + q
                conts[cat] = conts.get(cat, 0) + 1
            elif metric == "Contagem de Registros":
                valores[cat] = valores.get(cat, 0.0) + 1.0
            elif metric in unique_fields:
                fld = unique_fields[metric]
                sets = sets_distintos.setdefault(cat, set())
                sets.add(r.get(fld))

        if metric == "Média de Quantidade":
            for cat, soma_val in somas.items():
                c = conts.get(cat, 0)
                valores[cat] = (soma_val / c) if c else 0.0
        elif metric in unique_fields:
            for cat, s in sets_distintos.items():
                valores[cat] = float(len(s))

        # Ordena por valor desc e limita a 15 fatias (resto = Outros)
        itens = sorted(valores.items(), key=lambda kv: kv[1], reverse=True)
        max_slices = 15
        outros_val = sum(v for _, v in itens[max_slices:])
        itens = itens[:max_slices]
        if outros_val > 0:
            itens.append(("Outros", outros_val))

        self._render_pie(itens)
        total = sum(v for _, v in itens)
        self.lab_status.setText(
            f"{len(regs)} registro(s) no período. Total: {total:.2f} ({metric})."
        )

    def _render_pie(self, itens: List[tuple[str, float]]) -> None:
        if not HAS_QTCHARTS:
            return
        # Limpa séries antigas
        for s in list(self.chart.series()):
            self.chart.removeSeries(s)

        series = QPieSeries()
        for nome, valor in itens:
            if valor <= 0:
                continue
            # Formata label (inteiro quando possível)
            label_val = int(valor) if abs(valor - int(valor)) < 1e-6 else round(float(valor), 2)
            slice_ = series.append(f"{nome} ({label_val})", float(valor))
            if nome == "Outros":
                slice_.setColor(QColor("#c9c9c9"))
            slice_.setLabelVisible(True)

        if series.slices():
            self.chart.addSeries(series)
            agrup = getattr(self, "_last_agrup", "Dimensão")
            metric = getattr(self, "_last_metric", "Métrica")
            self.chart.setTitle(f"{metric} por {agrup}")
        else:
            self.chart.setTitle("Sem dados para o período/agrupamento")

        self.chart.legend().setVisible(True)
        self.chart.legend().setAlignment(Qt.AlignRight)

    # ---------------- Tema do gráfico ---------------- #
    def aplicar_tema(self, modo: str) -> None:
        """Aplica tema 'claro' ou 'escuro' ao chart, alinhado com o estilo global.

        - Usa ChartThemeLight/Dark quando disponível e reforça cores de fundo/título/legenda.
        - Ajusta cor dos rótulos das fatias da pizza.
        """
        if not HAS_QTCHARTS:
            return
        escuro = (str(modo).lower() == "escuro")
        try:
            self.chart.setTheme(QChart.ChartThemeDark if escuro else QChart.ChartThemeLight)
        except Exception:
            pass
        # Cores alinhadas ao style.py
        bg = QColor(30, 34, 40) if escuro else QColor(255, 255, 252)
        plot_bg = QColor(40, 44, 52) if escuro else QColor(255, 255, 255)
        fg = QColor(255, 255, 255) if escuro else QColor(10, 10, 10)

        # Fundo do chart e área de plotagem
        try:
            self.chart.setBackgroundVisible(True)
            self.chart.setBackgroundBrush(QBrush(bg))
            self.chart.setPlotAreaBackgroundVisible(True)
            self.chart.setPlotAreaBackgroundBrush(QBrush(plot_bg))
        except Exception:
            pass
        # Título e legenda
        try:
            self.chart.setTitleBrush(fg)
            lg = self.chart.legend()
            if hasattr(lg, "setLabelColor"):
                lg.setLabelColor(fg)
        except Exception:
            pass
        # Ajusta rótulos das séries atuais
        try:
            for s in self.chart.series():
                if hasattr(s, "slices"):
                    for sl in s.slices():
                        if hasattr(sl, "setLabelColor"):
                            sl.setLabelColor(fg)
                        # Bordas discretas nas fatias em escuro
                        if escuro and hasattr(sl, "setPen"):
                            sl.setPen(QPen(QColor(70, 74, 84)))
        except Exception:
            pass

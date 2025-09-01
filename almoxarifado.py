from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt, QRegularExpression
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator, QColor
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QFormLayout,
    QComboBox,
    QLineEdit,
    QTextEdit,
    QPushButton,
    QLabel,
    QHBoxLayout,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QMessageBox,
)

try:
    # Estilos compartilhados (se existir)
    from style import QSS_FORMULARIO_BASE, QSS_HEADER_BLOQUEADO
except Exception:
    QSS_FORMULARIO_BASE = ""
    QSS_HEADER_BLOQUEADO = ""

try:
    from config import SETORES as SETORES_GLOBAIS
except Exception:
    SETORES_GLOBAIS = None


class AlmoxarifadoPage(QWidget):
    """Página de requisição de insumos (Almoxarifado).

    Campos:
      - Setor: opções predefinidas
      - Turno: 1° Turno, 2° Turno
      - Responsável solicitante: texto
      - Insumo: {"Fita", "Copo", "Caneta"}
      - Quantidade: inteiro > 0

    Ao clicar em Inserir, valida e imprime no console (stdout) o registro capturado.
    """

    INSUMOS = ["Fita", "Copo", "Caneta"]
    TURNOS = ["1° Turno", "2° Turno"]

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PaginaAlmoxarifado")
        self._build()

    def _build(self) -> None:
        self.setMinimumWidth(520)
        root = QVBoxLayout(self)

        # Cabeçalho estilo Bloqueado/Monitoramento
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

        lab_titulo = QLabel("ALMOXARIFADO")
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

        icone = QLabel("🏢")
        icone.setObjectName("IconeBloqueado")
        icone.setAlignment(Qt.AlignCenter)
        titulo_layout.addWidget(icone)
        titulo_layout.addWidget(lab_titulo)

        wrap_layout.addWidget(titulo_container)
        wrap_layout.addWidget(line_right)
        head_layout.addWidget(titulo_wrap, 0, Qt.AlignLeft | Qt.AlignVCenter)

        try:
            _title_shadow = QGraphicsDropShadowEffect(self)
            _title_shadow.setBlurRadius(20)
            _title_shadow.setOffset(0, 2)
            lab_titulo.setGraphicsEffect(_title_shadow)
        except Exception:
            pass

        head_layout.addStretch(1)
        self.btn_help = QPushButton("❓ Ajuda")
        self.btn_help.setObjectName("HelpBloqueado")
        self.btn_help.setCursor(Qt.PointingHandCursor)
        self.btn_help.setToolTip("Ajuda sobre a seção Almoxarifado")
        self.btn_help.clicked.connect(self._mostrar_ajuda)
        head_layout.addWidget(self.btn_help, 0, Qt.AlignRight | Qt.AlignTop)
        # Limita altura do cabeçalho para não ocupar muito espaço vertical
        head_frame.setMaximumHeight(116)

        # Sombra sutil no cabeçalho
        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 60))
            head_frame.setGraphicsEffect(shadow)
        except Exception:
            pass

        # Bordas arredondadas no cabeçalho e no container do título
        try:
            head_frame.setStyleSheet("border-radius: 10px;")
            titulo_wrap.setStyleSheet("border-radius: 10px;")
        except Exception:
            pass

        root.addWidget(head_frame)

        # Aplica QSS do header, se disponível
        if QSS_HEADER_BLOQUEADO:
            self.setStyleSheet(self.styleSheet() + QSS_HEADER_BLOQUEADO)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignRight)

        # Setor
        self.cb_setor = QComboBox()
        self.cb_setor.addItem("-- Selecione --", "")
        try:
            itens = list(SETORES_GLOBAIS) if SETORES_GLOBAIS else self.SETORES
            self.cb_setor.addItems(itens)
        except Exception:
            self.cb_setor.addItems(self.SETORES)
        form.addRow("Setor:", self.cb_setor)

        # Turno
        self.cb_turno = QComboBox()
        self.cb_turno.addItem("-- Selecione --", "")
        self.cb_turno.addItems(self.TURNOS)
        form.addRow("Turno:", self.cb_turno)

        # Matrícula do responsável (inteiro) - acima do Responsável
        self.ed_matricula = QLineEdit()
        self.ed_matricula.setValidator(QIntValidator(1, 99_999_999, self))
        self.ed_matricula.setPlaceholderText("Número de matrícula")
        form.addRow("Matrícula:", self.ed_matricula)

        # Responsável solicitante (apenas letras e espaços)
        self.ed_resp = QLineEdit()
        only_text_regex = QRegularExpression(r"^[\p{L} ]+$")  # letras unicode e espaço
        self.ed_resp.setValidator(QRegularExpressionValidator(only_text_regex, self))
        self.ed_resp.setPlaceholderText("Nome do responsável solicitante (Primeiro nome)")
        # Força o texto para maiúsculas quando terminar de editar
        self.ed_resp.editingFinished.connect(self._upper_responsavel)
        form.addRow("Responsável:", self.ed_resp)

        # Insumo
        self.cb_insumo = QComboBox()
        self.cb_insumo.addItem("-- Selecione --", "")
        self.cb_insumo.addItems(self.INSUMOS)
        form.addRow("Insumo:", self.cb_insumo)

        # Quantidade
        self.ed_qtd = QLineEdit()
        self.ed_qtd.setValidator(QIntValidator(1, 1_000_000, self))
        self.ed_qtd.setPlaceholderText("Quantidade")
        form.addRow("Quantidade:", self.ed_qtd)

        # Observação (opcional) - área de texto ampla
        self.ed_obs = QTextEdit()
        self.ed_obs.setPlaceholderText("Observação (opcional)")
        self.ed_obs.setAcceptRichText(False)
        self.ed_obs.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.ed_obs.setMinimumHeight(100)
        self.ed_obs.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.ed_obs.setTabChangesFocus(True)
        form.addRow("Observação:", self.ed_obs)

        # Botões
        row_btn = QHBoxLayout()
        row_btn.addStretch(1)
        self.btn_inserir = QPushButton("Inserir")
        self.btn_inserir.setObjectName("Primary")
        self.btn_inserir.clicked.connect(self._on_inserir)
        row_btn.addWidget(self.btn_inserir)

        # Feedback
        self.feedback = QLabel()
        self.feedback.setObjectName("feedbackLabel")
        self.feedback.setVisible(False)

        root.addLayout(form)
        root.addWidget(self.feedback)
        root.addLayout(row_btn)

        # Aplicar estilo base se disponível
        if QSS_FORMULARIO_BASE:
            self.setStyleSheet(self.styleSheet() + QSS_FORMULARIO_BASE)

    def _validar(self) -> Optional[str]:
        if self.cb_setor.currentIndex() <= 0:
            return "Selecione um Setor."
        if self.cb_turno.currentIndex() <= 0:
            return "Selecione um Turno."
        if not self.ed_matricula.text().strip():
            return "Informe a Matrícula."
        try:
            mat = int(self.ed_matricula.text())
            if mat <= 0:
                return "Matrícula deve ser maior que zero."
        except ValueError:
            return "Matrícula inválida."
        if not self.ed_resp.text().strip():
            return "Informe o Responsável."
        if self.cb_insumo.currentIndex() <= 0:
            return "Selecione um Insumo."
        if not self.ed_qtd.text().strip():
            return "Informe a Quantidade."
        try:
            qtd = int(self.ed_qtd.text())
            if qtd <= 0:
                return "Quantidade deve ser maior que zero."
        except ValueError:
            return "Quantidade inválida."
        return None

    def _on_inserir(self) -> None:
        erro = self._validar()
        if erro:
            self._show_feedback(erro, erro=True)
            return
        registro = {
            "setor": self.cb_setor.currentText(),
            "turno": self.cb_turno.currentText(),
            "matricula": int(self.ed_matricula.text()),
            "responsavel": self.ed_resp.text().strip().upper(),
            "insumo": self.cb_insumo.currentText(),
            "quantidade": int(self.ed_qtd.text()),
            "observacao": self.ed_obs.toPlainText().strip(),
        }
        # Persistir no banco
        try:
            from database import salvar_almoxafire
            novo_id = salvar_almoxafire(**registro)
            self._show_feedback("Solicitação registrada no banco.", erro=False)
        except Exception as e:
            self._show_feedback(f"Erro ao salvar: {e}", erro=True)
            return
        # Limpa campos
        self.cb_setor.setCurrentIndex(0)
        self.cb_turno.setCurrentIndex(0)
        self.ed_matricula.clear()
        self.ed_resp.clear()
        self.cb_insumo.setCurrentIndex(0)
        self.ed_qtd.clear()
        self.ed_obs.clear()
        self.cb_setor.setFocus()

    def _upper_responsavel(self) -> None:
        try:
            self.ed_resp.setText(self.ed_resp.text().upper())
        except Exception:
            pass

    def _show_feedback(self, msg: str, erro: bool) -> None:
        self.feedback.setProperty("erro", "true" if erro else "false")
        self.feedback.setText(msg)
        self.feedback.setVisible(True)
        self.feedback.style().unpolish(self.feedback)
        self.feedback.style().polish(self.feedback)

    def _mostrar_ajuda(self) -> None:
        QMessageBox.information(
            self,
            "Ajuda - Almoxarifado",
            (
                "Preencha Setor, Turno, Matrícula do responsável, Responsável, Insumo e Quantidade.\n"
                "Clique em Inserir para registrar (no momento a saída é exibida no console)."
            ),
        )

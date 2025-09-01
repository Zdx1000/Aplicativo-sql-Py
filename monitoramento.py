from __future__ import annotations

from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QColor, QIcon
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLineEdit,
    QTextEdit,
    QComboBox,
    QPushButton,
    QLabel,
    QMessageBox,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)
from style import QSS_HEADER_BLOQUEADO
try:
    from config import SETORES as SETORES_GLOBAIS
except Exception:
    SETORES_GLOBAIS = None


class MonitoramentoPage(QWidget):
    """Tela de Monitoramento (Reimpressão de Etiquetas).

    Campos:
    - Onda, Carga, Container
    - Responsável solicitante
    - Observação com lista de motivos (Etiqueta sumida, Etiqueta danificada, Outros)
    - Setor
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PaginaMonitoramento")
        self._build()

    def _build(self) -> None:
        self.setWindowTitle("Monitoramento")
        # Base visual igual à página Bloqueado
        self.setMinimumWidth(520)
        self.setWindowIcon(QIcon())  # Placeholder (poderá ser substituído futuramente)
        root = QVBoxLayout(self)


        # Cabeçalho no mesmo estilo do Bloqueado
        head_frame = QFrame()
        head_frame.setObjectName("HeaderBloqueado")
        head_layout = QHBoxLayout(head_frame)


        titulo_wrap = QFrame()
        titulo_wrap.setObjectName("TituloWrap")
        wrap_layout = QHBoxLayout(titulo_wrap)
        wrap_layout.setContentsMargins(28, 6, 28, 6)
        wrap_layout.setSpacing(14)
        line_left = QFrame()
        line_left.setObjectName("DecorLine")
        line_left.setFrameShape(QFrame.Shape.HLine)
        line_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lab_titulo = QLabel("REIMPRESSÃO DE ETIQUETAS")
        lab_titulo.setObjectName("TituloBloqueado")
        line_right = QFrame()
        line_right.setObjectName("DecorLine")
        line_right.setFrameShape(QFrame.Shape.HLine)
        line_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        wrap_layout.addWidget(line_left)

        # Ícone antes do título
        titulo_container = QWidget()
        titulo_layout = QHBoxLayout(titulo_container)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo_layout.setSpacing(8)
        icone = QLabel("📋")
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
            _title_shadow.setColor(QColor(0, 0, 0, 70))
            lab_titulo.setGraphicsEffect(_title_shadow)
        except Exception:
            pass
        head_layout.addStretch(1)
        # Botão de ajuda (mesmo padrão da página Bloqueado)
        self.btn_help_mon = QPushButton("❓ Ajuda")
        # Usa o mesmo objectName do Bloqueado para herdar o QSS existente
        self.btn_help_mon.setObjectName("HelpBloqueado")
        self.btn_help_mon.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_help_mon.setToolTip("Ajuda sobre a seção Monitoramento")
        self.btn_help_mon.clicked.connect(self._mostrar_ajuda_monitoramento)
        head_layout.addWidget(self.btn_help_mon, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)

        # Sombra sutil no cabeçalho
        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 60))
            head_frame.setGraphicsEffect(shadow)
        except Exception:
            pass

        root.addWidget(head_frame)
        # Aplica QSS de header igual ao Bloqueado
        self.setStyleSheet(self.styleSheet() + QSS_HEADER_BLOQUEADO)

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setSpacing(10)

        # Onda, Carga e Container lado a lado, com rótulos acima
        self.ed_onda = QLineEdit()
        self.ed_onda.setPlaceholderText("Ex: 45633")
        self.ed_onda.setValidator(QIntValidator(0, 2_147_483_647, self))

        self.ed_carga = QLineEdit()
        self.ed_carga.setPlaceholderText("Ex: 20906")
        self.ed_carga.setValidator(QIntValidator(0, 2_147_483_647, self))

        self.ed_container = QLineEdit()
        self.ed_container.setPlaceholderText("Ex: 7108078")
        self.ed_container.setValidator(QIntValidator(0, 2_147_483_647, self))
        linha_topo = QHBoxLayout()
        linha_topo.setSpacing(8)
        # Coluna Onda
        col_onda = QVBoxLayout()
        col_onda.setSpacing(2)
        lab_onda = QLabel("Onda")
        col_onda.addWidget(lab_onda)
        col_onda.addWidget(self.ed_onda)
        # Coluna Carga
        col_carga = QVBoxLayout()
        col_carga.setSpacing(2)
        lab_carga = QLabel("Carga")
        col_carga.addWidget(lab_carga)
        col_carga.addWidget(self.ed_carga)
        # Coluna Container
        col_cont = QVBoxLayout()
        col_cont.setSpacing(2)
        lab_cont = QLabel("Container")
        col_cont.addWidget(lab_cont)
        col_cont.addWidget(self.ed_container)
        # Adiciona colunas com pesos iguais
        linha_topo.addLayout(col_onda, 1)
        linha_topo.addLayout(col_carga, 1)
        linha_topo.addLayout(col_cont, 1)
        w_topo = QWidget()
        w_topo.setLayout(linha_topo)
        # Linha única sem rótulo do lado esquerdo
        form.addRow("", w_topo)

        from PySide6.QtWidgets import QCompleter
        self.ed_responsavel = QLineEdit()
        self.ed_responsavel.setPlaceholderText("Nome de quem solicitou")
        # Autocomplete baseado nos responsáveis já cadastrados no banco
        try:
            from database import listar_responsaveis
            self._responsavel_completer = QCompleter([], self)
            self._responsavel_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self._responsavel_completer.setFilterMode(Qt.MatchStartsWith)
            self.ed_responsavel.setCompleter(self._responsavel_completer)
            # Carrega iniciais
            self._atualizar_completer_responsavel("")
            # Atualiza sugestões enquanto digita
            self.ed_responsavel.textEdited.connect(self._atualizar_completer_responsavel)
        except Exception:
            pass
        form.addRow("Responsável:", self.ed_responsavel)

        # Observação: combobox + texto (como Bloqueado)
        self.cb_motivo = QComboBox()
        motivos = [
            "-- Selecione --",
            "Etiqueta sumida",
            "Etiqueta danificada",
            "Fora do procedimento",
            "Outros",
        ]
        self.cb_motivo.addItems(motivos)
        self.ed_obs = QTextEdit()
        self.ed_obs.setPlaceholderText("Selecione um motivo ou 'Outros' para digitar...")
        self.ed_obs.setAcceptRichText(False)
        self.ed_obs.setTabChangesFocus(True)
        self.ed_obs.setEnabled(False)
        wrap_obs = QVBoxLayout()
        wrap_obs.setSpacing(4)
        wrap_obs_widget = QWidget()
        wrap_obs_widget.setLayout(wrap_obs)
        wrap_obs.addWidget(self.cb_motivo)
        wrap_obs.addWidget(self.ed_obs)
        form.addRow("Observação:", wrap_obs_widget)
        self.cb_motivo.currentIndexChanged.connect(self._on_motivo_changed)

        self.cb_setor = QComboBox()
        self.cb_setor.addItem("-- Selecione --", "")
        try:
            itens = list(SETORES_GLOBAIS) if SETORES_GLOBAIS else self.SETORES_PADRAO
            self.cb_setor.addItems(itens)
        except Exception:
            self.cb_setor.addItems(self.SETORES_PADRAO)
        form.addRow("Setor:", self.cb_setor)

        row_btns = QHBoxLayout()
        row_btns.addStretch(1)
        self.btn_inserir = QPushButton("Inserir")
        # Estilo: fundo azul e texto branco
        self.btn_inserir.setStyleSheet(
            "QPushButton{background-color:#0078D7;color:#ffffff;border:1px solid #0063B1;padding:6px 14px;border-radius:6px;}"
            "QPushButton:hover{background-color:#0a84ff;}"
            "QPushButton:pressed{background-color:#0063B1;}"
        )
        self.btn_inserir.clicked.connect(self._on_inserir)
        row_btns.addWidget(self.btn_inserir)

        self.lab_feedback = QLabel()
        self.lab_feedback.setObjectName("FeedbackMonitoramento")
        self.lab_feedback.setVisible(False)

        root.addLayout(form)
        root.addWidget(self.lab_feedback)
        root.addLayout(row_btns)

    def _mostrar_ajuda_monitoramento(self) -> None:
        mensagem = (
            "Seção Monitoramento:\n\n"
            "Use esta tela para registrar solicitações de monitoramento.\n"
            "Campos:\n"
            "- Onda: identificação da onda.\n"
            "- Carga / Container: códigos conforme operação (lado a lado).\n"
            "- Responsável solicitante: quem solicitou.\n"
            "- Setor: selecione na lista.\n"
            "- Observação: campo opcional para detalhes adicionais.\n\n"
            "Ao clicar em Inserir, os dados são exibidos no console por enquanto."
        )
        try:
            QMessageBox.information(self, "Ajuda - Monitoramento", mensagem)
        except Exception:
            pass

    # --- Lógica --- #
    def _validar(self) -> Optional[str]:
        if not self.ed_onda.text().strip():
            return "Onda é obrigatória."
        if not self.ed_carga.text().strip():
            return "Carga é obrigatória."
        if not self.ed_container.text().strip():
            return "Container é obrigatório."
        if not self.ed_responsavel.text().strip():
            return "Responsável solicitante é obrigatório."
        if self.cb_setor.currentIndex() <= 0:
            return "Selecione um Setor."
        # Validação do motivo/observação como no Bloqueado
        idx_mot = self.cb_motivo.currentIndex()
        texto_mot = self.ed_obs.toPlainText().strip()
        if idx_mot <= 0:
            return "Observação é obrigatória (selecione ou escolha 'Outros')."
        rotulo_sel = self.cb_motivo.currentText()
        if rotulo_sel == "Outros" and not texto_mot:
            return "Digite a observação em 'Outros'."
        if rotulo_sel != "Outros" and not texto_mot:
            return "Observação inválida."
        return None

    def _on_inserir(self) -> None:
        erro = self._validar()
        if erro:
            self._feedback(erro, erro_flag=True)
            return
        dados = {
            "onda": self.ed_onda.text().strip(),
            "carga": self.ed_carga.text().strip(),
            "container": self.ed_container.text().strip(),
            "responsavel": self.ed_responsavel.text().strip(),
            "setor": self.cb_setor.currentText().strip(),
            "observacao": self.ed_obs.toPlainText().strip(),
        }
        # Persistência no banco
        try:
            from database import salvar_monitoramento
            novo_id = salvar_monitoramento(**dados)
            self._feedback(f"Registro de monitoramento #{novo_id} inserido.", erro_flag=False)
        except Exception as exc:
            self._feedback(f"Falha ao salvar monitoramento: {exc}", erro_flag=True)
            return
    # Limpa campos após inserir
        self.ed_onda.clear()
        self.ed_carga.clear()
        self.ed_container.clear()
        self.ed_responsavel.clear()
        self.cb_setor.setCurrentIndex(0)
        self.cb_motivo.setCurrentIndex(0)
        self.ed_obs.clear()
        self.ed_obs.setEnabled(False)
        # Atualiza sugestões de responsável
        try:
            self._atualizar_completer_responsavel("")
        except Exception:
            pass

    def _on_motivo_changed(self) -> None:
        idx = self.cb_motivo.currentIndex()
        texto = self.cb_motivo.currentText()
        if idx <= 0:
            self.ed_obs.clear()
            self.ed_obs.setEnabled(False)
        elif texto == "Outros":
            self.ed_obs.clear()
            self.ed_obs.setEnabled(True)
            self.ed_obs.setFocus()
        elif texto == "Fora do procedimento":
            # Confirmação especial para motivo não autorizado
            try:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Atenção")
                msg.setText("Esta Reimpressão não é um tipo autorizado. Você concorda com este procedimento?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
                btn_yes = msg.button(QMessageBox.Yes)
                btn_no = msg.button(QMessageBox.No)
                btn_yes.setText("Concordar")
                btn_no.setText("Discordar")
                resp = msg.exec()
                if resp == QMessageBox.No:
                    # Reverter seleção e não adicionar motivo
                    self.cb_motivo.setCurrentIndex(0)
                    return
            except Exception:
                # Fallback silencioso: se der erro no diálogo, trata como discordar
                self.cb_motivo.setCurrentIndex(0)
                return
            # Concordou: preencher e bloquear edição
            self.ed_obs.setEnabled(False)
            self.ed_obs.setPlainText(texto)
        else:
            # Preenche e bloqueia edição
            self.ed_obs.setEnabled(False)
            self.ed_obs.setPlainText(texto)

    def _feedback(self, msg: str, erro_flag: bool) -> None:
        self.lab_feedback.setText(msg)
        self.lab_feedback.setProperty("erro", "true" if erro_flag else "false")
        self.lab_feedback.setVisible(True)
        self.lab_feedback.style().unpolish(self.lab_feedback)
        self.lab_feedback.style().polish(self.lab_feedback)

    # --- Autocomplete Responsável ---
    def _atualizar_completer_responsavel(self, prefix: str) -> None:
        try:
            from database import listar_responsaveis
            vals = listar_responsaveis(prefix=prefix, limit=50)
            if hasattr(self, "_responsavel_completer") and self._responsavel_completer:
                self._responsavel_completer.model().setStringList(vals)  # type: ignore[attr-defined]
        except Exception:
            pass

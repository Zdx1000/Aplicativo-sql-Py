from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict
import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QIntValidator, QIcon, QColor
from PySide6.QtWidgets import (
    QWidget,
    QFormLayout,
    QLineEdit,
    QComboBox,
    QTextEdit,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QMessageBox,
    QLabel,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
    QDialog,
)

from style import (
    build_palette_claro,
    QSS_HEADER_BLOQUEADO,
    QSS_FORMULARIO_BASE,
)

from config import SETORES as SETORES_GLOBAIS


# Utilitário local (evita import circular com servidor.py)
def _resource_path(rel_path: str) -> str:
    base = getattr(sys, "_MEIPASS", None)
    if base:
        return str(Path(base) / rel_path)
    return str(Path(__file__).resolve().parent / rel_path)


def _get_app_icon() -> QIcon:
    for c in ("assets/app_icon.ico", "assets/app_icon.png", "assets/app_icon.svg"):
        p = Path(_resource_path(c))
        if p.exists():
            return QIcon(str(p))
    return QIcon()


@dataclass(slots=True)
class Registro:
    item: int
    quantidade: int
    motivo: str
    setor_responsavel: str
    matricula: int
    data_mov: str | None = None  # YYYY-MM-DD


class ExportDialog(QDialog):
    """Diálogo para escolher filtros de exportação e formato."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Exportar Registros")
        self.setWindowIcon(_get_app_icon())
        self._build()

    def _build(self) -> None:
        from PySide6.QtWidgets import QDateEdit, QCheckBox
        from PySide6.QtCore import QDate
        lay = QVBoxLayout(self)
        form = QFormLayout()
        # Datas com calendário (opcionais via checkbox)
        self.chk_data_ini = QCheckBox("Usar")
        self.ed_data_ini = QDateEdit()
        self.ed_data_ini.setDisplayFormat("yyyy-MM-dd")
        self.ed_data_ini.setCalendarPopup(True)
        self.ed_data_ini.setDate(QDate.currentDate())
        self.ed_data_ini.setEnabled(False)
        row_ini = QHBoxLayout()
        row_ini.addWidget(self.chk_data_ini)
        row_ini.addWidget(self.ed_data_ini, 1)
        self.chk_data_ini.toggled.connect(self.ed_data_ini.setEnabled)
        self.chk_data_fim = QCheckBox("Usar")
        self.ed_data_fim = QDateEdit()
        self.ed_data_fim.setDisplayFormat("yyyy-MM-dd")
        self.ed_data_fim.setCalendarPopup(True)
        self.ed_data_fim.setDate(QDate.currentDate())
        self.ed_data_fim.setEnabled(False)
        row_fim = QHBoxLayout()
        row_fim.addWidget(self.chk_data_fim)
        row_fim.addWidget(self.ed_data_fim, 1)
        self.chk_data_fim.toggled.connect(self.ed_data_fim.setEnabled)
        # Motivo via lista ("Outros" = Todos)
        self.cb_motivo = QComboBox()
        motivos: list = [
            "Armazenamento inadequado",
            "Armazenamento fora do sistema",
            "Movimentação apenas fisica",
            "Movimentação apenas sistemica",
            "Não movimentado do Box de recebimento",
            "Perca do produto pós recebimento",
            "Produto com avaria",
            "Expedição irregular",
            "Entrada do inventário",
            "Outros",
        ]
        self.cb_motivo.addItems(motivos)
        # Formato
        self.cb_formato = QComboBox()
        self.cb_formato.addItems(["csv", "xlsx", "txt"])
        # Monta formulário
        form.addRow("Data inicial:", self._wrap_row(row_ini))
        form.addRow("Data final:", self._wrap_row(row_fim))
        form.addRow("Motivo:", self.cb_motivo)
        form.addRow("Formato:", self.cb_formato)
        lay.addLayout(form)
        row_btn = QHBoxLayout()
        btn_cancel = QPushButton("Cancelar")
        btn_ok = QPushButton("Exportar")
        btn_cancel.clicked.connect(self.reject)
        btn_ok.clicked.connect(self._confirmar)
        row_btn.addStretch(1)
        row_btn.addWidget(btn_cancel)
        row_btn.addWidget(btn_ok)
        lay.addLayout(row_btn)
        self.resize(360, 200)

    def _wrap_row(self, layout: QHBoxLayout) -> QWidget:
        w = QWidget()
        w.setLayout(layout)
        return w

    def _confirmar(self) -> None:
        # Se ambas datas estiverem ativas, garantir ordem válida
        if getattr(self, "chk_data_ini", None) and getattr(self, "chk_data_fim", None):
            if self.chk_data_ini.isChecked() and self.chk_data_fim.isChecked():
                if self.ed_data_ini.date() > self.ed_data_fim.date():
                    QMessageBox.warning(self, "Aviso", "Data inicial não pode ser maior que a final.")
                    return
        self.accept()

    def get_params(self) -> dict:
        fmt_date = "yyyy-MM-dd"
        data_ini = None
        data_fim = None
        if getattr(self, "chk_data_ini", None) and self.chk_data_ini.isChecked():
            data_ini = self.ed_data_ini.date().toString(fmt_date)
        if getattr(self, "chk_data_fim", None) and self.chk_data_fim.isChecked():
            data_fim = self.ed_data_fim.date().toString(fmt_date)
        mot = self.cb_motivo.currentText() if hasattr(self, "cb_motivo") else None
        # "Outros" = sem filtro (todos)
        if mot == "Outros":
            mot = None
        return {
            "data_ini": data_ini,
            "data_fim": data_fim,
            "motivo": mot,
            "formato": self.cb_formato.currentText(),
        }


class BloqueadoPage(QWidget):
    """Página Bloqueado extraída de servidor.py"""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PaginaBloqueado")
        self._build_ui()

    def _build_ui(self) -> None:
        self.setWindowTitle("Cadastro de Itens")
        self.setMinimumWidth(520)

        # Layout raiz
        root_layout = QVBoxLayout()

        # Cabeçalho da página Bloqueado
        head_frame = QFrame()
        head_frame.setObjectName("HeaderBloqueado")
        head_layout = QHBoxLayout(head_frame)
        head_layout.setContentsMargins(8, 4, 8, 12)
        head_layout.setSpacing(4)
        # Wrapper decorativo do título
        titulo_wrap = QFrame()
        titulo_wrap.setObjectName("TituloWrap")
        wrap_layout = QHBoxLayout(titulo_wrap)
        wrap_layout.setContentsMargins(28, 6, 28, 6)
        wrap_layout.setSpacing(14)
        line_left = QFrame()
        line_left.setObjectName("DecorLine")
        line_left.setFrameShape(QFrame.Shape.HLine)
        line_left.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        lab_titulo = QLabel("BLOQUEADO")
        lab_titulo.setObjectName("TituloBloqueado")
        line_right = QFrame()
        line_right.setObjectName("DecorLine")
        line_right.setFrameShape(QFrame.Shape.HLine)
        line_right.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        wrap_layout.addWidget(line_left)

        # Container do título com ícone
        titulo_container = QWidget()
        titulo_layout = QHBoxLayout(titulo_container)
        titulo_layout.setContentsMargins(0, 0, 0, 0)
        titulo_layout.setSpacing(8)
        icone_bloqueado = QLabel("🔒")
        icone_bloqueado.setObjectName("IconeBloqueado")
        icone_bloqueado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo_layout.addWidget(icone_bloqueado)
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
        self.btn_help_bloq = QPushButton("❓ Ajuda")
        self.btn_help_bloq.setObjectName("HelpBloqueado")
        try:
            self.btn_help_bloq.setCursor(Qt.CursorShape.PointingHandCursor)
        except Exception:
            pass
        self.btn_help_bloq.setToolTip("Ajuda sobre a seção Bloqueado")
        self.btn_help_bloq.clicked.connect(self._mostrar_ajuda_bloqueado)
        head_layout.addWidget(self.btn_help_bloq, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        root_layout.addWidget(head_frame)
        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 60))
            head_frame.setGraphicsEffect(shadow)
        except Exception:
            pass
        self.setStyleSheet(self.styleSheet() + QSS_HEADER_BLOQUEADO)

        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form_layout.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form_layout.setSpacing(10)

        # Campo: Item (código)
        self.campo_item = QLineEdit()
        self.campo_item.setPlaceholderText("Ex: 2222223")
        self.campo_item.setValidator(QIntValidator(1, 10_000_000, self))
        self.campo_item.setClearButtonEnabled(True)
        form_layout.addRow("&Item (cód.):", self.campo_item)

        # Campo: Quantidade
        self.campo_quantidade = QLineEdit()
        self.campo_quantidade.setPlaceholderText("Ex: 150")
        self.campo_quantidade.setValidator(QIntValidator(1, 1_000_000, self))
        self.campo_quantidade.setClearButtonEnabled(True)
        form_layout.addRow("&Quantidade:", self.campo_quantidade)

        # Campo: Matrícula
        self.campo_matricula = QLineEdit()
        self.campo_matricula.setPlaceholderText("Responsável pela Movimentação / Erro")
        self.campo_matricula.setValidator(QIntValidator(1, 99_999_999, self))
        self.campo_matricula.setClearButtonEnabled(True)
        lab_matricula = QLabel("Matrícula:")
        lab_matricula.setToolTip("Matrícula do responsável pela movimentação ou erro.")
        form_layout.addRow(lab_matricula, self.campo_matricula)

        # Campo: Data da movimentação (abaixo de Matrícula)
        from PySide6.QtWidgets import QDateEdit
        from PySide6.QtCore import QDate
        self.campo_data_mov = QDateEdit()
        self.campo_data_mov.setDisplayFormat("yyyy-MM-dd")
        self.campo_data_mov.setCalendarPopup(True)
        self.campo_data_mov.setDate(QDate.currentDate())
        lab_data_mov = QLabel("Data da movimentação:")
        form_layout.addRow(lab_data_mov, self.campo_data_mov)

        # Observação (combo + texto)
        self.cb_motivo_padrao = QComboBox()
        self.cb_motivo_padrao.setObjectName("ComboMotivoPadrao")
        motivos_padrao: list = [
            "-- Selecione --",
            "Armazenamento inadequado",
            "Armazenamento fora do sistema",
            "Movimentação inadequado",
            "Movimentação apenas fisica",
            "Movimentação apenas sistemica",
            "Ressuprimento irregular",
            "Separação incorreta",
            "Perca no manuseio",
            "Recebido trocado",
            "Não movimentado do Box de recebimento",
            "Perca do produto pós recebimento",
            "Produto com avaria",
            "Expedição irregular",
            "Entrada inrreegular",
            "Erro de contagem",
            "Antenas consumo interno",
            "Outros",
        ]
        self.cb_motivo_padrao.addItems(motivos_padrao)
        self.campo_motivo = QTextEdit()
        self.campo_motivo.setPlaceholderText("Selecione um motivo padrão ou 'Outros' para digitar...")
        self.campo_motivo.setAcceptRichText(False)
        self.campo_motivo.setTabChangesFocus(True)
        self.campo_motivo.setEnabled(False)
        wrap_obs = QVBoxLayout()
        wrap_obs.setSpacing(4)
        wrap_obs_widget = QWidget()
        wrap_obs_widget.setLayout(wrap_obs)
        wrap_obs.addWidget(self.cb_motivo_padrao)
        wrap_obs.addWidget(self.campo_motivo)
        form_layout.addRow("&Observação:", wrap_obs_widget)
        self.cb_motivo_padrao.currentIndexChanged.connect(self._on_motivo_padrao_changed)

        # Campo: Setor
        self.campo_setor = QComboBox()
        self.campo_setor.setEditable(False)
        self.campo_setor.addItem("-- Selecione --", "")
        self.campo_setor.addItems(list(SETORES_GLOBAIS))
        self.campo_setor.setCurrentIndex(0)
        form_layout.addRow("&Setor:", self.campo_setor)

        # Botões
        self.botao_salvar = QPushButton("&Inserir")
        self.botao_salvar.clicked.connect(self._on_inserir)
        self.botao_salvar.setDefault(True)

        self.botao_exportar = QPushButton("&Exportar")
        self.botao_exportar.clicked.connect(self._abrir_exportacao)

        botoes_layout = QHBoxLayout()
        botoes_layout.addStretch(1)
        botoes_layout.addWidget(self.botao_exportar)
        botoes_layout.addWidget(self.botao_salvar)

        # Feedback label
        self.feedback = QLabel()
        self.feedback.setObjectName("feedbackLabel")
        self.feedback.setVisible(False)

        root_layout.addLayout(form_layout)
        root_layout.addWidget(self.feedback)
        root_layout.addLayout(botoes_layout)
        self.setLayout(root_layout)

        self._aplicar_tema()

    def _aplicar_tema(self) -> None:
        from PySide6.QtWidgets import QApplication
        QApplication.setStyle("Fusion")
        self.setPalette(build_palette_claro())
        self.setStyleSheet(self.styleSheet() + QSS_FORMULARIO_BASE)
        self.botao_exportar.setObjectName("danger")

    # ------------------------- Lógica ------------------------- #
    def _validar(self) -> Optional[str]:
        if not self.campo_item.text().strip():
            return "Item é obrigatório."
        try:
            valor_item = int(self.campo_item.text())
            if valor_item <= 0:
                return "Item deve ser maior que zero."
        except ValueError:
            return "Item inválido."
        if not self.campo_quantidade.text().strip():
            return "Quantidade é obrigatória."
        try:
            qtd = int(self.campo_quantidade.text())
            if qtd <= 0:
                return "Quantidade deve ser maior que zero."
        except ValueError:
            return "Quantidade inválida."
        # Validação do motivo/observação
        idx_mot = self.cb_motivo_padrao.currentIndex()
        texto_mot = self.campo_motivo.toPlainText().strip()
        if idx_mot <= 0:  # placeholder
            return "Observação é obrigatória (selecione ou escolha 'Outros')."
        rotulo_sel = self.cb_motivo_padrao.currentText()
        if rotulo_sel == "Outros" and not texto_mot:
            return "Digite a observação em 'Outros'."
        if rotulo_sel != "Outros" and not texto_mot:
            return "Observação inválida."
        if self.campo_setor.currentIndex() <= 0:
            return "Selecione um Setor."
        # Data da movimentação sempre definida (pode permitir None no futuro)
        try:
            _ = self.campo_data_mov.date()
        except Exception:
            return "Data da movimentação inválida."
        return None

    def _on_inserir(self) -> None:
        erro = self._validar()
        if erro:
            self._mostrar_feedback(erro, erro_flag=True)
            return
        registro = Registro(
            item=int(self.campo_item.text()),
            quantidade=int(self.campo_quantidade.text()),
            motivo=self.campo_motivo.toPlainText().strip(),
            setor_responsavel=self.campo_setor.currentText().strip(),
            matricula=int(self.campo_matricula.text()),
            data_mov=self.campo_data_mov.date().toString("yyyy-MM-dd"),
        )
        # Persistência
        try:
            from database import salvar_registro  # import local
            registro_id = salvar_registro(
                item=registro.item,
                quantidade=registro.quantidade,
                motivo=registro.motivo,
                setor_responsavel=registro.setor_responsavel,
                matricula=registro.matricula,
                data_mov=registro.data_mov,
            )
            self._mostrar_feedback(
                f"Registro #{registro_id} inserido: {registro.item} (Qtd: {registro.quantidade})",
                erro_flag=False,
            )
            # Limpa após inserção
            self.campo_item.clear()
            self.campo_quantidade.clear()
            self.cb_motivo_padrao.setCurrentIndex(0)
            self.campo_motivo.clear()
            self.campo_motivo.setEnabled(False)
            self.campo_setor.setCurrentIndex(0)
            # mantém a data no dia corrente
            try:
                from PySide6.QtCore import QDate
                self.campo_data_mov.setDate(QDate.currentDate())
            except Exception:
                pass
            self.campo_item.setFocus()
        except Exception as exc:  # pragma: no cover
            self._mostrar_feedback(f"Falha ao salvar: {exc}", erro_flag=True)

    def _mostrar_feedback(self, mensagem: str, erro_flag: bool) -> None:
        self.feedback.setProperty("erro", "true" if erro_flag else "false")
        self.feedback.setText(mensagem)
        self.feedback.setVisible(True)
        self.feedback.style().unpolish(self.feedback)
        self.feedback.style().polish(self.feedback)
        if erro_flag:
            if "Item" in mensagem:
                self.campo_item.setFocus()
            elif "Quantidade" in mensagem:
                self.campo_quantidade.setFocus()
            elif "Motivo" in mensagem or "Observação" in mensagem:
                self.cb_motivo_padrao.setFocus()
            elif "Setor" in mensagem:
                self.campo_setor.setFocus()

    def _on_motivo_padrao_changed(self) -> None:
        idx = self.cb_motivo_padrao.currentIndex()
        texto = self.cb_motivo_padrao.currentText()
        if idx <= 0:  # placeholder
            self.campo_motivo.clear()
            self.campo_motivo.setEnabled(False)
        elif texto == "Outros":
            self.campo_motivo.clear()
            self.campo_motivo.setEnabled(True)
            self.campo_motivo.setFocus()
        else:
            self.campo_motivo.setEnabled(False)
            self.campo_motivo.setPlainText(texto)

    def _abrir_exportacao(self) -> None:
        dlg = ExportDialog(parent=self)
        if dlg.exec():
            params = dlg.get_params()
            try:
                from database import consultar_registros_filtrados
                regs = consultar_registros_filtrados(
                    data_ini=params.get("data_ini") or None,
                    data_fim=params.get("data_fim") or None,
                    motivo_sub=params.get("motivo") or None,
                )
            except ValueError as exc:
                QMessageBox.warning(self, "Aviso", str(exc))
                return
            if not regs:
                QMessageBox.information(self, "Exportação", "Nenhum registro para os filtros.")
                return
            # Escolher arquivo
            from datetime import datetime
            padrao_nome = f"registros_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.{params.get('formato','csv')}"
            from PySide6.QtWidgets import QFileDialog
            arquivo, _ = QFileDialog.getSaveFileName(self, "Salvar Exportação", padrao_nome, "Arquivos (*.*)")
            if not arquivo:
                return
            try:
                self._exportar_arquivo(regs, arquivo, params.get("formato", "csv"))
            except Exception as exc:  # pragma: no cover
                QMessageBox.critical(self, "Erro", f"Falha ao exportar: {exc}")
                return
            QMessageBox.information(self, "Exportação", f"Exportado {len(regs)} registro(s).")

    def _exportar_arquivo(self, registros: list[dict], caminho: str, formato: str) -> None:
        formato = (formato or "csv").lower()
        if formato == "csv":
            import csv
            with open(caminho, "w", newline="", encoding="utf-8") as f:
                w = csv.writer(f, delimiter=';')
                # Inclui matrícula e Data da movimentação
                w.writerow(["id", "item", "quantidade", "motivo", "setor", "matricula", "data_mov", "usuario", "created_at"])
                for r in registros:
                    w.writerow([
                        r.get("id", ""), r.get("item", ""), r.get("quantidade", ""), r.get("motivo", ""), r.get("setor_responsavel", ""), r.get("matricula", ""), r.get("data_mov", ""), r.get("usuario") or "", r.get("created_at", "")
                    ])
        elif formato == "xlsx":
            from openpyxl import Workbook
            wb = Workbook()
            ws = wb.active
            # Inclui matrícula e Data da movimentação
            ws.append(["id", "item", "quantidade", "motivo", "setor", "matricula", "data_mov", "usuario", "created_at"])
            for r in registros:
                ws.append([
                    r.get("id", ""), r.get("item", ""), r.get("quantidade", ""), r.get("motivo", ""), r.get("setor_responsavel", ""), r.get("matricula", ""), r.get("data_mov", ""), r.get("usuario") or "", r.get("created_at", "")
                ])
            wb.save(caminho)
        elif formato == "txt":
            with open(caminho, "w", encoding="utf-8") as f:
                for r in registros:
                    f.write("\t".join([
                        str(r.get('id','')),
                        str(r.get('item','')),
                        str(r.get('quantidade','')),
                        str(r.get('motivo','')),
                        str(r.get('setor_responsavel','')),
                        str(r.get('matricula','')),
                        str(r.get('data_mov','')),
                        str(r.get('usuario','') or ''),
                        str(r.get('created_at','')),
                    ]) + "\n")
        else:
            raise ValueError("Formato não suportado. Use csv, xlsx ou txt.")

    def _mostrar_ajuda_bloqueado(self) -> None:
        mensagem: str = (
            "Seção Bloqueado:\n\n"
            "Use este formulário para registrar itens que estão Bloqueados (ex: aguardando análise, qualidade, manutenção).\n"
            "Campos:\n"
            "- Item: código numérico do item.\n"
            "- Quantidade: volume afetado.\n"
            "- Motivo: razão detalhada do bloqueio.\n"
            "- Setor: setor responsável ou impactado.\n\n"
            "O registro ficará associado ao usuário logado e pode ser consultado futuramente em outras seções." 
        )
        QMessageBox.information(self, "Ajuda - Bloqueado", mensagem)

from __future__ import annotations

from typing import Optional, List, Dict

from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QIntValidator, QRegularExpressionValidator, QColor
from PySide6.QtWidgets import (
	QWidget,
	QVBoxLayout,
	QHBoxLayout,
	QFormLayout,
	QLabel,
	QLineEdit,
	QTextEdit,
	QComboBox,
	QDateEdit,
	QPushButton,
	QTableWidget,
	QTableWidgetItem,
	QMessageBox,
	QFrame,
	QSizePolicy,
	QGraphicsDropShadowEffect,
	QDialog,
	QDialogButtonBox,
	QAbstractItemView,
	QStyledItemDelegate,
)

from style import QSS_HEADER_BLOQUEADO, QSS_FORMULARIO_BASE
from database import salvar_senha_corte


class _IntDelegate(QStyledItemDelegate):
	"""Delegate para edição com QLineEdit + QIntValidator."""

	def __init__(self, parent=None, minimo: int = 1, maximo: int = 9_999_999):
		super().__init__(parent)
		self._min = minimo
		self._max = maximo

	def createEditor(self, parent, option, index):
		ed = QLineEdit(parent)
		ed.setValidator(QIntValidator(self._min, self._max, ed))
		# Mantém o editor com aparência padrão, sem bordas arredondadas
		ed.setStyleSheet("border-radius:0; padding:0px; margin:0px;")
		return ed


class ItensDialog(QDialog):
	"""Diálogo para inserir itens (Código, Quantidade)."""

	def __init__(self, parent: Optional[QWidget] = None, itens: Optional[List[Dict]] = None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Itens da Senha Corte")
		self.resize(520, 360)
		self._build(itens or [])

	def _build(self, itens: List[Dict]) -> None:
		root = QVBoxLayout(self)

		# Cabeçalho estilizado
		head = QFrame()
		head.setObjectName("HeaderBloqueado")
		hl = QHBoxLayout(head)
		hl.setContentsMargins(12, 8, 12, 8)
		hl.setSpacing(8)
		icon = QLabel("📦")
		icon.setObjectName("IconeBloqueado")
		lab = QLabel("Itens da Senha Corte")
		# Fonte maior e cor branca
		lab_font = lab.font()
		try:
			lab_font.setPointSize(max(lab_font.pointSize(), 26))
		except Exception:
			pass
		lab.setFont(lab_font)
		# Usa stylesheet para garantir o tamanho mesmo com QSS herdado
		lab.setStyleSheet("color: #ffffff; font-size: 18px; font-weight: bold;")
		lab.setObjectName("TituloBloqueado")
		hl.addWidget(icon)
		hl.addWidget(lab)
		hl.addStretch(1)
		root.addWidget(head)
		# Aplica QSS se disponível
		try:
			if QSS_HEADER_BLOQUEADO:
				self.setStyleSheet(self.styleSheet() + QSS_HEADER_BLOQUEADO)
		except Exception:
			pass

		self.tab = QTableWidget(0, 2)
		self.tab.setHorizontalHeaderLabels(["Código", "Quantidade"])
		try:
			from PySide6.QtWidgets import QHeaderView
			hdr = self.tab.horizontalHeader()
			hdr.setStretchLastSection(True)
			hdr.setSectionResizeMode(QHeaderView.Stretch)
			hdr.setMinimumSectionSize(120)
		except Exception:
			pass
		self.tab.verticalHeader().setVisible(False)
		self.tab.verticalHeader().setDefaultSectionSize(26)
		self.tab.setAlternatingRowColors(True)
		self.tab.setSelectionBehavior(QAbstractItemView.SelectRows)
		self.tab.setSelectionMode(QAbstractItemView.SingleSelection)
		self.tab.setEditTriggers(QAbstractItemView.AllEditTriggers)
		self.tab.setWordWrap(False)
		# Tooltips de cabeçalho
		it0 = QTableWidgetItem("Código")
		it0.setToolTip("Código do item (Valido)")
		it1 = QTableWidgetItem("Quantidade")
		it1.setToolTip("Quantidade (inteiro >= 1)")
		self.tab.setHorizontalHeaderItem(0, it0)
		self.tab.setHorizontalHeaderItem(1, it1)
		# Delegates de validação
		self.tab.setItemDelegateForColumn(0, _IntDelegate(self, 1_000, 9_999_999))
		self.tab.setItemDelegateForColumn(1, _IntDelegate(self, 1, 9_999_999))
		# Estilo da tabela
		self.tab.setStyleSheet(
			"""
			QTableWidget { background: #fff; gridline-color: #2a2a2a; }
			QHeaderView::section { background-color: #1e1e1e; color: #ddd; padding: 6px; border: none; }
			QTableWidget::item:selected { background: #2d7dd2; color: white; }
			QTableWidget QLineEdit { border-radius: 0; padding: 0px; margin: 0px; border: 1px solid palette(mid); }
			"""
		)
		root.addWidget(self.tab)

		row_btn = QHBoxLayout()
		self.btn_add = QPushButton("➕ Adicionar")
		self.btn_del = QPushButton("➖ Remover")
		self.btn_clear = QPushButton("🧹 Limpar")
		self.lab_count = QLabel("Itens: 0")
		self.lab_count.setStyleSheet("color: #888;")
		self.btn_add.clicked.connect(self._adicionar)
		self.btn_del.clicked.connect(self._remover)
		self.btn_clear.clicked.connect(self._limpar)
		self.btn_del.setEnabled(False)
		self.btn_add.setStyleSheet("padding:6px 12px; background:#2ecc71; color:#fff; border:none; border-radius:6px;")
		self.btn_del.setStyleSheet("padding:6px 12px; background:#e74c3c; color:#fff; border:none; border-radius:6px;")
		self.btn_clear.setStyleSheet("padding:6px 12px; background:#555; color:#fff; border:none; border-radius:6px;")
		row_btn.addWidget(self.btn_add)
		row_btn.addWidget(self.btn_del)
		row_btn.addWidget(self.btn_clear)
		row_btn.addStretch(1)
		row_btn.addWidget(self.lab_count)
		root.addLayout(row_btn)

		try:
			self.tab.selectionModel().selectionChanged.connect(self._atualizar_estado)
		except Exception:
			pass

		# Preload itens
		for it in itens:
			self._adicionar(codigo=it.get("codigo_item"), qtd=it.get("quantidade", 0))
		self._atualizar_contador()

		box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
		box.accepted.connect(self._on_accept)
		box.rejected.connect(self.reject)
		root.addWidget(box)

	def _adicionar(self, *, codigo: Optional[int] = None, qtd: Optional[int] = None) -> None:
		r = self.tab.rowCount()
		self.tab.insertRow(r)
		it_cod = QTableWidgetItem(str(codigo or ""))
		it_cod.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
		it_qtd = QTableWidgetItem(str(qtd or 1))
		it_qtd.setTextAlignment(Qt.AlignVCenter | Qt.AlignLeft)
		self.tab.setItem(r, 0, it_cod)
		self.tab.setItem(r, 1, it_qtd)
		self._atualizar_contador()
		self._atualizar_estado()

	def _remover(self) -> None:
		r = self.tab.currentRow()
		if r >= 0:
			self.tab.removeRow(r)
			self._atualizar_contador()
			self._atualizar_estado()

	def _limpar(self) -> None:
		self.tab.setRowCount(0)
		self._atualizar_contador()
		self._atualizar_estado()

	def _on_accept(self) -> None:
		# Valida cada linha: Código >= 1000 e Quantidade >= 1
		linhas = self.tab.rowCount()
		validos = 0
		for r in range(linhas):
			it_cod = self.tab.item(r, 0)
			it_qtd = self.tab.item(r, 1)
			try:
				codigo = int((it_cod.text() if it_cod else "").strip() or 0)
			except Exception:
				codigo = 0
			try:
				qtd = int((it_qtd.text() if it_qtd else "").strip() or 0)
			except Exception:
				qtd = 0
			if codigo >= 1000 and qtd >= 1:
				validos += 1
		if validos == 0:
			QMessageBox.warning(self, "Aviso", "Adicione pelo menos um item válido (Código > valido).")
			return
		self.accept()

	def get_itens(self) -> List[Dict]:
		itens: List[Dict] = []
		for r in range(self.tab.rowCount()):
			it_cod = self.tab.item(r, 0)
			it_qtd = self.tab.item(r, 1)
			try:
				codigo = int((it_cod.text() if it_cod else "").strip() or 0)
			except Exception:
				codigo = 0
			try:
				qtd = int((it_qtd.text() if it_qtd else "").strip() or 0)
			except Exception:
				qtd = 0
			if codigo >= 1000 and qtd >= 1:
				itens.append({"codigo_item": codigo, "quantidade": qtd})
		return itens

	def _atualizar_contador(self) -> None:
		self.lab_count.setText(f"Itens: {self.tab.rowCount()}")

	def _atualizar_estado(self) -> None:
		self.btn_del.setEnabled(self.tab.currentRow() >= 0)


class SenhaCortePage(QWidget):
	"""Página para registrar Senha Corte.

	Campos:
	  - Ordem (int)
	  - Carga (int)
	  - Valor (float)
	  - Data Ordem (calendário)
	  - Tipo de tratativa (Finalizado | Cancelado | Em andamento)
	- Itens: adicionados via diálogo (Obrigatório)
	- Observação: campo de texto opcional
	Inserção: imprime payload no console.
	"""

	def __init__(self, parent: Optional[QWidget] = None) -> None:
		super().__init__(parent)
		self.setObjectName("PaginaSenhaCorte")
		self._itens: List[Dict] = []
		self._build()

	def _build(self) -> None:
		root = QVBoxLayout(self)

		# Cabeçalho padrão
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

		lab_titulo = QLabel("SENHA CORTE")
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

		icone = QLabel("✂️")
		icone.setObjectName("IconeBloqueado")
		icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
		titulo_layout.addWidget(icone)
		titulo_layout.addWidget(lab_titulo)

		wrap_layout.addWidget(titulo_container)
		wrap_layout.addWidget(line_right)
		head_layout.addWidget(titulo_wrap, 0, Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

		# Botão de Ajuda no header, padronizado com outros heads
		self.btn_help = QPushButton("❓ Ajuda")
		self.btn_help.setObjectName("HelpBloqueado")
		try:
			self.btn_help.setCursor(Qt.CursorShape.PointingHandCursor)
		except Exception:
			pass
		self.btn_help.setToolTip("Ajuda sobre a seção Senha Corte")
		self.btn_help.clicked.connect(self._on_help_clicked)

		try:
			_title_shadow = QGraphicsDropShadowEffect(self)
			_title_shadow.setBlurRadius(20)
			_title_shadow.setOffset(0, 2)
			lab_titulo.setGraphicsEffect(_title_shadow)
		except Exception:
			pass

		head_layout.addStretch(1)
		# Botão à direita
		head_layout.addWidget(self.btn_help, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
		# Limita altura do cabeçalho para manter consistência visual
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
		if QSS_HEADER_BLOQUEADO:
			self.setStyleSheet(self.styleSheet() + QSS_HEADER_BLOQUEADO)

		# Formulário
		form = QFormLayout()
		form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
		form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
		form.setSpacing(10)

		# Campo Ordem
		self.ed_ordem = QLineEdit()
		self.ed_ordem.setValidator(QIntValidator(10_000, 9_999_999, self))
		self.ed_ordem.setPlaceholderText("Ex: 123412")
		form.addRow("&Ordem:", self.ed_ordem)

		# Botão Itens abaixo da Ordem
		self.btn_itens = QPushButton("Inserir Itens…")
		self.btn_itens.clicked.connect(self._abrir_itens_dialogo)
		self.lab_itens = QLabel("Itens selecionados: 0")
		self.lab_itens.setStyleSheet("color: #666;")
		wrap_itens = QHBoxLayout()
		wrap_itens.setContentsMargins(0, 0, 0, 0)
		wrap_itens.setSpacing(8)
		container_itens = QWidget()
		container_itens.setLayout(wrap_itens)
		wrap_itens.addWidget(self.btn_itens)
		wrap_itens.addWidget(self.lab_itens)
		wrap_itens.addStretch(1)
		form.addRow("", container_itens)

		self.ed_carga = QLineEdit()
		self.ed_carga.setValidator(QIntValidator(1_000, 9_999_999, self))
		self.ed_carga.setPlaceholderText("Ex: 23131")
		form.addRow("&Carga:", self.ed_carga)

		self.ed_valor = QLineEdit()
		# Aceita 123, 123.45, 123,45
		regex = QRegularExpression(r"^\d{1,9}([\.,]\d{1,2})?$")
		self.ed_valor.setValidator(QRegularExpressionValidator(regex, self))
		self.ed_valor.setPlaceholderText("Ex: 199,90")
		form.addRow("&Valor:", self.ed_valor)

		self.ed_data = QDateEdit()
		self.ed_data.setDisplayFormat("yyyy-MM-dd")
		self.ed_data.setCalendarPopup(True)
		self.ed_data.setDate(QDate.currentDate())
		form.addRow("&Data Ordem:", self.ed_data)

		self.cb_tipo = QComboBox()
		self.cb_tipo.addItems(["Finalizado", "Cancelado", "Em andamento"])
		# Valor padrão: "Em andamento"
		self.cb_tipo.setCurrentText("Em andamento")
		form.addRow("&Tipo de tratativa:", self.cb_tipo)

		# Campo condicional: Data da Finalização (mostra para Finalizado/Cancelado)
		self.lab_data_fim = QLabel("Data da Finalização:")
		self.ed_data_fim = QDateEdit()
		self.ed_data_fim.setDisplayFormat("yyyy-MM-dd")
		self.ed_data_fim.setCalendarPopup(True)
		self.ed_data_fim.setDate(QDate.currentDate())
		self.lab_data_fim.setVisible(False)
		self.ed_data_fim.setVisible(False)
		form.addRow(self.lab_data_fim, self.ed_data_fim)
		self.cb_tipo.currentIndexChanged.connect(self._on_tipo_changed)
		# Sincroniza a visibilidade inicial conforme valor padrão
		self._on_tipo_changed()

		# Fecha formulário
		root.addLayout(form)

		# Observação opcional (área maior)
		root.addWidget(QLabel("Observação (opcional):"))
		self.ed_obs = QTextEdit()
		self.ed_obs.setAcceptRichText(False)
		self.ed_obs.setPlaceholderText("Escreva aqui, se necessário…")
		self.ed_obs.setMinimumHeight(90)
		root.addWidget(self.ed_obs)

		# Botões de ação
		row_btn = QHBoxLayout()
		row_btn.addStretch(1)
		self.btn_inserir = QPushButton("Inserir")
		self.btn_inserir.clicked.connect(self._on_inserir)
		row_btn.addWidget(self.btn_inserir)
		root.addLayout(row_btn)

		# Estilo base
		self.setStyleSheet(self.styleSheet() + QSS_FORMULARIO_BASE)

	def _abrir_itens_dialogo(self) -> None:
		dlg = ItensDialog(self, itens=self._itens)
		if dlg.exec() == QDialog.Accepted:
			self._itens = dlg.get_itens()
			self._atualizar_resumo_itens()

	def _on_help_clicked(self) -> None:
		QMessageBox.information(
			self,
			"Ajuda — Senha Corte",
			(
				"Como preencher esta tela:\n\n"
				"1) Ordem (obrigatório): número inteiro da ordem.\n"
				"2) Carga (obrigatório): número inteiro da carga.\n"
				"3) Valor (obrigatório): valor monetário; aceita 123,45 ou 123.45 (2 casas).\n"
				"4) Data Ordem (obrigatório): selecione no calendário.\n"
				"5) Tipo de tratativa (obrigatório): escolha uma opção.\n\n"
				"Itens (obrigatório):\n"
				"- Clique em ‘Inserir Itens…’ para abrir o diálogo.\n"
				"- Para cada item informe: Código (inteiro) e Quantidade (>= 1).\n"
				"- Use os botões ➕ Adicionar, ➖ Remover e 🧹 Limpar conforme necessário.\n"
				"- Clique em OK para confirmar os itens (o contador ‘Itens selecionados: N’ será atualizado).\n\n"
				"Observação (opcional):\n"
				"- Campo livre para anotações adicionais.\n\n"
				"Finalizar:\n"
				"- Clique em ‘Inserir’. Os dados serão validados e enviados (impressos no console).\n"
			),
		)

	def _validar(self) -> Optional[str]:
		if not self.ed_ordem.text().strip():
			return "Ordem é obrigatória."
		try:
			if int(self.ed_ordem.text()) < 10_000:
				return "Ordem deve ser valida."
		except Exception:
			return "Ordem inválida."
		if not self.ed_carga.text().strip():
			return "Carga é obrigatória."
		try:
			if int(self.ed_carga.text()) < 1_000:
				return "Carga deve ser valida."
		except Exception:
			return "Carga inválida."
		if not self.ed_valor.text().strip():
			return "Valor é obrigatório."
		# Itens obrigatórios
		if not self._itens:
			return "Adicione pelo menos um item."
		return None

	def _parse_valor(self, s: str) -> float:
		s = (s or "").strip()
		if not s:
			return 0.0
		s = s.replace(" ", "")
		if "," in s and "." in s:
			s = s.replace(".", "")
			s = s.replace(",", ".")
		elif "," in s:
			s = s.replace(".", "")
			s = s.replace(",", ".")
		try:
			return float(s)
		except Exception:
			return 0.0

	def _coletar_payload(self) -> Dict:
		payload = {
			"ordem": int(self.ed_ordem.text()),
			"carga": int(self.ed_carga.text()),
			"valor": self._parse_valor(self.ed_valor.text()),
			"data_ordem": self.ed_data.date().toString("yyyy-MM-dd"),
			"tipo": self.cb_tipo.currentText(),
			"observacao": self.ed_obs.toPlainText().strip(),
			"itens": list(self._itens),
		}
		if self.cb_tipo.currentText() in ("Finalizado", "Cancelado"):
			payload["data_finalizacao"] = self.ed_data_fim.date().toString("yyyy-MM-dd")
		return payload

	def _on_tipo_changed(self) -> None:
		tipo = self.cb_tipo.currentText()
		# Visibilidade do campo de data de finalização
		mostrar = tipo in ("Finalizado", "Cancelado")
		self.lab_data_fim.setVisible(mostrar)
		self.ed_data_fim.setVisible(mostrar)

		# Estilo do combo conforme o tipo selecionado
		if tipo == "Cancelado":
			self.cb_tipo.setStyleSheet("QComboBox { background-color: #f18c0f; color: #000000; }")
		elif tipo == "Finalizado":
			self.cb_tipo.setStyleSheet("QComboBox { background-color: #2bc06a; color: #000000; }")
		else:
			# Restaura o estilo padrão herdado do formulário
			self.cb_tipo.setStyleSheet("")

	def _atualizar_resumo_itens(self) -> None:
		qtd = len(self._itens)
		self.lab_itens.setText(f"Itens selecionados: {qtd}")

	def _limpar_formulario(self) -> None:
		"""Limpa todos os campos do formulário após inserção."""
		self.ed_ordem.clear()
		self.ed_carga.clear()
		self.ed_valor.clear()
		self.ed_data.setDate(QDate.currentDate())
		self.cb_tipo.setCurrentText("Em andamento")
		self.ed_data_fim.setDate(QDate.currentDate())
		self._itens = []
		self._atualizar_resumo_itens()
		self.ed_obs.clear()
		# Garante visibilidade correta dos campos condicionais e estilo do combo
		self._on_tipo_changed()
		# Foco no primeiro campo
		self.ed_ordem.setFocus()

	def _on_inserir(self) -> None:
		erro = self._validar()
		if erro:
			QMessageBox.warning(self, "Aviso", erro)
			return
		data = self._coletar_payload()
		# Persistência no banco
		try:
			cab_id = salvar_senha_corte(
				ordem=data["ordem"],
				carga=data["carga"],
				valor=data["valor"],
				data_ordem=data["data_ordem"],
				tipo_tratativa=data["tipo"],
				observacao=data["observacao"] or None,
				data_finalizacao=data.get("data_finalizacao"),
				itens=[{"codigo": it.get("codigo_item"), "quantidade": it.get("quantidade"), "tipo_tratativa": data["tipo"]} for it in data["itens"]],
			)
			QMessageBox.information(self, "Senha Corte", f"Registro salvo com sucesso (ID {cab_id}).")
			self._limpar_formulario()
		except Exception as e:
			QMessageBox.critical(self, "Erro", f"Falha ao salvar: {e}")
		# Limpa o formulário após inserção
		self._limpar_formulario()

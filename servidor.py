"""Interface gráfica para inserção de dados: Item, Quantidade, Motivo, Setor Responsável.

Boas práticas adotadas:
 - Separação de construção da UI em método dedicado (_build_ui)
 - Validação de campos (quantidade numérica > 0, textos não vazios)
 - Mensagens de erro objetivas e rápidas
 - Uso de dataclass para representar o registro inserido
 - Estilo consistente (Fusion + palette custom) e acessibilidade (atalhos, tab order)
 - Preparado para futura extensão (ex: persistência) sem mudar contrato atual

Requisitos do usuário: apenas a interface para inserir os quatro campos solicitados.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Dict
from time import time
import sys
from pathlib import Path

try:
	from PySide6.QtCore import Qt, QSize
	from PySide6.QtGui import QIntValidator, QIcon, QPalette, QColor, QPixmap, QGuiApplication
	from PySide6.QtWidgets import (
		QApplication,
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
		QMainWindow,
		QStackedWidget,
		QFrame,
		QSizePolicy,
		QScrollArea,
		QButtonGroup,
		QDialog,
		QSpacerItem,
		QGridLayout,
		QGraphicsDropShadowEffect,
		QTableWidget,
		QTableWidgetItem,
		QHeaderView,
		QAbstractScrollArea,
	)
except ImportError as exc:  # Falha clara caso dependência não esteja instalada
	raise SystemExit(
		"Dependência PySide6 não encontrada. Instale com: pip install PySide6"
	) from exc

# Estilos centralizados do aplicativo
from style import (
	build_palette_claro,
	build_palette_escuro,
	QSS_HEADER_BLOQUEADO,
	QSS_FORMULARIO_BASE,
	QSS_CONSULTAS_PAGE,
	QSS_SLIMBAR_BASE,
	qss_tema_extra,
	qss_focus_override,
)

# Lista global de setores centralizada em config
from config import SETORES as SETORES_GLOBAIS

# Import opcional da página de gráficos
try:
	from grafico import GraficoPage  # type: ignore
	HAS_GRAFICO = True
except Exception:
	HAS_GRAFICO = False

# Import opcional da página de consolidado
try:
	from consolidado import ConsolidadoPage  # type: ignore
	HAS_CONSOLIDADO = True
except Exception:
	HAS_CONSOLIDADO = False

# Import opcional da página de monitoramento
try:
	from monitoramento import MonitoramentoPage  # type: ignore
	HAS_MONITORAMENTO = True
except Exception:
	HAS_MONITORAMENTO = False

# Import opcional da página de EPIs
try:
	from epis import EpisPage  # type: ignore
	HAS_EPIS = True
except Exception:
	HAS_EPIS = False

# Import opcional da página Senha Corte
try:
	from senha_corte import SenhaCortePage  # type: ignore
	HAS_SENHA_CORTE = True
except Exception:
	HAS_SENHA_CORTE = False

# Import opcional da página de almoxarifado
try:
	from almoxarifado import AlmoxarifadoPage  # type: ignore
	HAS_ALMOX = True
except Exception:
	HAS_ALMOX = False

# Import opcional da página de consultas externa
try:
	from consultas import ConsultasPage  # type: ignore
	HAS_CONSULTAS_PAGE = True
except Exception:
	HAS_CONSULTAS_PAGE = False

# Import opcional da página de Registros (auditoria)
try:
	from registros import RegistrosPage  # type: ignore
	HAS_REGISTROS = True
except Exception:
	HAS_REGISTROS = False

# Import opcional da página Bloqueado (extraída)
try:
	from bloqueado import BloqueadoPage  # type: ignore
	HAS_BLOQUEADO = True
except Exception:
	HAS_BLOQUEADO = False

# Utilitário para localizar arquivos de recursos (assets) tanto em desenvolvimento quanto empacotado (PyInstaller)
def _resource_path(rel_path: str) -> str:
	base = getattr(sys, "_MEIPASS", None)
	if base:
		return str(Path(base) / rel_path)
	return str(Path(__file__).resolve().parent / rel_path)


def _get_app_icon():
	try:
		from PySide6.QtGui import QIcon
	except Exception:
		return None
	for candidate in ("assets/app_icon.ico", "assets/app_icon.png", "assets/app_icon.svg"):
		p = Path(_resource_path(candidate))
		if p.exists():
			return QIcon(str(p))
	return QIcon()


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


## Classe de exportação específica da página Consultas foi removida (mantida em consultas.py)


class MainWindow(QMainWindow):
	"""Janela principal com slimbar lateral e área central com páginas.

	A página 'Bloqueado' usa o formulário existente. Outras páginas são placeholders.
	"""

	SECOES: list = [
		"Consultas",
		"Consolidado",
		"Bloqueado",
		"Entrada",
		"Saida",
		"Senha Falta",
		"Senha Corte",
		"balanceamento",
		"Cadastro",
		"Monitoramento",
		"Almoxarifado",
		"EPIs",
		"Sindicância",
		"Checklist",
		"Grafico",
		"Registros",
		"Configurações",
	]

	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle("Sistema Tech")
		self._set_window_icon()
		self.setMinimumSize(960, 620)
		self._botoes: Dict[str, QPushButton] = {}
		self._stack = QStackedWidget()
		self._button_group = QButtonGroup(self)
		self._button_group.setExclusive(True)
		# Cache simples (item -> (timestamp, lista de registros)) para evitar consultas repetidas
		self._consulta_cache: dict[int, tuple[float, list[dict]]] = {}
		self._consulta_cache_ttl = 120.0  # segundos
		self._consulta_cache_max = 50
		self._ultimos_resultados_consulta: list[dict] = []  # cache da última consulta para exportação
		self._icons_map: dict = {
			"Consultas": "📊",
			"Consolidado": "📟",
			"Bloqueado": "🔒",
			"Entrada": "📥",
			"Saida": "📤",
			"Senha Falta": "🔑",
			"Senha Corte": "🛡️",
			"balanceamento": "⚖️",
			"Cadastro": "👤",
			"Monitoramento": "📋",
			"Almoxarifado": "🏢",
			"EPIs": "🦺",
			"Sindicância": "🕵️",
			"Checklist": "☑️",
			"Grafico": "📈",
			"Registros": "🗂️",
			"Configurações": "⚙️",
		}
		self.APP_NAME = "Sistema Tech"
		self.APP_SUBTITLE = "Gestão Integrada"
		self.APP_VERSION = "v2.1.3"
		# Captura usuário logado para exibir no footer
		try:
			from database import obter_usuario_atual
			self.CURRENT_USER = obter_usuario_atual() or "USUARIO"  # manter caso correto para lógica
			self.CURRENT_USER_DISPLAY = self.CURRENT_USER.upper()  # apenas para exibição
		except Exception:
			self.CURRENT_USER = "USUARIO"
			self.CURRENT_USER_DISPLAY = self.CURRENT_USER
		self._montar_ui()
		self._aplicar_estilo_slimbar()
		# Aplica tema CLARO imediatamente na inicialização da janela principal
		try:
			self._ativar_tema_claro()
			if hasattr(self, "btn_tema_claro"):
				self.btn_tema_claro.setChecked(True)
		except Exception:
			pass
		self._selecionar_secao_inicial("Consultas")

	def _montar_ui(self) -> None:
		container = QWidget()
		layout_root = QHBoxLayout(container)
		layout_root.setContentsMargins(0, 0, 0, 0)

		# Slimbar
		self.slimbar = QFrame()
		self.slimbar.setObjectName("Slimbar")
		self._slimbar_colapsado = False
		self.slimbar.setFixedWidth(220)  # largura padrão
		lay_slim = QVBoxLayout(self.slimbar)
		lay_slim.setContentsMargins(0, 0, 0, 0)
		lay_slim.setSpacing(0)

		# Área de rolagem apenas para as seções (botões de navegação)
		nav_scroll = QScrollArea()
		nav_scroll.setFrameShape(QFrame.Shape.NoFrame)
		nav_scroll.setWidgetResizable(True)
		nav_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
		nav_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
		nav_scroll.setMaximumHeight(620)
		nav_content = QWidget()
		lay_nav_content = QVBoxLayout(nav_content)
		lay_nav_content.setContentsMargins(0, 8, 0, 8)
		lay_nav_content.setSpacing(4)

		# Botão de alternância (Hide/Show)
		self.btn_toggle_menu = QPushButton("◀ Ocultar Menu")
		self.btn_toggle_menu.setObjectName("ToggleMenu")
		self.btn_toggle_menu.setCursor(Qt.CursorShape.PointingHandCursor)
		self.btn_toggle_menu.clicked.connect(self._toggle_slimbar)
		lay_slim.addWidget(self.btn_toggle_menu)

		# Header
		header = self._criar_header()
		lay_slim.addWidget(header)

		# Separador após header
		sep_top = QFrame()
		sep_top.setFrameShape(QFrame.Shape.HLine)
		sep_top.setObjectName("SlimSeparator")
		lay_slim.addWidget(sep_top)

		# Botões de navegação
		self._texto_botoes: Dict[str, str] = {}
		for nome in self.SECOES:
			rotulo = f"{self._icons_map.get(nome, '')}  {nome}".strip()
			btn = QPushButton(rotulo)
			btn.setCheckable(True)
			btn.setCursor(Qt.CursorShape.PointingHandCursor)
			btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
			btn.clicked.connect(lambda _=False, n=nome: self._on_navegar(n))
			self._botoes[nome] = btn
			self._texto_botoes[nome] = rotulo
			self._button_group.addButton(btn)
			lay_nav_content.addWidget(btn)

		lay_nav_content.addStretch(1)
		nav_scroll.setWidget(nav_content)
		lay_slim.addWidget(nav_scroll, 1)

		# Footer
		footer_sep = QFrame()
		footer_sep.setFrameShape(QFrame.Shape.HLine)
		footer_sep.setObjectName("SlimSeparator")
		lay_slim.addWidget(footer_sep)
		footer = self._criar_footer()
		lay_slim.addWidget(footer)

		# Páginas
		for nome in self.SECOES:
			if nome == "Bloqueado":
				if HAS_BLOQUEADO:
					pagina = BloqueadoPage()
				else:
					pagina = self._criar_placeholder("Bloqueado (módulo ausente)")
			elif nome == "Consultas":
				if HAS_CONSULTAS_PAGE:
					pagina = ConsultasPage()
				else:
					pagina = self._criar_placeholder("Consultas (módulo ausente)")
			elif nome == "Consolidado":
				if HAS_CONSOLIDADO:
					pagina = ConsolidadoPage()
				else:
					pagina = self._criar_placeholder("Consolidado (módulo ausente)")
			elif nome == "Grafico":
				if HAS_GRAFICO:
					pagina = GraficoPage()
				else:
					pagina = self._criar_placeholder("Grafico (QtCharts não disponível)")
			elif nome == "Configurações":
				pagina = self._criar_configuracoes()
			elif nome == "Monitoramento":
				if HAS_MONITORAMENTO:
					pagina = MonitoramentoPage()
				else:
					pagina = self._criar_placeholder("Monitoramento (módulo ausente)")
			elif nome == "Almoxarifado":
				if HAS_ALMOX:
					pagina = AlmoxarifadoPage()
				else:
					pagina = self._criar_placeholder("Almoxarifado (módulo ausente)")
			elif nome == "EPIs":
				if HAS_EPIS:
					pagina = EpisPage()
				else:
					pagina = self._criar_placeholder("EPIs (módulo ausente)")
			elif nome == "Senha Corte":
				if HAS_SENHA_CORTE:
					pagina = SenhaCortePage()
				else:
					pagina = self._criar_placeholder("Senha Corte (módulo ausente)")
			elif nome == "Registros":
				if HAS_REGISTROS:
					pagina = RegistrosPage()
				else:
					pagina = self._criar_placeholder("Registros (módulo ausente)")
			else:
				pagina = self._criar_placeholder(nome)
			self._stack.addWidget(pagina)

		layout_root.addWidget(self.slimbar)
		layout_root.addWidget(self._stack, 1)
		self.setCentralWidget(container)

	def _criar_placeholder(self, nome: str) -> QWidget:
		w = QWidget()
		lay = QVBoxLayout(w)
		lab = QLabel(f"Seção '{nome}' ainda não implementada.")
		lab.setAlignment(Qt.AlignmentFlag.AlignCenter)
		lab.setObjectName("PlaceholderLabel")
		lay.addWidget(lab, 1)
		return w

	# Página Consultas é fornecida por consultas.py; métodos duplicados removidos.

	def _criar_header(self) -> QWidget:
		header = QWidget()
		lay = QVBoxLayout(header)
		lay.setContentsMargins(12, 8, 12, 8)
		lay.setSpacing(4)

		icon_box = QLabel()
		icon_box.setObjectName("AppIcon")
		icon_box.setFixedSize(QSize(44, 44))
		try:
			ic = _get_app_icon()
			pm = ic.pixmap(44, 44)
			if not pm.isNull():
				icon_box.setPixmap(pm)
		except Exception:
			pass

		lab_nome = QLabel(self.APP_NAME)
		lab_nome.setObjectName("AppName")
		lab_sub = QLabel(self.APP_SUBTITLE)
		lab_sub.setObjectName("AppSubtitle")

		top_line = QHBoxLayout()
		top_line.addWidget(icon_box, 0, Qt.AlignmentFlag.AlignTop)
		text_box = QVBoxLayout()
		text_box.setSpacing(0)
		text_box.addWidget(lab_nome)
		text_box.addWidget(lab_sub)
		top_line.addLayout(text_box, 1)
		top_line.addStretch(1)

		lay.addLayout(top_line)
		# Guardar referências para uso no colapso
		self._header_refs: dict = {
			"header": header,
			"icon": icon_box,
			"nome": lab_nome,
			"sub": lab_sub,
		}
		return header

	def _criar_footer(self) -> QWidget:
		footer = QWidget()
		lay = QVBoxLayout(footer)
		lay.setContentsMargins(12, 4, 12, 4)
		lay.setSpacing(2)
		lab_user = QLabel(f"👤  {getattr(self, 'CURRENT_USER_DISPLAY', self.CURRENT_USER)}")
		lab_user.setObjectName("UserLabel")
		try:
			# Permite clique no nome do usuário para abrir o Perfil
			lab_user.setCursor(Qt.CursorShape.PointingHandCursor)
			lab_user.mousePressEvent = lambda e: self._abrir_perfil()
		except Exception:
			pass
		lab_status = QLabel("🟢 Sistema Online")
		lab_status.setObjectName("StatusLabel")
		lab_version = QLabel(f"🔖 {self.APP_VERSION}")
		lab_version.setObjectName("VersionLabel")
		lay.addWidget(lab_user)
		lay.addWidget(lab_status)
		lay.addWidget(lab_version)
		self._footer_refs: dict = {
			"footer": footer,
			"user": lab_user,
			"status": lab_status,
			"version": lab_version,
		}
		return footer

	def _abrir_perfil(self) -> None:
		"""Abre o painel de Perfil do usuário atual."""
		try:
			from perfil import PerfilDialog  # type: ignore
		except Exception as exc:
			QMessageBox.critical(self, "Perfil", f"Módulo de perfil indisponível: {exc}")
			return
		dlg = PerfilDialog(self)
		dlg.exec()

	def _toggle_slimbar(self) -> None:
		"""Alterna entre Slimbar expandida e colapsada.

		- Colapsada: largura ~64, botões mostram apenas ícones, header oculta textos.
		- Expandida: largura padrão, botões mostram ícone + texto.
		"""
		self._slimbar_colapsado = not getattr(self, "_slimbar_colapsado", False)
		if self._slimbar_colapsado:
			self.slimbar.setFixedWidth(64)
			self.btn_toggle_menu.setText("▶ Mostrar Menu")
			# Header: mostra apenas ícone
			if hasattr(self, "_header_refs"):
				self._header_refs["nome"].setVisible(False)
				self._header_refs["sub"].setVisible(False)
				self._header_refs["icon"].setFixedSize(QSize(36, 36))
			# Footer: reduzir visibilidade (opcional: esconder status/versão)
			if hasattr(self, "_footer_refs"):
				self._footer_refs["status"].setVisible(False)
				self._footer_refs["version"].setVisible(False)
				# Mantém o UserLabel sempre visível mesmo colapsado
				self._footer_refs["user"].setVisible(True)
		else:
			self.slimbar.setFixedWidth(220)
			self.btn_toggle_menu.setText("◀ Ocultar Menu")
			if hasattr(self, "_header_refs"):
				self._header_refs["nome"].setVisible(True)
				self._header_refs["sub"].setVisible(True)
				self._header_refs["icon"].setFixedSize(QSize(44, 44))
			if hasattr(self, "_footer_refs"):
				self._footer_refs["status"].setVisible(True)
				self._footer_refs["version"].setVisible(True)
				# Reforça o UserLabel visível ao expandir
				self._footer_refs["user"].setVisible(True)
		self._update_slimbar_labels()

	def _update_slimbar_labels(self) -> None:
		"""Atualiza o texto dos botões da Slimbar conforme estado (colapsado/expandido)."""
		for nome, btn in self._botoes.items():
			icon = self._icons_map.get(nome, "")
			if self._slimbar_colapsado:
				btn.setText(icon)
				btn.setToolTip(nome)
				btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
			else:
				btn.setText(self._texto_botoes.get(nome, f"{icon}  {nome}"))
				btn.setToolTip("")

	def _criar_configuracoes(self) -> QWidget:
		w = QWidget()
		w.setObjectName("PaginaConfiguracoes")
		lay = QVBoxLayout(w)
		lay.setContentsMargins(40, 30, 40, 30)
		lay.setSpacing(24)

		# Seção Alterar Tema
		sec_tema = QFrame()
		sec_tema.setObjectName("SecaoTema")
		ltema = QVBoxLayout(sec_tema)
		ltema.setSpacing(8)
		lab_tema = QLabel("Tema")
		lab_tema.setObjectName("SectionTitle")
		# Botões de modo: Sistêmico, Claro, Escuro (modo Normal removido conforme solicitação)
		self.btn_tema_claro = QPushButton("Claro")
		self.btn_tema_escuro = QPushButton("Escuro")
		for b in (self.btn_tema_claro, self.btn_tema_escuro):
			b.setCheckable(True)
		linha_tema = QHBoxLayout()
		linha_tema.addWidget(self.btn_tema_claro)
		linha_tema.addWidget(self.btn_tema_escuro)
		linha_tema.addStretch(1)
		ltema.addWidget(lab_tema)
		ltema.addLayout(linha_tema)
		self.btn_tema_claro.clicked.connect(lambda: self._aplicar_tema_global("claro"))
		self.btn_tema_escuro.clicked.connect(lambda: self._aplicar_tema_global("escuro"))

		# Seção Alterar Senha
		sec_senha = QFrame()
		sec_senha.setObjectName("SecaoSenha")
		lsenha = QVBoxLayout(sec_senha)
		lsenha.setSpacing(8)
		lab_senha = QLabel("Alterar Senha")
		lab_senha.setObjectName("SectionTitle")
		form = QFormLayout()
		self.ed_senha_atual = QLineEdit()
		self.ed_senha_atual.setEchoMode(QLineEdit.EchoMode.Password)
		self.ed_nova_senha = QLineEdit()
		self.ed_nova_senha.setEchoMode(QLineEdit.EchoMode.Password)
		self.ed_conf_nova = QLineEdit()
		self.ed_conf_nova.setEchoMode(QLineEdit.EchoMode.Password)
		form.addRow("Senha atual:", self.ed_senha_atual)
		form.addRow("Nova senha:", self.ed_nova_senha)
		form.addRow("Confirmar nova:", self.ed_conf_nova)
		btn_salvar_senha = QPushButton("Salvar Senha")
		btn_salvar_senha.clicked.connect(self._alterar_senha)
		lsenha.addWidget(lab_senha)
		lsenha.addLayout(form)
		lsenha.addWidget(btn_salvar_senha, 0, Qt.AlignmentFlag.AlignLeft)

		lay.addWidget(sec_tema)
		lay.addWidget(sec_senha)

		# Seção administrativa (somente ADMINISTRADOR)
		try:
			from database import obter_tipo_usuario_atual
			is_admin = obter_tipo_usuario_atual() == "ADMINISTRADOR"
		except Exception:
			is_admin = False
		if is_admin:
			lay.addWidget(self._criar_secao_admin())
		lay.addStretch(1)
		return w

	def _criar_secao_admin(self) -> QWidget:
		"""Cria seção de administração de usuários (lista + ações)."""
		wrap = QFrame()
		wrap.setObjectName("SecaoAdminUsuarios")
		lv = QVBoxLayout(wrap)
		lv.setSpacing(8)
		lab = QLabel("Usuários (USUARIO)")
		lab.setObjectName("SectionTitle")
		lv.addWidget(lab)
		# Container scroll
		self.scroll_users = QScrollArea()
		self.scroll_users.setWidgetResizable(True)
		self.scroll_users.setFixedHeight(160)  # ~4 itens (ajustável)
		cont = QWidget()
		self.layout_users = QVBoxLayout(cont)
		self.layout_users.setSpacing(4)
		self.layout_users.setContentsMargins(0,0,0,0)
		self.scroll_users.setWidget(cont)
		lv.addWidget(self.scroll_users)
		# Ações sobre usuário selecionado
		linha_sel = QHBoxLayout()
		self.ed_usuario_sel = QLineEdit()
		self.ed_usuario_sel.setPlaceholderText("Usuário selecionado...")
		self.ed_usuario_sel.setReadOnly(True)
		linha_sel.addWidget(self.ed_usuario_sel)
		btn_refresh = QPushButton("↻")
		btn_refresh.setToolTip("Recarregar lista")
		btn_refresh.clicked.connect(self._carregar_usuarios_admin)
		linha_sel.addWidget(btn_refresh)
		lv.addLayout(linha_sel)
		linha_acoes = QHBoxLayout()
		self.ed_nova_senha_admin = QLineEdit()
		self.ed_nova_senha_admin.setPlaceholderText("Nova senha p/ usuário")
		self.ed_nova_senha_admin.setEchoMode(QLineEdit.EchoMode.Password)
		btn_redef = QPushButton("Redefinir Senha")
		btn_redef.clicked.connect(self._redefinir_senha_usuario)
		btn_excluir = QPushButton("Excluir Usuário")
		btn_excluir.setObjectName("danger")
		btn_excluir.clicked.connect(self._excluir_usuario)
		linha_acoes.addWidget(self.ed_nova_senha_admin, 1)
		linha_acoes.addWidget(btn_redef)
		linha_acoes.addWidget(btn_excluir)
		lv.addLayout(linha_acoes)
		self._carregar_usuarios_admin()
		return wrap

	def _carregar_usuarios_admin(self) -> None:
		# Limpa lista
		while self.layout_users.count():
			item = self.layout_users.takeAt(0)
			w = item.widget()
			if w:
				w.deleteLater()
		try:
			from database import listar_usuarios
			usuarios = listar_usuarios(tipo="USUARIO")
		except Exception as exc:  # pragma: no cover
			lab_err = QLabel(f"Erro ao carregar usuários: {exc}")
			self.layout_users.addWidget(lab_err)
			return
		for u in usuarios:
			btn = QPushButton(u["username"])
			btn.setCheckable(False)
			btn.setCursor(Qt.CursorShape.PointingHandCursor)
			btn.clicked.connect(lambda _=False, nome=u["username"]: self._selecionar_usuario_admin(nome))
			self.layout_users.addWidget(btn)
		self.layout_users.addStretch(1)

	def _selecionar_usuario_admin(self, username: str) -> None:
		self.ed_usuario_sel.setText(username)

	def _redefinir_senha_usuario(self) -> None:
		user_alvo = self.ed_usuario_sel.text().strip()
		if not user_alvo:
			QMessageBox.warning(self, "Aviso", "Selecione um usuário.")
			return
		nova = self.ed_nova_senha_admin.text()
		if not nova:
			QMessageBox.warning(self, "Aviso", "Informe nova senha.")
			return
		try:
			from database import redefinir_senha_usuario
			ok = redefinir_senha_usuario(username=user_alvo, nova_senha=nova)
		except ValueError as exc:
			QMessageBox.critical(self, "Erro", str(exc))
			return
		except Exception as exc:  # pragma: no cover
			QMessageBox.critical(self, "Erro", f"Falha: {exc}")
			return
		if not ok:
			QMessageBox.warning(self, "Aviso", "Usuário não encontrado.")
			return
		QMessageBox.information(self, "Sucesso", "Senha redefinida.")
		self.ed_nova_senha_admin.clear()

	def _excluir_usuario(self) -> None:
		user_alvo = self.ed_usuario_sel.text().strip()
		if not user_alvo:
			QMessageBox.warning(self, "Aviso", "Selecione um usuário.")
			return
		if user_alvo == self.CURRENT_USER:
			QMessageBox.warning(self, "Aviso", "Não é possível excluir o próprio usuário logado.")
			return
		resp = QMessageBox.question(self, "Confirmar", f"Excluir usuário '{user_alvo}'?", QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, QMessageBox.StandardButton.No)
		if resp != QMessageBox.StandardButton.Yes:
			return
		try:
			from database import excluir_usuario
			ok = excluir_usuario(username=user_alvo)
		except ValueError as exc:
			QMessageBox.critical(self, "Erro", str(exc))
			return
		except Exception as exc:  # pragma: no cover
			QMessageBox.critical(self, "Erro", f"Falha: {exc}")
			return
		if not ok:
			QMessageBox.warning(self, "Aviso", "Usuário não encontrado ou não pode ser excluído.")
			return
		QMessageBox.information(self, "Sucesso", "Usuário excluído.")
		self.ed_usuario_sel.clear()
		self._carregar_usuarios_admin()

	def _aplicar_tema_global(self, modo: str) -> None:
		# Desmarca todos antes de aplicar (apenas claro/escuro)
		for b in [self.btn_tema_claro, self.btn_tema_escuro]:
			b.setChecked(False)
		if modo == "escuro":
			self._ativar_tema_escuro()
			self.btn_tema_escuro.setChecked(True)
		elif modo == "claro":
			self._ativar_tema_claro()
			self.btn_tema_claro.setChecked(True)

	def _ativar_tema_escuro(self) -> None:
		QApplication.instance().setPalette(build_palette_escuro())
		self._atualizar_estilos_tema("escuro")
		self._ajustar_focus_bloqueado("escuro")
		# Atualiza tema da página de gráficos, se existir
		try:
			for i in range(self._stack.count()):
				w = self._stack.widget(i)
				if getattr(w, "objectName", lambda: "")() == "PaginaGrafico" and hasattr(w, "aplicar_tema"):
					w.aplicar_tema("escuro")
		except Exception:
			pass

	def _ativar_tema_claro(self) -> None:
		# Modo Claro especial
		QApplication.instance().setPalette(build_palette_claro())
		self._atualizar_estilos_tema("claro")
		self._ajustar_focus_bloqueado("claro")
		# Atualiza tema da página de gráficos, se existir
		try:
			for i in range(self._stack.count()):
				w = self._stack.widget(i)
				if getattr(w, "objectName", lambda: "")() == "PaginaGrafico" and hasattr(w, "aplicar_tema"):
					w.aplicar_tema("claro")
		except Exception:
			pass

	# Modo sem tema removido

	def _atualizar_estilos_tema(self, modo: str) -> None:
		"""Reaplica o stylesheet global a partir da base, evitando acúmulo de QSS.

		- Sempre recompõe: base_global + QSS_SLIMBAR_BASE + overrides do tema
		- Depois, aplica QSS específico por página (Consultas) com precedência local
		"""
		base = getattr(self, "_stylesheet_base", "") or ""
		qss_global = base + QSS_SLIMBAR_BASE + qss_tema_extra(modo)
		self.setStyleSheet(qss_global)
		# Re-polish do main window para garantir refresh imediato do QSS
		self.style().unpolish(self)
		self.style().polish(self)
		# Atualiza também o QSS da página Consultas com precedência local
		self._aplicar_qss_consultas_por_tema(modo)

	def _aplicar_qss_consultas_por_tema(self, modo: str) -> None:
		"""Aplica o QSS da página Consultas conforme o tema, com prioridade no próprio widget."""
		consultas_qss_escuro = (
			"""
			#PaginaConsultas QLineEdit { padding:6px 8px; }
			#TabelaConsultas { background:#403f3f; border:1px solid #b7d9ef; gridline-color:#bababa; color:#fff; alternate-background-color:#292929; }
			#TabelaConsultas QHeaderView::section { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #001d2e, stop:1 #001724); color:#ffffff; padding:4px 6px; border:1px solid #002336; font-weight:600; }
			#StatusConsultaLabel { color:#666; padding:4px 2px; }
			"""
		)
		for i in range(self._stack.count()):
			w = self._stack.widget(i)
			if w and getattr(w, "objectName", lambda: None)() == "PaginaConsultas":
				if modo == "escuro":
					w.setStyleSheet(consultas_qss_escuro)
				else:
					w.setStyleSheet(QSS_CONSULTAS_PAGE)
				# Re-polish garante aplicação imediata
				w.style().unpolish(w)
				w.style().polish(w)
				break

	def _ajustar_focus_bloqueado(self, modo: str) -> None:
		"""Garante que o foco dos campos do formulário Bloqueado use cores corretas por tema.

		O stylesheet local do formulário define um fundo azul (#eef7ff) no foco. Aqui
		sobrescrevemos após mudança de tema para evitar conflito de precedência.
		"""
		for i in range(self._stack.count()):
			w = self._stack.widget(i)
			# Detecta a página Bloqueado sem depender do nome da classe antiga
			is_bloqueado = False
			try:
				from bloqueado import BloqueadoPage  # type: ignore
				is_bloqueado = isinstance(w, BloqueadoPage)
			except Exception:
				# fallback por objectName
				is_bloqueado = getattr(w, "objectName", lambda: "")() in {"PaginaBloqueado", "PaginaBloqueadoPage"}
			if is_bloqueado:
				# Guarda base (sem overrides dinâmicos) apenas uma vez
				if not hasattr(w, "_base_stylesheet"):
					w._base_stylesheet = w.styleSheet()
				# Inclui também os extras do tema (garante que HeaderBloqueado no escuro
				# sobrescreva o QSS base aplicado localmente no widget)
				override_focus = qss_focus_override(modo)
				override_tema = qss_tema_extra(modo)
				w.setStyleSheet(w._base_stylesheet + override_tema + override_focus)
				# Re-polish garante refresh imediato
				w.style().unpolish(w)
				w.style().polish(w)
				break

	def _alterar_senha(self) -> None:
		user = self.CURRENT_USER
		if not user:
			QMessageBox.warning(self, "Aviso", "Usuário não identificado.")
			return
		atual = self.ed_senha_atual.text()
		nova = self.ed_nova_senha.text()
		conf = self.ed_conf_nova.text()
		if not atual or not nova:
			QMessageBox.warning(self, "Aviso", "Preencha senha atual e nova.")
			return
		if nova != conf:
			QMessageBox.warning(self, "Aviso", "Nova senha e confirmação não conferem.")
			return
		try:
			from database import alterar_senha
			sucesso = alterar_senha(username=user, senha_atual=atual, nova_senha=nova)
		except ValueError as exc:
			QMessageBox.critical(self, "Erro", str(exc))
			return
		if not sucesso:
			QMessageBox.critical(self, "Erro", "Senha atual incorreta.")
			return
		QMessageBox.information(self, "Sucesso", "Senha alterada.")
		self.ed_senha_atual.clear()
		self.ed_nova_senha.clear()
		self.ed_conf_nova.clear()

	def _on_navegar(self, nome: str) -> None:
		# Atualiza botão selecionado e muda página
		btn = self._botoes.get(nome)
		if btn and not btn.isChecked():
			btn.setChecked(True)
		indice = self.SECOES.index(nome)
		self._stack.setCurrentIndex(indice)

	def _selecionar_secao_inicial(self, nome: str) -> None:
		self._on_navegar(nome)

	def _aplicar_estilo_slimbar(self) -> None:
		if not hasattr(self, "_stylesheet_base"):
			self._stylesheet_base = self.styleSheet()
		self.setStyleSheet(self._stylesheet_base + QSS_SLIMBAR_BASE)

	def _set_window_icon(self) -> None:
		self.setWindowIcon(_get_app_icon())


# ------------------------- Login / Registro ------------------------- #

class LoginDialog(QDialog):
	def __init__(self) -> None:
		super().__init__()
		self.setWindowTitle("Login")
		self.setModal(True)
		self.setObjectName("AuthDialog")
		self.setWindowIcon(_get_app_icon())
		self._build()
		self.usuario = None

	def _build(self) -> None:
		from style import QSS_AUTH_DIALOG
		self.setStyleSheet(self.styleSheet() + QSS_AUTH_DIALOG)
		layout = QVBoxLayout(self)

		# Header com ícone e título
		header = QHBoxLayout()
		ic = QLabel("🔐")
		ic.setObjectName("AuthIcon")
		title_box = QVBoxLayout()
		lab_t = QLabel("Acessar Conta")
		lab_t.setObjectName("AuthTitle")
		lab_s = QLabel("Digite suas credenciais para entrar")
		lab_s.setObjectName("AuthSubtitle")
		title_box.addWidget(lab_t)
		title_box.addWidget(lab_s)
		header.addWidget(ic, 0, Qt.AlignmentFlag.AlignTop)
		header.addLayout(title_box)
		header.addStretch(1)
		layout.addLayout(header)

		form = QFormLayout()
		self.ed_user = QLineEdit()
		self.ed_user.setPlaceholderText("Usuário")
		self.ed_senha = QLineEdit()
		self.ed_senha.setEchoMode(QLineEdit.EchoMode.Password)
		self.ed_senha.setPlaceholderText("Senha")
		form.addRow("Usuário:", self.ed_user)
		form.addRow("Senha:", self.ed_senha)
		layout.addLayout(form)

		row_btns = QHBoxLayout()
		self.btn_login = QPushButton("Entrar")
		self.btn_login.setObjectName("Primary")
		self.btn_registrar = QPushButton("Registrar")
		self.btn_registrar.setObjectName("Ghost")
		# Enter deve acionar "Entrar"
		self.btn_login.setDefault(True)
		self.btn_login.setAutoDefault(True)
		self.btn_registrar.setDefault(False)
		self.btn_registrar.setAutoDefault(False)
		self.btn_login.clicked.connect(self._do_login)
		self.btn_registrar.clicked.connect(self._abrir_registro)
		# Enter nos campos também aciona login diretamente
		self.ed_user.returnPressed.connect(self._do_login)
		self.ed_senha.returnPressed.connect(self._do_login)
		row_btns.addStretch(1)
		row_btns.addWidget(self.btn_registrar)
		row_btns.addWidget(self.btn_login)
		layout.addLayout(row_btns)
		self.resize(380, 200)

	def _do_login(self) -> None:
		from database import autenticar_usuario
		user = self.ed_user.text().strip()
		senha = self.ed_senha.text()
		if not user or not senha:
			QMessageBox.warning(self, "Aviso", "Informe usuário e senha.")
			return
		if autenticar_usuario(username=user, senha=senha):
			self.usuario = user
			self.accept()
		else:
			QMessageBox.critical(self, "Erro", "Credenciais inválidas.")

	def _abrir_registro(self) -> None:
		dlg = RegistroUsuarioDialog(parent=self)
		if dlg.exec():
			QMessageBox.information(self, "Sucesso", "Usuário registrado. Faça login.")


class RegistroUsuarioDialog(QDialog):
	def __init__(self, parent: Optional[QWidget] = None) -> None:
		super().__init__(parent)
		self.setWindowTitle("Registro de Usuário")
		self.setModal(True)
		self.setObjectName("AuthDialog")
		self.setWindowIcon(_get_app_icon())
		self._build()

	def _build(self) -> None:
		from style import QSS_AUTH_DIALOG
		self.setStyleSheet(self.styleSheet() + QSS_AUTH_DIALOG)
		lay = QVBoxLayout(self)

		header = QHBoxLayout()
		ic = QLabel("🧩")
		ic.setObjectName("AuthIcon")
		title_box = QVBoxLayout()
		lab_t = QLabel("Criar Conta")
		lab_t.setObjectName("AuthTitle")
		lab_s = QLabel("Preencha os dados para registrar um novo usuário")
		lab_s.setObjectName("AuthSubtitle")
		title_box.addWidget(lab_t)
		title_box.addWidget(lab_s)
		header.addWidget(ic, 0, Qt.AlignmentFlag.AlignTop)
		header.addLayout(title_box)
		header.addStretch(1)
		lay.addLayout(header)

		form = QFormLayout()
		self.ed_user = QLineEdit()
		self.ed_user.setPlaceholderText("Novo usuário")
		self.ed_senha = QLineEdit()
		self.ed_senha.setEchoMode(QLineEdit.EchoMode.Password)
		self.ed_conf = QLineEdit()
		self.ed_conf.setEchoMode(QLineEdit.EchoMode.Password)
		self.cb_tipo = QComboBox()
		self.cb_tipo.addItems(["USUARIO", "ADMINISTRADOR"])  # substitui ADM
		self.ed_api = QLineEdit()
		self.ed_api.setPlaceholderText("API Key de Registro")
		self.ed_api.setEchoMode(QLineEdit.EchoMode.Password)
		form.addRow("Usuário:", self.ed_user)
		form.addRow("Senha:", self.ed_senha)
		form.addRow("Confirmar:", self.ed_conf)
		form.addRow("Tipo:", self.cb_tipo)
		form.addRow("API Key:", self.ed_api)
		lay.addLayout(form)
		btns = QHBoxLayout()
		btn_cancel = QPushButton("Cancelar")
		btn_cancel.setObjectName("Ghost")
		btn_ok = QPushButton("Criar")
		btn_ok.setObjectName("Primary")
		btn_cancel.clicked.connect(self.reject)
		btn_ok.clicked.connect(self._criar)
		btns.addStretch(1)
		btns.addWidget(btn_cancel)
		btns.addWidget(btn_ok)
		lay.addLayout(btns)
		self.resize(420, 240)

	def _criar(self) -> None:
		from database import criar_usuario
		user = self.ed_user.text().strip()
		senha = self.ed_senha.text()
		conf = self.ed_conf.text()
		tipo = self.cb_tipo.currentText()
		if not user or not senha:
			QMessageBox.warning(self, "Aviso", "Preencha usuário e senha.")
			return
		if senha != conf:
			QMessageBox.warning(self, "Aviso", "Senhas não conferem.")
			return
		api_key = self.ed_api.text().strip()
		try:
			criar_usuario(username=user, senha=senha, tipo=tipo, api_key=api_key)
		except ValueError as exc:
			QMessageBox.critical(self, "Erro", str(exc))
			return
		self.accept()


def executar() -> int:
	# Desabilita leitura automática de tema/ajustes do sistema (evita alternância escuro/claro do OS)
	try:
		QGuiApplication.setDesktopSettingsAware(False)
	except Exception:
		pass
	app = QApplication.instance() or QApplication(sys.argv)
	# Força estilo/paleta independentes do sistema desde o início
	try:
		QApplication.setStyle("Fusion")
		# Garante tema CLARO global (não seguir tema do Windows)
		QApplication.instance().setPalette(build_palette_claro())
	except Exception:
		pass
	# Inicializa banco
	try:
		from database import init_db
		init_db()
	except Exception as exc:  # pragma: no cover
		QMessageBox.critical(None, "Erro BD", f"Falha ao inicializar banco: {exc}")
		return 1
	# Fluxo de login
	login = LoginDialog()
	if not login.exec():
		return 0
	main = MainWindow()
	main.show()
	return app.exec()


if __name__ == "__main__":  # Execução direta
	raise SystemExit(executar())


from __future__ import annotations

from typing import Optional, Dict, List
from decimal import Decimal

from PySide6.QtCore import Qt, QDate, QRegularExpression
from PySide6.QtGui import QIntValidator, QColor, QRegularExpressionValidator
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFormLayout,
    QLabel,
    QPushButton,
    QComboBox,
    QDateEdit,
    QLineEdit,
    QTextEdit,
    QTableWidget,
    QTableWidgetItem,
    QMessageBox,
    QStyledItemDelegate,
    QFrame,
    QSizePolicy,
    QGraphicsDropShadowEffect,
)

from style import QSS_FORMULARIO_BASE, QSS_HEADER_BLOQUEADO
from database import listar_configuracoes_api, substituir_configuracoes_api

SETORES_GLOBAIS: List[str] = [
    "CARGA GROSSA",
    "FRACIONADO",
    "Recebimento",
    "Armazenagem e Ressuprimento",
    "SME - Logistica reversa",
    "Controle de Estoque",
    "Qualidade",
    "Expedição",
    "Monitoramento",
    "APRENDIZ ASSISTENTE ADMINISTRATIVO",
    "ARMAZENAGEM PCP LOGISTICO",
    "EFÁCIL",
    "GESTÃO DE ACERTOS",
    "GESTÃO DE FROTA",
    "Metal Grampo",
    "MANUTENÇÃO DE M&A",
    "MOTORISTA",
    "RECURSOS HUMANOS",
    "UTILIDADES",
    ]

# Motivos pré-definidos para Observação (EPIs)
MOTIVOS_EPI: List[str] = [
    "AVARIADA",
    "DESGASTE POR TEMPO DE USO",
    "DIVERGÊNCIA COM O TAMANHO",
    "MACHUCANDO",
    "DEFEITO DE FABRICA",
    "SOLADO RASGADO/FURADO",
    "PALMILHA AVARIADA",
    "CONTRAFORTE RASGADO/FURADO/DESCOLANDO",
    "TALONEIRA RASGADA/FURADA",
    "CANO RASGADO/FURADO",
    "CADARÇO AVARIADO",
    "BIQUEIRA AVARIADA",
    "INTERIOR DANIFICADO",
    "LATERAIS RASGADA",
    "AVARIADA POR MÁQUINA",
    "SOLADO DESCOLADO",
    "RASGADA NO CALCANHAR",
    "RASGADA",
]

class EpisPage(QWidget):
    """Página de EPIs para registrar entregas/trocas.

    Campos:
      - Matrícula (int)
      - Setor (lista global de setores)
      - Turno ("1° TURNO" | "2° TURNO")
      - Primeira? ("SIM" | "NÃO")
      - Data (calendário)
      - Responsável (int)
      - Código (str)
      - Produtos (lista: Produto + Quantidade)
      - Motivo da troca / Observação (texto)
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setObjectName("PaginaEPIs")
        self._catalogo_produtos: List[Dict] = []  # [{'codigo': str, 'produto': str}]
        self._carregar_catalogo_bd()
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)

        # Cabeçalho estilo Bloqueado/Monitoramento/Almoxarifado
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

        lab_titulo = QLabel("EPIs")
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

        icone = QLabel("🦺")
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
        self.btn_help_epi = QPushButton("❓ Ajuda")
        self.btn_help_epi.setObjectName("HelpBloqueado")
        self.btn_help_epi.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_help_epi.setToolTip("Ajuda sobre a seção EPIs")
        self.btn_help_epi.clicked.connect(self._mostrar_ajuda_epis)
        head_layout.addWidget(self.btn_help_epi, 0, Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignTop)
        head_frame.setMaximumHeight(116)

        try:
            shadow = QGraphicsDropShadowEffect(self)
            shadow.setBlurRadius(18)
            shadow.setOffset(0, 4)
            shadow.setColor(QColor(0, 0, 0, 60))
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

        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)
        form.setFormAlignment(Qt.AlignmentFlag.AlignTop)
        form.setSpacing(10)

        # Matrícula
        self.ed_matricula = QLineEdit()
        self.ed_matricula.setValidator(QIntValidator(1, 99_999_999, self))
        self.ed_matricula.setPlaceholderText("Ex: 123456")
        form.addRow("&Matrícula:", self.ed_matricula)

        # Setor
        self.cb_setor = QComboBox()
        self.cb_setor.addItem("-- Selecione --", "")
        self.cb_setor.addItems(list(SETORES_GLOBAIS))
        form.addRow("&Setor:", self.cb_setor)

        # Turno
        self.cb_turno = QComboBox()
        self.cb_turno.addItems(["1° TURNO", "2° TURNO"])
        form.addRow("&Turno:", self.cb_turno)

        # Primeira entrega?
        self.cb_primeira = QComboBox()
        self.cb_primeira.addItems(["SIM", "NÃO"])
        form.addRow("&Primeira?", self.cb_primeira)

        # Data
        self.ed_data = QDateEdit()
        self.ed_data.setDisplayFormat("yyyy-MM-dd")
        self.ed_data.setCalendarPopup(True)
        self.ed_data.setDate(QDate.currentDate())
        form.addRow("&Data:", self.ed_data)

        # Responsável (matrícula/int)
        self.ed_resp = QLineEdit()
        self.ed_resp.setValidator(QIntValidator(1, 99_999_999, self))
        self.ed_resp.setPlaceholderText("Matrícula do responsável")
        form.addRow("&Responsável:", self.ed_resp)

    # Produtos: Código (edita) -> Produto (auto) -> Quantidade -> Valor (Qtd x valor unitário da config)
        self.tab_produtos = QTableWidget(0, 5)
        self.tab_produtos.setHorizontalHeaderLabels(["Código", "Produto", "Quantidade", "Valor (R$)", "UON"])
        # Deixar a coluna Produto mais larga que as demais
        try:
            from PySide6.QtWidgets import QHeaderView
            header = self.tab_produtos.horizontalHeader()
            header.setStretchLastSection(False)
            # Modo base interativo
            header.setSectionResizeMode(QHeaderView.Interactive)
            # Colunas estreitas: Código, Quantidade, Valor e UON se ajustam ao conteúdo
            header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
            header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
            # Coluna Produto ocupa o espaço disponível
            header.setSectionResizeMode(1, QHeaderView.Stretch)
            header.setMinimumSectionSize(60)
        except Exception:
            # Fallback simples: garantir uma largura inicial maior para Produto
            try:
                self.tab_produtos.setColumnWidth(1, 300)
            except Exception:
                pass
        self.tab_produtos.setAlternatingRowColors(True)
        self.tab_produtos.itemChanged.connect(self._on_item_changed)
        # Autocomplete para Código e Produto (usando catálogos das configurações)
        try:
            self._setup_codigo_completer()
            self._setup_produto_completer()
        except Exception:
            pass
    
        row_prod = QHBoxLayout()
        btn_add = QPushButton("+ Adicionar Produto")
        btn_del = QPushButton("Remover Selecionado")
        btn_add.clicked.connect(self._adicionar_produto)
        btn_del.clicked.connect(self._remover_produto)
        row_prod.addWidget(btn_add)
        row_prod.addWidget(btn_del)
        row_prod.addStretch(1)

        form.addRow("&Produtos:", self.tab_produtos)
        form.addRow("", QWidget())  # espaçamento
        root.addLayout(form)
        root.addLayout(row_prod)

        # Observação (mesmo padrão do Bloqueado: combo + texto controlado)
        root.addWidget(QLabel("Observação:"))
        self.cb_motivo_epi = QComboBox()
        self.cb_motivo_epi.setObjectName("ComboMotivoEPIs")
        self.cb_motivo_epi.addItem("-- Selecione --", "")
        self.cb_motivo_epi.addItems(list(MOTIVOS_EPI) + ["Outros"])  # inclui 'Outros' ao final
        self.ed_obs = QTextEdit()
        self.ed_obs.setAcceptRichText(False)
        self.ed_obs.setPlaceholderText("Selecione um motivo padrão ou 'Outros' para digitar...")
        self.ed_obs.setTabChangesFocus(True)
        self.ed_obs.setEnabled(False)
        wrap_obs = QVBoxLayout()
        wrap_obs.setSpacing(4)
        wrap_obs_widget = QWidget()
        wrap_obs_widget.setLayout(wrap_obs)
        wrap_obs.addWidget(self.cb_motivo_epi)
        wrap_obs.addWidget(self.ed_obs)
        root.addWidget(wrap_obs_widget)
        self.cb_motivo_epi.currentIndexChanged.connect(self._on_motivo_epi_changed)

        # Ações
        row_btn = QHBoxLayout()
        row_btn.addStretch(1)
        self.btn_config = QPushButton("Configurações")
        # Estilo amarelo escuro específico para o botão Configurações (EPIs)
        try:
            self.btn_config.setCursor(Qt.CursorShape.PointingHandCursor)
            self.btn_config.setStyleSheet(
                """
                QPushButton {
                    background-color: #C9A227; /* amarelo escuro */
                    color: #111111;
                    border: none;
                    border-radius: 6px;
                    padding: 8px 14px;
                    font-weight: 600;
                }
                QPushButton:hover {
                    background-color: #B0891E;
                }
                QPushButton:pressed {
                    background-color: #8C7418;
                }
                """
            )
        except Exception:
            pass
        self.btn_config.clicked.connect(self._abrir_configuracoes)
        self.btn_inserir = QPushButton("Inserir")
        self.btn_inserir.clicked.connect(self._on_inserir)
        row_btn.addWidget(self.btn_config)
        row_btn.addWidget(self.btn_inserir)
        root.addLayout(row_btn)

        # Estilo base
        self.setStyleSheet(self.styleSheet() + QSS_FORMULARIO_BASE)

    def _mostrar_ajuda_epis(self) -> None:
        QMessageBox.information(
            self,
            "Ajuda - EPIs",
            (
                "Preencha Matrícula, Setor, Turno, Primeira entrega, Data e Responsável.\n"
                "Adicione Produtos informando o Código (preenche o Produto automaticamente) e a Quantidade.\n"
                "O Valor é calculado por (Quantidade x valor configurado).\n"
                "Selecione um motivo em Observação ou escolha 'Outros' para digitar."
            ),
        )

    def _on_motivo_epi_changed(self) -> None:
        """Habilita/Desabilita e preenche Observação conforme seleção (padrão Bloqueado)."""
        try:
            idx = self.cb_motivo_epi.currentIndex()
            texto = self.cb_motivo_epi.currentText()
            if idx <= 0:  # placeholder
                self.ed_obs.clear()
                self.ed_obs.setEnabled(False)
            elif texto == "Outros":
                self.ed_obs.clear()
                self.ed_obs.setEnabled(True)
                self.ed_obs.setFocus()
            else:
                self.ed_obs.setEnabled(False)
                self.ed_obs.setPlainText(texto)
        except Exception:
            pass

    # ----- Produtos ----- #
    def _adicionar_produto(self) -> None:
        r = self.tab_produtos.rowCount()
        self.tab_produtos.insertRow(r)
        # Código (editável)
        self.tab_produtos.setItem(r, 0, QTableWidgetItem(""))
        # Produto (auto, somente leitura)
        it_prod = QTableWidgetItem("")
        # Deixa Produto editável para permitir busca por nome
        self.tab_produtos.setItem(r, 1, it_prod)
        # Quantidade
        it_qtd = QTableWidgetItem()
        it_qtd.setData(Qt.ItemDataRole.DisplayRole, 1)
        self.tab_produtos.setItem(r, 2, it_qtd)
        # Valor total (somente leitura)
        it_val = QTableWidgetItem(self._format_brl(0))
        it_val.setFlags(it_val.flags() & ~Qt.ItemIsEditable)
        it_val.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.tab_produtos.setItem(r, 3, it_val)
        # UON (combobox por linha: PARES ou UNID)
        try:
            cb_uon = QComboBox()
            cb_uon.addItems(["PARES", "UNID"])  # ordem conforme solicitado
            cb_uon.setCurrentText("UNID")
            self.tab_produtos.setCellWidget(r, 4, cb_uon)
        except Exception:
            pass

    def _remover_produto(self) -> None:
        r = self.tab_produtos.currentRow()
        if r >= 0:
            self.tab_produtos.removeRow(r)

    def _validar(self) -> Optional[str]:
        if not self.ed_matricula.text().strip():
            return "Matrícula é obrigatória."
        if self.cb_setor.currentIndex() <= 0:
            return "Selecione um Setor."
        if not self.ed_resp.text().strip():
            return "Responsável é obrigatório."
        if self.tab_produtos.rowCount() == 0:
            return "Adicione ao menos um produto."
        # valida quantidades
        for r in range(self.tab_produtos.rowCount()):
            it_cod = self.tab_produtos.item(r, 0)
            it_prod = self.tab_produtos.item(r, 1)
            it_qtd = self.tab_produtos.item(r, 2)
            cod = (it_cod.text() if it_cod else "").strip()
            nome = (it_prod.text() if it_prod else "").strip()
            # Código deve existir nas configurações e preencher Produto
            if not cod:
                return f"Código na linha {r+1} está vazio."
            if not nome:
                return f"Código inválido na linha {r+1} (não encontrado nas configurações)."
            try:
                qtd = int(it_qtd.text()) if it_qtd and it_qtd.text() else 0
            except Exception:
                qtd = 0
            if qtd <= 0:
                return f"Quantidade inválida na linha {r+1}."
        # valida observação (mesmo padrão do Bloqueado)
        idx_mot = self.cb_motivo_epi.currentIndex()
        txt_mot = self.ed_obs.toPlainText().strip()
        if idx_mot <= 0:
            return "Observação é obrigatória (selecione ou escolha 'Outros')."
        rotulo_sel = self.cb_motivo_epi.currentText()
        if rotulo_sel == "Outros" and not txt_mot:
            return "Digite a observação em 'Outros'."
        if rotulo_sel != "Outros" and not txt_mot:
            return "Observação inválida."
        return None

    def _coletar_payload(self) -> Dict:
        produtos: list[Dict] = []
        for r in range(self.tab_produtos.rowCount()):
            it_cod = self.tab_produtos.item(r, 0)
            it_prod = self.tab_produtos.item(r, 1)
            it_qtd = self.tab_produtos.item(r, 2)
            # UON via combobox na coluna 4
            uon = None
            try:
                w = self.tab_produtos.cellWidget(r, 4)
                if isinstance(w, QComboBox):
                    uon = w.currentText().strip()
            except Exception:
                uon = None
            cod = (it_cod.text() if it_cod else "").strip()
            nome = (it_prod.text() if it_prod else "").strip()
            try:
                qtd = int(it_qtd.text()) if it_qtd and it_qtd.text() else 0
            except Exception:
                qtd = 0
            # Calcula valores para persistir: unitário e total (Decimal com 2 casas)
            unit_dec: Decimal = Decimal("0.00")
            try:
                if hasattr(self, "_valor_map") and cod:
                    vm = self._valor_map.get(cod)
                    unit_dec = vm if isinstance(vm, Decimal) else (self._parse_decimal(vm) or Decimal("0.00"))
            except Exception:
                unit_dec = Decimal("0.00")
            total_dec = (Decimal(max(0, qtd)) * (unit_dec if unit_dec >= Decimal("0") else Decimal("0.00"))).quantize(Decimal("0.01"))
            # Importante: backend aceita "10" ou "10,00"; enviaremos com ponto decimal.
            item_prod = {
                "codigo": cod,
                "produto": nome,
                "quantidade": qtd,
                "valor_unit": f"{unit_dec:.2f}",
                "valor_total": f"{total_dec:.2f}",
            }
            if uon:
                item_prod["uon"] = uon
            produtos.append(item_prod)
        payload = {
            "matricula": int(self.ed_matricula.text()),
            "setor": self.cb_setor.currentText(),
            "turno": self.cb_turno.currentText(),
            "primeira": self.cb_primeira.currentText(),
            "data": self.ed_data.date().toString("yyyy-MM-dd"),
            "responsavel": int(self.ed_resp.text()),
            "produtos": produtos,
            "observacao": self.ed_obs.toPlainText().strip(),
        }
        return payload

    def _on_inserir(self) -> None:
        erro = self._validar()
        if erro:
            QMessageBox.warning(self, "Aviso", erro)
            return
        payload = self._coletar_payload()
        # Persistência no banco de dados
        try:
            from database import salvar_epi
            novo_id = salvar_epi(
                matricula=payload["matricula"],
                setor=payload["setor"],
                turno=payload["turno"],
                primeira=payload["primeira"],
                data=payload["data"],
                responsavel=payload["responsavel"],
                observacao=payload["observacao"],
                produtos=payload["produtos"],
            )
        except Exception as exc:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar no banco: {exc}")
            return
        if novo_id:
            QMessageBox.information(self, "EPIs", f"Registro de EPIs #{novo_id} inserido.")
            # Reset básico
            self.ed_matricula.clear()
            self.cb_setor.setCurrentIndex(0)
            self.cb_turno.setCurrentIndex(0)
            self.cb_primeira.setCurrentIndex(0)
            self.ed_data.setDate(QDate.currentDate())
            self.ed_resp.clear()
            # self.ed_codigo removido
            self.tab_produtos.setRowCount(0)
            if hasattr(self, "cb_motivo_epi"):
                self.cb_motivo_epi.setCurrentIndex(0)
            self.ed_obs.clear()
            self.ed_obs.setEnabled(False)
            self.ed_matricula.setFocus()
        else:
            QMessageBox.warning(self, "EPIs", "Falha ao inserir EPIs.")

    def _abrir_configuracoes(self) -> None:
        dlg = _EpisConfigDialog(self._catalogo_produtos, parent=self)
        if not dlg.exec():
            return
        novos = dlg.get_data()
        # Validação simples: códigos únicos e não vazios
        cods = [r.get("codigo", "").strip() for r in novos]
        if any(not c for c in cods):
            QMessageBox.warning(self, "Configurações", "Há código vazio.")
            return
        if len(set(cods)) != len(cods):
            QMessageBox.warning(self, "Configurações", "Códigos duplicados não são permitidos.")
            return
        self._catalogo_produtos = novos
        try:
            qtd = substituir_configuracoes_api(self._catalogo_produtos)
        except Exception as exc:
            QMessageBox.warning(self, "Configurações", f"Falha ao salvar no banco: {exc}")
            return
        # Reconstrói os mapas para Código->Produto/Produto->Código e Código->Valor (Decimal com 2 casas)
        self._catalogo_map = {d.get("codigo", ""): d.get("produto", "") for d in self._catalogo_produtos if d.get("codigo")}
        self._produto_map = {d.get("produto", ""): d.get("codigo", "") for d in self._catalogo_produtos if d.get("produto") and d.get("codigo")}
        self._valor_map = {}
        for d in self._catalogo_produtos:
            cod = d.get("codigo")
            val_raw = str(d.get("valor", "") or "").strip()
            if cod:
                try:
                    dec = self._parse_decimal(val_raw)
                    if dec is not None and dec >= Decimal("0"):
                        self._valor_map[cod] = dec.quantize(Decimal("0.01"))
                    else:
                        self._valor_map[cod] = Decimal("0.00")
                except Exception:
                    self._valor_map[cod] = Decimal("0.00")
        # Atualiza listas do autocomplete de códigos e produtos
        try:
            self._refresh_codigo_completer()
            self._refresh_produto_completer()
        except Exception:
            pass
        QMessageBox.information(self, "Configurações", "Catálogo salvo com sucesso.")

    # ----- Catálogo (persistência no banco) ----- #
    def _carregar_catalogo_bd(self) -> None:
        try:
            data = listar_configuracoes_api()
            # Normaliza para List[Dict] (preserva valor para pré-preencher o diálogo)
            self._catalogo_produtos = [
                {
                    "codigo": str(d.get("codigo", "")).strip(),
                    "produto": str(d.get("produto", "")).strip(),
                    "valor": str(d.get("valor", "") or "").strip(),
                }
                for d in (data or [])
            ]
            # Mapas: código->produto, produto->código e código->valor (Decimal com 2 casas)
            self._catalogo_map = {d["codigo"]: d["produto"] for d in self._catalogo_produtos if d.get("codigo")}
            self._produto_map = {d["produto"]: d["codigo"] for d in self._catalogo_produtos if d.get("produto") and d.get("codigo")}
            self._valor_map = {}
            for d in self._catalogo_produtos:
                cod = d.get("codigo")
                val_raw = str(d.get("valor", "") or "").strip()
                if cod:
                    try:
                        dec = self._parse_decimal(val_raw)
                        if dec is not None and dec >= Decimal("0"):
                            self._valor_map[cod] = dec.quantize(Decimal("0.01"))
                        else:
                            self._valor_map[cod] = Decimal("0.00")
                    except Exception:
                        self._valor_map[cod] = Decimal("0.00")
        except Exception as exc:
            self._catalogo_produtos = []
            self._catalogo_map = {}
            self._valor_map = {}
        # Migração leve: se banco estiver vazio, tentar importar do JSON legado uma vez
        if not self._catalogo_produtos:
            try:
                from pathlib import Path
                import json
                legacy = Path(__file__).resolve().parent / "output" / "epis_produtos.json"
                if legacy.exists():
                    with open(legacy, "r", encoding="utf-8") as f:
                        raw = json.load(f)
                    if isinstance(raw, list):
                        itens = []
                        for it in raw:
                            cod = str(it.get("codigo", "")).strip()
                            prod = str(it.get("produto", "")).strip()
                            if cod and prod:
                                itens.append({"codigo": cod, "produto": prod})
                        if itens:
                            substituir_configuracoes_api(itens)
                            self._catalogo_produtos = itens
                            self._catalogo_map = {d["codigo"]: d["produto"] for d in itens if d.get("codigo")}
                            self._produto_map = {d["produto"]: d["codigo"] for d in itens if d.get("produto") and d.get("codigo")}
                            self._valor_map = {d["codigo"]: Decimal("0.00") for d in itens if d.get("codigo")}
            except Exception as _exc:
                # silencioso; apenas loga
                pass

    def _on_item_changed(self, item: QTableWidgetItem) -> None:
        # Quando Código (col 0) muda, preencher Produto (col 1) e recalcular Valor
        # Quando Quantidade (col 2) muda, recalcular Valor
        try:
            if item is None:
                return
            col = item.column()
            row = item.row()
            if col == 0:
                cod = (item.text() or "").strip()
                nome = self._catalogo_map.get(cod, "")
                prod_item = self.tab_produtos.item(row, 1)
                if prod_item is None:
                    prod_item = QTableWidgetItem("")
                    # Mantém editável para permitir busca por Produto
                    self.tab_produtos.setItem(row, 1, prod_item)
                # Evita loop: só atualiza se diferente
                if (prod_item.text() or "") != nome:
                    prod_item.setText(nome)
                # Recalcular valor total da linha
                self._recalcular_valor_linha(row)
            elif col == 1:
                # Produto alterado -> preencher Código correspondente e recalcular
                prod_txt = (item.text() or "").strip()
                # Encontra código por nome do produto
                cod_novo = None
                try:
                    if hasattr(self, "_produto_map"):
                        cod_novo = self._produto_map.get(prod_txt)
                except Exception:
                    cod_novo = None
                it_cod = self.tab_produtos.item(row, 0)
                cod_atual = (it_cod.text() if it_cod else "").strip()
                if cod_novo and cod_novo != cod_atual:
                    if it_cod is None:
                        it_cod = QTableWidgetItem("")
                        self.tab_produtos.setItem(row, 0, it_cod)
                    it_cod.setText(cod_novo)
                # Recalcular valor total da linha em qualquer caso
                self._recalcular_valor_linha(row)
            elif col == 2:
                # Quantidade alterada
                self._recalcular_valor_linha(row)
        except Exception:
            pass

    def _recalcular_valor_linha(self, row: int) -> None:
        try:
            it_cod = self.tab_produtos.item(row, 0)
            it_qtd = self.tab_produtos.item(row, 2)
            it_val = self.tab_produtos.item(row, 3)
            cod = (it_cod.text() if it_cod else "").strip()
            # quantidade
            try:
                qtd = int(it_qtd.text()) if it_qtd and it_qtd.text() else 0
            except Exception:
                qtd = 0
            # valor unitário das configurações (Decimal)
            unit_dec: Decimal = Decimal("0.00")
            if hasattr(self, "_valor_map") and cod:
                try:
                    vm = self._valor_map.get(cod)
                    unit_dec = vm if isinstance(vm, Decimal) else (self._parse_decimal(vm) or Decimal("0.00"))
                except Exception:
                    unit_dec = Decimal("0.00")
            total_dec = (Decimal(max(0, qtd)) * (unit_dec if unit_dec >= Decimal("0") else Decimal("0.00"))).quantize(Decimal("0.01"))
            if it_val is None:
                it_val = QTableWidgetItem(self._format_brl(total_dec))
                it_val.setFlags(it_val.flags() & ~Qt.ItemIsEditable)
                it_val.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tab_produtos.setItem(row, 3, it_val)
            else:
                novo_txt = self._format_brl(total_dec)
                if (it_val.text() or "") != novo_txt:
                    it_val.setText(novo_txt)
        except Exception:
            pass

    def _format_brl(self, valor) -> str:
        v = self._parse_decimal(valor) or Decimal("0.00")
        s = f"{float(v):,.2f}"  # 1,234.56
        s = s.replace(",", "_").replace(".", ",").replace("_", ".")
        return f"R$ {s}"

    def _parse_decimal(self, val) -> Decimal | None:
        """Converte string/num para Decimal aceitando formatos 10, 10.00, 10,00, 1.234,56.
        Retorna None em caso de falha.
        """
        try:
            if val is None or val == "":
                return None
            if isinstance(val, Decimal):
                return val
            if isinstance(val, (int, float)):
                return Decimal(str(val))
            s = str(val).strip().replace(" ", "")
            if "," in s and "." in s:
                s = s.replace(".", "")
                s = s.replace(",", ".")
            elif "," in s:
                s = s.replace(".", "")
                s = s.replace(",", ".")
            return Decimal(s)
        except Exception:
            return None

    # --- Autocomplete para Código ---
    def _setup_codigo_completer(self) -> None:
        """Configura QCompleter na coluna Código da tabela usando códigos do catálogo."""
        try:
            from PySide6.QtWidgets import QCompleter
            from PySide6.QtCore import QStringListModel
        except Exception:
            return
        codigos = sorted(list(getattr(self, "_catalogo_map", {}).keys()))
        try:
            self._codigos_model = QStringListModel(codigos)
        except Exception:
            self._codigos_model = None
        try:
            self._cod_completer = QCompleter(self._codigos_model if self._codigos_model else codigos, self)
            self._cod_completer.setCaseSensitivity(Qt.CaseInsensitive)
            self._cod_completer.setFilterMode(Qt.MatchStartsWith)
        except Exception:
            self._cod_completer = None
        # Delegate para acoplar o completer aos editores da coluna 0
        class _CodigoDelegate(QStyledItemDelegate):
            def __init__(self, completer, parent=None):
                super().__init__(parent)
                self._completer = completer
            def createEditor(self, parent, option, index):
                ed = QLineEdit(parent)
                try:
                    if self._completer:
                        ed.setCompleter(self._completer)
                except Exception:
                    pass
                return ed
        try:
            self.tab_produtos.setItemDelegateForColumn(0, _CodigoDelegate(self._cod_completer, self.tab_produtos))
        except Exception:
            pass

    def _refresh_codigo_completer(self) -> None:
        """Atualiza os itens do completer de códigos após alterar Configurações."""
        try:
            codigos = sorted(list(getattr(self, "_catalogo_map", {}).keys()))
            if hasattr(self, "_codigos_model") and self._codigos_model:
                # Atualiza modelo existente
                self._codigos_model.setStringList(codigos)  # type: ignore[attr-defined]
            elif hasattr(self, "_cod_completer") and self._cod_completer:
                # Recria se necessário
                self._setup_codigo_completer()
        except Exception:
            pass

    # --- Autocomplete para Produto ---
    def _setup_produto_completer(self) -> None:
        """Configura QCompleter na coluna Produto da tabela usando nomes do catálogo."""
        try:
            from PySide6.QtWidgets import QCompleter
            from PySide6.QtCore import QStringListModel
        except Exception:
            return
        produtos = sorted(list(getattr(self, "_produto_map", {}).keys()))
        try:
            self._produtos_model = QStringListModel(produtos)
        except Exception:
            self._produtos_model = None
        try:
            self._prod_completer = QCompleter(self._produtos_model if self._produtos_model else produtos, self)
            self._prod_completer.setCaseSensitivity(Qt.CaseInsensitive)
            # Busca por "contém" para facilitar localizar parte do nome
            self._prod_completer.setFilterMode(Qt.MatchContains)
            # Exibir popup de sugestões
            self._prod_completer.setCompletionMode(self._prod_completer.CompletionMode.PopupCompletion)
        except Exception:
            self._prod_completer = None

        class _ProdutoDelegate(QStyledItemDelegate):
            def __init__(self, completer, parent=None):
                super().__init__(parent)
                self._completer = completer
            def createEditor(self, parent, option, index):
                ed = QLineEdit(parent)
                try:
                    if self._completer:
                        ed.setCompleter(self._completer)
                except Exception:
                    pass
                return ed
        try:
            self.tab_produtos.setItemDelegateForColumn(1, _ProdutoDelegate(self._prod_completer, self.tab_produtos))
        except Exception:
            pass

    def _refresh_produto_completer(self) -> None:
        """Atualiza os itens do completer de produtos após alterar Configurações."""
        try:
            produtos = sorted(list(getattr(self, "_produto_map", {}).keys()))
            if hasattr(self, "_produtos_model") and self._produtos_model:
                self._produtos_model.setStringList(produtos)  # type: ignore[attr-defined]
            elif hasattr(self, "_prod_completer") and self._prod_completer:
                self._setup_produto_completer()
        except Exception:
            pass


from PySide6.QtWidgets import QDialog, QDialogButtonBox


class _EpisConfigDialog(QDialog):
    """Diálogo para editar o catálogo de Código/Produto das EPIs."""
    def __init__(self, data: List[Dict], parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Configurações de EPIs")
        self._data = [
            {"codigo": str(d.get("codigo", "")), "produto": str(d.get("produto", "")), "valor": str(d.get("valor", "") or "")}
            for d in (data or [])
        ]
        self._build()

    def _build(self) -> None:
        lay = QVBoxLayout(self)
        form = QFormLayout()
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        self.tab = QTableWidget(0, 3)
        self.tab.setHorizontalHeaderLabels(["Código", "Produto", "Valor"])
        self.tab.horizontalHeader().setStretchLastSection(True)
        self.tab.setAlternatingRowColors(True)
        # Delegate para aceitar decimais (0-2 casas) na coluna Valor (col 2)
        class _DecimalItemDelegate(QStyledItemDelegate):
            def createEditor(self, parent, option, index):
                ed = QLineEdit(parent)
                # Aceita: 10, 10.0, 10.23, 10,23
                regex = QRegularExpression(r"^\d{1,9}([\.,]\d{1,2})?$")
                ed.setValidator(QRegularExpressionValidator(regex, ed))
                return ed
        self.tab.setItemDelegateForColumn(2, _DecimalItemDelegate(self.tab))
        for row, d in enumerate(self._data):
            self.tab.insertRow(row)
            self.tab.setItem(row, 0, QTableWidgetItem(d.get("codigo", "")))
            self.tab.setItem(row, 1, QTableWidgetItem(d.get("produto", "")))
            # Valor: exibir com até 2 casas decimais (aceita vírgula)
            val_raw = str(d.get("valor", "") or "").strip()
            val_disp = ""
            if val_raw:
                try:
                    from decimal import Decimal
                    s = val_raw.replace(" ", "")
                    if "," in s and "." in s:
                        s = s.replace(".", "").replace(",", ".")
                    elif "," in s:
                        s = s.replace(".", "").replace(",", ".")
                    v = Decimal(s)
                    val_disp = f"{v:.2f}".replace(".", ",")
                except Exception:
                    val_disp = ""
            self.tab.setItem(row, 2, QTableWidgetItem(val_disp))

        row_btn = QHBoxLayout()
        btn_add = QPushButton("+ Adicionar")
        btn_del = QPushButton("Remover Selecionado")
        btn_add.clicked.connect(self._add_row)
        btn_del.clicked.connect(self._del_row)
        row_btn.addWidget(btn_add)
        row_btn.addWidget(btn_del)
        row_btn.addStretch(1)

        form.addRow("&Catálogo:", self.tab)
        lay.addLayout(form)
        lay.addLayout(row_btn)

        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(self.accept)
        btns.rejected.connect(self.reject)
        lay.addWidget(btns)

    def _add_row(self) -> None:
        r = self.tab.rowCount()
        self.tab.insertRow(r)
        self.tab.setItem(r, 0, QTableWidgetItem(""))
        self.tab.setItem(r, 1, QTableWidgetItem(""))
        self.tab.setItem(r, 2, QTableWidgetItem(""))

    def _del_row(self) -> None:
        r = self.tab.currentRow()
        if r >= 0:
            self.tab.removeRow(r)

    def get_data(self) -> List[Dict]:
        out: List[Dict] = []
        for r in range(self.tab.rowCount()):
            it_cod = self.tab.item(r, 0)
            it_prod = self.tab.item(r, 1)
            it_val = self.tab.item(r, 2)
            cod = (it_cod.text() if it_cod else "").strip()
            prod = (it_prod.text() if it_prod else "").strip()
            val = (it_val.text() if it_val else "").strip()
            # Normaliza valor: decimal com ponto, 2 casas; inválido vira None
            valor_norm = None
            if val:
                s = val.strip().replace(" ", "")
                if "," in s and "." in s:
                    s = s.replace(".", "").replace(",", ".")
                elif "," in s:
                    s = s.replace(".", "").replace(",", ".")
                try:
                    from decimal import Decimal
                    v = Decimal(s)
                    if v >= 0:
                        valor_norm = f"{v:.2f}"
                except Exception:
                    valor_norm = None
            if cod or prod:
                out.append({"codigo": cod, "produto": prod, "valor": valor_norm})
        return out

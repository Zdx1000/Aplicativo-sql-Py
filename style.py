"""
style.py — Definições de cores e estilos (QSS) do aplicativo

Este módulo centraliza as cores e estilos para facilitar manutenção.
- Paletas (QPalette): base de cores para Claro e Escuro
- QSS do cabeçalho "Bloqueado" (header da página)
- QSS da página de Consultas
- QSS da Slimbar (menu lateral)
- QSS adicionais por tema (claro/escuro)
- QSS de foco para os campos da página Bloqueado (por tema)
"""
from __future__ import annotations

# Importações locais apenas dentro das funções para evitar custo em import prematuro

# ---------------- Paletas ---------------- #

def build_palette_claro():
    """Retorna QPalette para o Modo Claro.
    - Window/Base/Button: tons claros
    - Text/ButtonText: cinza escuro (boa leitura)
    - Highlight/HighlightedText: amarelo suave/Preto
    """
    from PySide6.QtGui import QPalette, QColor
    pal = QPalette()
    # Fundos claros
    pal.setColor(QPalette.ColorRole.Window, QColor(255, 255, 252))
    pal.setColor(QPalette.ColorRole.Base, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(250, 250, 245))
    pal.setColor(QPalette.ColorRole.Button, QColor(255, 255, 250))
    # Textos padrão escuros (como no tema claro do Windows)
    pal.setColor(QPalette.ColorRole.WindowText, QColor(20, 20, 20))
    pal.setColor(QPalette.ColorRole.Text, QColor(20, 20, 20))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(20, 20, 20))
    pal.setColor(QPalette.ColorRole.ToolTipText, QColor(20, 20, 20))
    # Placeholder levemente acinzentado
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(120, 120, 120))
    # Seleção (highlight) padrão do Windows (azul) com texto branco
    pal.setColor(QPalette.ColorRole.Highlight, QColor(0, 120, 215))  # #0078d7
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    return pal


def build_palette_escuro():
    """Retorna QPalette para o Modo Escuro.
    - Window/Base/Button: tons de cinza escuros
    - Text/ButtonText: claros
    - Highlight/HighlightedText: amarelo/Preto
    """
    from PySide6.QtGui import QPalette, QColor
    pal = QPalette()
    pal.setColor(QPalette.ColorRole.Window, QColor(30, 34, 40))
    pal.setColor(QPalette.ColorRole.Base, QColor(40, 44, 52))
    pal.setColor(QPalette.ColorRole.AlternateBase, QColor(48, 52, 60))
    pal.setColor(QPalette.ColorRole.Text, QColor(255, 255, 255))
    pal.setColor(QPalette.ColorRole.Button, QColor(50, 56, 66))
    pal.setColor(QPalette.ColorRole.ButtonText, QColor(235, 235, 235))
    # Seleção (highlight) em azul escuro com texto branco
    pal.setColor(QPalette.ColorRole.Highlight, QColor(8, 1, 56))
    pal.setColor(QPalette.ColorRole.HighlightedText, QColor(255, 255, 255))
    # Placeholder em branco fosco (aprox. 60% opacidade)
    pal.setColor(QPalette.ColorRole.PlaceholderText, QColor(255, 255, 255, 153))

    return pal


# ---------------- QSS do cabeçalho da página Bloqueado ---------------- #
# Onde aplica: IDs `HeaderBloqueado`, `TituloWrap`, `DecorLine`, `HelpBloqueado`,
# e o rótulo `TituloBloqueado` + ícone `IconeBloqueado`.
QSS_HEADER_BLOQUEADO = """
#HeaderBloqueado { 
    /* Gradiente mais profissional (indigo → púrpura) */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:0   #0b1f4a,   /* azul escuro */
    stop:0.5 #60a5fa,   /* azul claro  */
    stop:1   #ffffff    /* branco      */
    );
    border-radius: 18px; 
    padding: 12px 16px; 
}
#TituloWrap { 
    /* Pastilha translúcida para contraste do título */
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.92), stop:1 rgba(255,255,255,0.78)); 
    border: 1px solid rgba(255,255,255,0.7); 
    border-radius: 30px; 
}
#TituloWrap:hover { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.97), stop:1 rgba(255,255,255,0.88)); 
}
#TituloWrap #TituloBloqueado { 
    font-size: 28px; 
    font-weight: 900; 
    color: #312e81; /* indigo-900 para melhor leitura */ 
    padding: 4px 12px;
}
#IconeBloqueado {
    font-size: 32px;
    color: #4338ca; /* indigo-700 */
    padding: 2px;
}
#DecorLine { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255,255,255,0.55), stop:1 rgba(255,255,255,0.3)); 
    min-height: 3px; 
    max-height: 3px; 
    border: none; 
    border-radius: 2px; 
}
QPushButton#HelpBloqueado { 
    padding: 10px 20px; 
    border-radius: 25px; 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:1   #0b1f4a    /* branco      */
    );
    border: 1px solid rgba(59,130,246,0.45);
    color: #ffffff; 
    font-weight: 700; 
    font-size: 13px; 
}
QPushButton#HelpBloqueado:hover { 
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
    stop:1   #1660ba    /* branco      */
    );
}
QPushButton#HelpBloqueado:pressed { 
    background: #60a5fa; 
}
"""


# ---------------- QSS base para formulário (página Bloqueado) ---------------- #
# Onde aplica: widgets genéricos, campos e botões do formulário.
QSS_FORMULARIO_BASE = """
QWidget { font-family: 'Segoe UI', Arial; font-size: 13px; }
QLineEdit, QTextEdit, QComboBox { border: 1px solid #b8b8b8; border-radius: 4px; padding: 4px; }
QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #7aa7c7; }
QPushButton { border: 1px solid #007acc; background: #007acc; color: white; padding: 6px 14px; border-radius: 4px; }
QPushButton:hover { background: #0281d6; }
QPushButton:pressed { background: #0063a8; }
QPushButton#danger { background: #b00020; border-color: #b00020; }
QPushButton#danger:hover { background: #c51e35; }
QLabel#feedbackLabel { padding: 4px 6px; border-radius: 4px; background: #e8f4ff; color: #0a3d62; }
QLabel#feedbackLabel[erro="true"] { background: #ffe8ec; color: #b00020; }
"""


# ---------------- QSS da página Consultas ---------------- #
# Onde aplica: campos, tabela e status da página de consultas.
QSS_CONSULTAS_PAGE = """
#PaginaConsultas QLineEdit { padding:6px 8px; }
#PaginaConsultas #TabelaConsultas { background:#ffffff; border:1px solid #b7d9ef; gridline-color:#bababa; color:#000; alternate-background-color:#e6f3fc; }
#PaginaConsultas #TabelaConsultas QHeaderView::section { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3ca4dc, stop:1 #237fb3); color:#ffffff; padding:4px 6px; border:1px solid #1d6d97; font-weight:600; }
#PaginaConsultas #StatusConsultaLabel { color:#666; padding:4px 2px; }
"""


# ---------------- QSS da Slimbar (menu lateral) ---------------- #
# Onde aplica: menu lateral com botões e labels de status/versão.
QSS_SLIMBAR_BASE = """
#Slimbar {
    background: #e8eff9;
    border-right: 1px solid #c9d5e7;
}

#Slimbar #ToggleMenu {
    color: #0f2646;
    font-weight: 600;
    text-align: left;
    padding: 12px 20px;
    border-radius: 14px;
    border: 1px solid rgba(16, 52, 87, 0.08);
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #fcffff,
        stop:1 #e5f1ff
    );
}
#Slimbar #ToggleMenu[collapsed="true"] {
    text-align: center;
    padding: 12px;
    border-radius: 18px;
}
#Slimbar #ToggleMenu:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #ffffff,
        stop:1 #d7e8ff
    );
    border-color: rgba(32, 86, 142, 0.25);
}

#Slimbar #SlimHeaderCard,
#Slimbar #SlimNavCard,
#Slimbar #SlimFooterCard {
    background: rgba(255, 255, 255, 0.98);
    border: 1px solid rgba(9, 31, 58, 0.08);
    border-radius: 22px;
}

#Slimbar #SlimHeaderCard[collapsed="true"],
#Slimbar #SlimNavCard[collapsed="true"],
#Slimbar #SlimFooterCard[collapsed="true"] {
    background: transparent;
    border-color: transparent;
}

#Slimbar QLabel#SlimSectionLabel {
    font-size: 11px;
    letter-spacing: 0.4px;
    text-transform: uppercase;
    font-weight: 700;
    color: #4a678c;
}

#Slimbar QLineEdit#SlimSearchField {
    background: rgba(233, 241, 252, 0.9);
    border: 1px solid rgba(12, 52, 86, 0.14);
    border-radius: 12px;
    padding: 8px 14px;
    color: #0f2646;
    selection-background-color: #2a72f8;
    selection-color: #ffffff;
}
#Slimbar QLineEdit#SlimSearchField:focus {
    background: #ffffff;
    border-color: rgba(42, 114, 248, 0.55);
    box-shadow: 0 0 0 3px rgba(42, 114, 248, 0.15);
}

#Slimbar QLabel#SlimEmptyLabel {
    color: #6a7f9b;
    font-style: italic;
    background: rgba(232, 243, 255, 0.65);
    border-radius: 14px;
    padding: 12px 10px;
}

#Slimbar QScrollArea#SlimNavScroll {
    border: none;
    background: transparent;
}
#Slimbar QScrollArea#SlimNavScroll QWidget {
    background: transparent;
}

#Slimbar #SlimNavCard QPushButton {
    color: #142a4a;
    background: transparent;
    text-align: left;
    padding: 10px 16px;
    border-radius: 14px;
    border: 1px solid transparent;
    font-weight: 520;
    margin: 2px 0;
}
#Slimbar #SlimNavCard QPushButton:hover {
    background: rgba(34, 118, 227, 0.12);
    border-color: rgba(34, 118, 227, 0.24);
    color: #0d47a1;
}
#Slimbar #SlimNavCard QPushButton:checked,
#Slimbar #SlimNavCard QPushButton:pressed {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
        stop:0 #1a73e8,
        stop:1 #0d47a1
    );
    color: #ffffff;
    border-color: transparent;
    font-weight: 650;
}
#Slimbar #SlimNavCard[collapsed="true"] QPushButton {
    padding: 12px;
    border-radius: 18px;
    margin: 4px 0;
    text-align: center;
}

#PlaceholderLabel { color: #66717f; font-size: 17px; }

#Slimbar #AppName { font-size: 18px; font-weight: 800; color: #14203a; }
#Slimbar #AppSubtitle {
    font-size: 12px;
    color: #5b6f86;
    font-weight: 500;
}
#Slimbar #AppIcon {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4285f4, stop:1 #1976d2);
    border-radius: 12px;
    padding: 6px;
}

#Slimbar #UserLabel {
    font-size: 11px;
    font-weight: 700;
    color: #1050a1;
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e3f2fd, stop:1 #f0f4ff);
    border: 1px solid rgba(23, 78, 143, 0.18);
    border-radius: 12px;
    padding: 8px 12px;
}
#Slimbar #StatusLabel {
    font-size: 11px;
    color: #2e7d32;
    font-weight: 500;
}
#Slimbar #VersionLabel {
    font-size: 10px;
    color: #8694a6;
    font-weight: 500;
}
"""


# ---------------- QSS adicional por tema ---------------- #
# Onde aplica: reforça estilos por tema, incluindo Slimbar, página de Consultas e
# cores de texto das páginas Bloqueado/Configurações.

def qss_tema_extra(modo: str) -> str:
    if modo == "escuro":
        return (
            """
            /* Slimbar em tema escuro */
            #Slimbar { background:#0d1118; border-right:1px solid #1d2430; }
            #Slimbar #ToggleMenu {
                color:#dce6f4;
                background:rgba(255,255,255,0.06);
                border:1px solid rgba(99,132,177,0.26);
                border-radius:14px;
                padding:12px 20px;
                text-align:left;
                font-weight:600;
            }
            #Slimbar #ToggleMenu[collapsed="true"] {
                text-align:center;
                padding:12px;
                border-radius:18px;
            }
            #Slimbar #ToggleMenu:hover {
                background:rgba(255,255,255,0.12);
                border-color:rgba(110,168,254,0.45);
            }
            #Slimbar #SlimHeaderCard,
            #Slimbar #SlimNavCard,
            #Slimbar #SlimFooterCard {
                background:rgba(20,27,37,0.94);
                border:1px solid rgba(110,168,254,0.12);
                border-radius:22px;
            }
            #Slimbar #SlimHeaderCard[collapsed="true"],
            #Slimbar #SlimNavCard[collapsed="true"],
            #Slimbar #SlimFooterCard[collapsed="true"] {
                background:transparent;
                border-color:transparent;
            }
            #Slimbar QLabel#SlimSectionLabel {
                color:#88a2c7;
            }
            #Slimbar QLineEdit#SlimSearchField {
                background:rgba(19,33,50,0.85);
                border:1px solid rgba(116,147,196,0.25);
                border-radius:12px;
                padding:8px 14px;
                color:#e4ecfb;
                selection-background-color:#3c7bff;
                selection-color:#ffffff;
            }
            #Slimbar QLineEdit#SlimSearchField:focus {
                background:rgba(27,45,68,0.95);
                border-color:rgba(110,168,254,0.55);
                box-shadow:0 0 0 3px rgba(110,168,254,0.18);
            }
            #Slimbar QLabel#SlimEmptyLabel {
                color:#97abc9;
                background:rgba(35,50,71,0.65);
            }
            #Slimbar #SlimNavCard QPushButton {
                color:#dce6f8;
                background:transparent;
                text-align:left;
                padding:10px 16px;
                border-radius:14px;
                border:1px solid transparent;
                margin:2px 0;
                font-weight:520;
            }
            #Slimbar #SlimNavCard QPushButton:hover {
                background:rgba(110,168,254,0.18);
                border-color:rgba(110,168,254,0.35);
                color:#f7fbff;
            }
            #Slimbar #SlimNavCard QPushButton:checked,
            #Slimbar #SlimNavCard QPushButton:pressed {
                background:qlineargradient(x1:0,y1:0,x2:1,y2:1,
                    stop:0 #4b7fff,
                    stop:1 #2057c8
                );
                color:#ffffff;
                border-color:transparent;
                font-weight:650;
            }
            #Slimbar #SlimNavCard[collapsed="true"] QPushButton {
                padding:12px;
                border-radius:18px;
                text-align:center;
                margin:4px 0;
            }
            #PlaceholderLabel { color:#9aa2af; }
            #Slimbar #AppName { color:#f1f5ff; }
            #Slimbar #AppSubtitle { color:#94a7c6; }
            #Slimbar #UserLabel {
                background:rgba(37,52,74,0.75);
                color:#e6edf7;
                border:1px solid rgba(110,168,254,0.32);
            }
            #Slimbar #StatusLabel { color:#7ad38b; }
            #Slimbar #VersionLabel { color:#7c8caa; }

            /* Inputs (escuro) — unificar com o estilo do Bloqueado */
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox,
            QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QTimeEdit {
                background: #2b3138;
                color: #ffffff;
                border: 1px solid #4a515b;
                border-radius: 6px;
                padding: 6px 8px;
                selection-background-color: #0b1f4a;
                selection-color: #ffffff;
            }
            QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {
                color: rgba(255,255,255,0.6);
            }
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus,
            QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus, QDateTimeEdit:focus, QTimeEdit:focus {
                background: #3a4149; /* igual foco do Bloqueado */
                border: 1px solid #e0aa00;
                color: #ffffff;
            }
            /* Popup e drop-downs coerentes */
            QComboBox QAbstractItemView {
                background: #2b3138;
                color: #ffffff;
                selection-background-color: #3a4149;
                selection-color: #ffffff;
                border: 1px solid #4a515b;
            }
            QComboBox::drop-down,
            QDateEdit::drop-down, QDateTimeEdit::drop-down, QTimeEdit::drop-down {
                background: #2b3138;
                border-left: 1px solid #4a515b;
            }
            QSpinBox::up-button, QSpinBox::down-button,
            QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
                background: #2b3138;
                border: 1px solid #4a515b;
                border-radius: 3px;
            }
            /* Login/Registro também seguem o padrão no escuro */
            QDialog#AuthDialog QLineEdit,
            QDialog#AuthDialog QComboBox {
                background: #2b3138;
                color: #ffffff;
                border: 1px solid #4a515b;
                border-radius: 6px;
                padding: 6px 8px;
            }
            QDialog#AuthDialog QLineEdit:focus,
            QDialog#AuthDialog QComboBox:focus {
                background: #3a4149;
                border: 1px solid #e0aa00;
                color: #ffffff;
            }
            /* Header Bloqueado (override específico do modo escuro) */
            #HeaderBloqueado { 
                /* Gradiente mais profissional (indigo → púrpura) */
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0   #0b1f4a,   /* azul escuro */
                stop:0.5 #6e7585,   /* azul claro  */
                stop:1   #0b1f4a    /* branco      */
                );
                border-radius: 18px; 
                padding: 12px 16px; 
            }
            #TituloWrap { 
                /* Pastilha translúcida para contraste do título */
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.92), stop:1 rgba(255,255,255,0.78)); 
                border: 1px solid rgba(255,255,255,0.7); 
                border-radius: 30px; 
            }
            #TituloWrap:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 rgba(255,255,255,0.97), stop:1 rgba(255,255,255,0.88)); 
            }
            #TituloWrap #TituloBloqueado { 
                font-size: 28px; 
                font-weight: 900; 
                color: #312e81; /* indigo-900 para melhor leitura */ 
                padding: 4px 12px;
            }
            #IconeBloqueado {
                font-size: 32px;
                color: #4338ca; /* indigo-700 */
                padding: 2px;
            }
            #DecorLine { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 rgba(255,255,255,0.55), stop:1 rgba(255,255,255,0.3)); 
                min-height: 3px; 
                max-height: 3px; 
                border: none; 
                border-radius: 2px; 
            }
            QPushButton#HelpBloqueado { 
                padding: 10px 20px; 
                border-radius: 25px; 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:1   #0b1f4a    /* branco      */
                );
                border: 1px solid rgba(0, 0, 0, 1);
                color: #ffffff; 
                font-weight: 700; 
                font-size: 13px; 
            }
            QPushButton#HelpBloqueado:hover { 
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:1   #191c24    /* branco      */
                );
            }
            QPushButton#HelpBloqueado:pressed { 
                background: #000000; 
            }
            /* Consultas (escuro) — override exato solicitado */
            #PaginaConsultas QLineEdit { padding:6px 8px; }
            #PaginaConsultas QLabel { color:#ffffff; }
            #TabelaConsultas { background:#000000; border:1px solid #b7d9ef; gridline-color:#bababa; color:#ffffff; alternate-background-color:#e6f3fc; }
            #TabelaConsultas QHeaderView::section { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #3ca4dc, stop:1 #237fb3); color:#ffffff; padding:4px 6px; border:1px solid #1d6d97; font-weight:600; }
            #StatusConsultaLabel { color:#666; padding:4px 2px; }
            #StatusConsultaLabel { color:#ffffff; padding:4px 2px; }
            /* Páginas Bloqueado/Config: textos claros */
            #PaginaBloqueado, #PaginaBloqueado * { color:#fff; }
            #PaginaConfiguracoes, #PaginaConfiguracoes * { color:#fff; }
            /* Páginas solicitadas: texto branco no modo escuro */
            #PaginaGrafico, #PaginaGrafico * { color:#ffffff; }
            #PaginaEPIs, #PaginaEPIs * { color:#ffffff; }
            #PaginaAlmoxarifado, #PaginaAlmoxarifado * { color:#ffffff; }
            #PaginaMonitoramento, #PaginaMonitoramento * { color:#ffffff; }
            #PaginaSenhaCorte, #PaginaSenhaCorte * { color:#ffffff; }
            #PaginaConsolidado, #PaginaConsolidado * { color:#ffffff; }
            /* Consolidado: fundo cinza escuro e tabela escura no modo escuro */
            #PaginaConsolidado { background: #1f2329; }
            #PaginaConsolidado #TabelaConsultas {
                background: #2b3138;
                color: #ffffff;
                border: 1px solid #3a4149;
                gridline-color: #3f4751;
                alternate-background-color: #242a31;
            }
            #PaginaConsolidado #TabelaConsultas QHeaderView::section {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #0f141a, stop:1 #1b2027);
                color: #ffffff;
                padding: 4px 6px;
                border: 1px solid #2a2f36;
                font-weight: 600;
            }
            /* Garante o título branco nos headers dessas páginas */
            #PaginaGrafico #TituloBloqueado,
            #PaginaEPIs #TituloBloqueado,
            #PaginaAlmoxarifado #TituloBloqueado,
            #PaginaMonitoramento #TituloBloqueado,
            #PaginaSenhaCorte #TituloBloqueado,
            #PaginaConsolidado #TituloBloqueado { color:#ffffff; }
            /* Diálogos de configuração (modo escuro) */
            QDialog#ConfigEpiDialog,
            QDialog#ResponsaveisDialog {
                background: #11151c;
                border: 1px solid #262c36;
                border-radius: 22px;
            }
            #PaginaConfiguracoes {
                background: #0d1117;
            }
            #ConfigHero {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #121a2b, stop:1 #1c2a3f);
                border: 1px solid #1f2b3d;
                border-radius: 20px;
            }
            #ConfigHeroIcon {
                font-size: 42px;
            }
            #ConfigHeroTitle {
                color: #f5f6f8;
                font-size: 26px;
                font-weight: 900;
                letter-spacing: 0.4px;
            }
            #ConfigHeroSubtitle {
                color: #a9b3c3;
                font-size: 13px;
            }
            #ConfigToggleWrap {
                background: rgba(17,23,34,0.9);
                border: 1px solid #223048;
                border-radius: 14px;
            }
            #ConfigToggleLabel {
                color: #d4dbea;
                font-size: 12px;
                font-weight: 600;
                text-transform: uppercase;
                letter-spacing: 1.1px;
            }
            QPushButton#ConfigToggleButton {
                background: rgba(35,47,68,0.6);
                border: 1px solid rgba(110,168,254,0.25);
                border-radius: 10px;
                color: #e5ecf6;
                padding: 10px 18px;
                font-weight: 600;
            }
            QPushButton#ConfigToggleButton:hover {
                background: rgba(110,168,254,0.18);
            }
            QPushButton#ConfigToggleButton:checked {
                background: rgba(110,168,254,0.32);
                border: 1px solid #6ea8fe;
                color: #ffffff;
            }
            #ConfigCard {
                background: rgba(17,23,34,0.92);
                border: 1px solid #1e2634;
                border-radius: 18px;
            }
            #ConfigCardTitle {
                color: #f5f6f8;
                font-size: 18px;
                font-weight: 800;
            }
            #ConfigCardSubtitle {
                color: #94a2b8;
                font-size: 13px;
            }
            QLineEdit#ConfigReadOnlyField {
                background: rgba(255,255,255,0.05);
                border: 1px solid #303a4a;
                border-radius: 10px;
                color: #dfe6f3;
                padding: 8px 12px;
            }
            QPushButton#ConfigPrimaryButton {
                background: #e0aa00;
                border: none;
                border-radius: 12px;
                color: #11161f;
                padding: 10px 20px;
                font-weight: 800;
            }
            QPushButton#ConfigPrimaryButton:hover { background: #f0b800; }
            QPushButton#ConfigPrimaryButton:pressed { background: #c99600; }
            QPushButton#ConfigDangerButton {
                background: #9c1f2f;
                border: none;
                border-radius: 12px;
                color: #ffecef;
                padding: 10px 18px;
                font-weight: 700;
            }
            QPushButton#ConfigDangerButton:hover { background: #b32a3c; }
            QPushButton#ConfigDangerButton:pressed { background: #7d1623; }
            QPushButton#ConfigGhostButton {
                background: transparent;
                border: 1px solid #334059;
                border-radius: 10px;
                color: #c6d1e3;
                padding: 9px 16px;
                font-weight: 600;
            }
            QPushButton#ConfigGhostButton:hover { background: rgba(255,255,255,0.08); }
            QPushButton#ConfigGhostButton:pressed { background: rgba(255,255,255,0.12); }
            QPushButton#ConfigListButton {
                background: rgba(32,41,58,0.75);
                border: 1px solid rgba(98,123,168,0.35);
                border-radius: 10px;
                color: #e8eef9;
                padding: 8px 14px;
                text-align: left;
                font-weight: 600;
            }
            QPushButton#ConfigListButton:hover { background: rgba(110,168,254,0.18); }
            QPushButton#ConfigListButton:pressed { background: rgba(110,168,254,0.28); }
            QScrollArea#ConfigListScroll {
                border: 1px solid #202a3a;
                border-radius: 14px;
                background: rgba(14,19,28,0.65);
            }
            QScrollArea#ConfigListScroll QWidget {
                background: transparent;
            }
            #ConfigDialogHeader {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #1c2432, stop:1 #28374d);
                border-radius: 18px;
                border: 1px solid rgba(255,255,255,0.05);
            }
            #ConfigDialogIcon {
                font-size: 36px;
                color: #f5f6f8;
            }
            #ConfigDialogTitle {
                font-size: 24px;
                font-weight: 800;
                color: #f5f6f8;
                letter-spacing: 0.3px;
            }
            #ConfigDialogSubtitle {
                color: #a9b3c3;
                font-size: 13px;
            }
            #ConfigDialogCard {
                background: rgba(18,22,30,0.95);
                border: 1px solid #262c36;
                border-radius: 18px;
            }
            QLabel#ConfigDialogInfo {
                color: #d4dbea;
                font-weight: 600;
                font-size: 13px;
            }
            QLabel#ConfigDialogHint {
                color: #8f9bad;
                font-size: 12px;
            }
            QTableWidget#ConfigDialogTable {
                background: #181d26;
                color: #f3f6ff;
                border: 1px solid #2f3540;
                alternate-background-color: #151922;
                gridline-color: #2f3540;
                selection-background-color: rgba(224,170,0,0.28);
                selection-color: #ffffff;
            }
            QTableWidget#ConfigDialogTable::item:selected {
                background: rgba(224,170,0,0.34);
                color: #ffffff;
            }
            QTableWidget#ConfigDialogTable QHeaderView::section {
                background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #313d51, stop:1 #232c3a);
                color: #f1f5ff;
                border: none;
                padding: 8px 12px;
                font-weight: 600;
            }
            QPushButton#ConfigDialogAdd {
                background: #1f7a47;
                border: 1px solid #2d9f61;
                border-radius: 10px;
                color: #edfff3;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton#ConfigDialogAdd:hover { background: #2c985b; }
            QPushButton#ConfigDialogAdd:pressed { background: #1c653c; }
            QPushButton#ConfigDialogRemove {
                background: #7a1f2a;
                border: 1px solid #a63140;
                border-radius: 10px;
                color: #ffecef;
                padding: 8px 16px;
                font-weight: 600;
            }
            QPushButton#ConfigDialogRemove:hover { background: #98303c; }
            QPushButton#ConfigDialogRemove:pressed { background: #6b1822; }
            QPushButton#ConfigDialogOk {
                background: #e0aa00;
                border: none;
                border-radius: 12px;
                color: #10141d;
                padding: 10px 20px;
                font-weight: 800;
                letter-spacing: 0.4px;
            }
            QPushButton#ConfigDialogOk:hover { background: #f0b800; }
            QPushButton#ConfigDialogOk:pressed { background: #c99600; }
            QPushButton#ConfigDialogCancel {
                background: transparent;
                border: 1px solid #3a4149;
                border-radius: 12px;
                color: #d2dae5;
                padding: 10px 20px;
                font-weight: 600;
            }
            QPushButton#ConfigDialogCancel:hover {
                background: rgba(255,255,255,0.06);
            }
            """
        )
    elif modo == "claro":
        # Overrides leves para inputs no claro (mantém a base mas uniformiza padding/borda)
        return """
        QLineEdit, QTextEdit, QPlainTextEdit, QComboBox,
        QSpinBox, QDoubleSpinBox, QDateEdit, QDateTimeEdit, QTimeEdit {
            background: #ffffff;
            color: #222222;
            border: 1px solid #b8b8b8;
            border-radius: 6px;
            padding: 6px 8px;
            selection-background-color: #cfe8ff;
            selection-color: #000000;
        }
        QLineEdit::placeholder, QTextEdit::placeholder, QPlainTextEdit::placeholder {
            color: #7a7a7a;
        }
        /* Diálogos de configuração (modo claro) */
        QDialog#ConfigEpiDialog,
        QDialog#ResponsaveisDialog {
            background: #f6f9ff;
            border: 1px solid #dce6f5;
            border-radius: 22px;
        }
        #PaginaConfiguracoes {
            background: #f5f7fb;
        }
        #ConfigHero {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #f1f6ff, stop:1 #e1ecff);
            border: 1px solid #cfdcf3;
            border-radius: 20px;
        }
        #ConfigHeroIcon {
            font-size: 42px;
        }
        #ConfigHeroTitle {
            color: #1c2f4a;
            font-size: 26px;
            font-weight: 900;
            letter-spacing: 0.4px;
        }
        #ConfigHeroSubtitle {
            color: #4a5d7a;
            font-size: 13px;
        }
        #ConfigToggleWrap {
            background: rgba(255,255,255,0.92);
            border: 1px solid #d7e3f4;
            border-radius: 14px;
        }
        #ConfigToggleLabel {
            color: #385071;
            font-size: 12px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.1px;
        }
        QPushButton#ConfigToggleButton {
            background: rgba(230,238,255,0.9);
            border: 1px solid rgba(32,123,255,0.25);
            border-radius: 10px;
            color: #1f3b5b;
            padding: 10px 18px;
            font-weight: 600;
        }
        QPushButton#ConfigToggleButton:hover {
            background: rgba(32,123,255,0.16);
        }
        QPushButton#ConfigToggleButton:checked {
            background: rgba(32,123,255,0.28);
            border: 1px solid #207bff;
            color: #0b1f4a;
        }
        #ConfigCard {
            background: rgba(255,255,255,0.98);
            border: 1px solid #dbe6f7;
            border-radius: 18px;
        }
        #ConfigCardTitle {
            color: #1b2d48;
            font-size: 18px;
            font-weight: 800;
        }
        #ConfigCardSubtitle {
            color: #4f6383;
            font-size: 13px;
        }
        QLineEdit#ConfigReadOnlyField {
            background: rgba(246,249,255,0.9);
            border: 1px solid #d1ddef;
            border-radius: 10px;
            color: #233552;
            padding: 8px 12px;
        }
        QPushButton#ConfigPrimaryButton {
            background: #f4b400;
            border: none;
            border-radius: 12px;
            color: #1f2937;
            padding: 10px 20px;
            font-weight: 800;
        }
        QPushButton#ConfigPrimaryButton:hover { background: #ffca1a; }
        QPushButton#ConfigPrimaryButton:pressed { background: #d1a200; }
        QPushButton#ConfigDangerButton {
            background: #c62839;
            border: none;
            border-radius: 12px;
            color: #ffffff;
            padding: 10px 18px;
            font-weight: 700;
        }
        QPushButton#ConfigDangerButton:hover { background: #dd3a4e; }
        QPushButton#ConfigDangerButton:pressed { background: #a5212f; }
        QPushButton#ConfigGhostButton {
            background: transparent;
            border: 1px solid #bfd0e8;
            border-radius: 10px;
            color: #39506f;
            padding: 9px 16px;
            font-weight: 600;
        }
        QPushButton#ConfigGhostButton:hover { background: rgba(36,97,255,0.12); }
        QPushButton#ConfigGhostButton:pressed { background: rgba(36,97,255,0.18); }
        QPushButton#ConfigListButton {
            background: rgba(235,242,255,0.92);
            border: 1px solid rgba(32,123,255,0.2);
            border-radius: 10px;
            color: #1f3552;
            padding: 8px 14px;
            text-align: left;
            font-weight: 600;
        }
        QPushButton#ConfigListButton:hover { background: rgba(32,123,255,0.18); }
        QPushButton#ConfigListButton:pressed { background: rgba(32,123,255,0.28); }
        QScrollArea#ConfigListScroll {
            border: 1px solid #d6e2f6;
            border-radius: 14px;
            background: rgba(244,248,255,0.8);
        }
        QScrollArea#ConfigListScroll QWidget {
            background: transparent;
        }
        #ConfigDialogHeader {
            background: qlineargradient(x1:0,y1:0,x2:1,y2:1, stop:0 #e8f0ff, stop:1 #d4e4ff);
            border-radius: 18px;
            border: 1px solid rgba(15,64,128,0.08);
        }
        #ConfigDialogIcon {
            font-size: 36px;
            color: #1f3b5b;
        }
        #ConfigDialogTitle {
            font-size: 24px;
            font-weight: 800;
            color: #10223b;
            letter-spacing: 0.3px;
        }
        #ConfigDialogSubtitle {
            color: #4c5d73;
            font-size: 13px;
        }
        #ConfigDialogCard {
            background: rgba(255,255,255,0.98);
            border: 1px solid #d7e4f6;
            border-radius: 18px;
        }
        QLabel#ConfigDialogInfo {
            color: #203657;
            font-weight: 600;
            font-size: 13px;
        }
        QLabel#ConfigDialogHint {
            color: #5e728f;
            font-size: 12px;
        }
        QTableWidget#ConfigDialogTable {
            background: #ffffff;
            color: #1f2937;
            border: 1px solid #d7e3f4;
            alternate-background-color: #f5f9ff;
            gridline-color: #ccd9ed;
            selection-background-color: rgba(32,123,255,0.16);
            selection-color: #0b1f4a;
        }
        QTableWidget#ConfigDialogTable::item:selected {
            background: rgba(32,123,255,0.22);
            color: #0b1f4a;
        }
        QTableWidget#ConfigDialogTable QHeaderView::section {
            background: qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #edf3ff, stop:1 #dbe6ff);
            color: #10223b;
            border: none;
            padding: 8px 12px;
            font-weight: 600;
        }
        QPushButton#ConfigDialogAdd {
            background: #1a7d36;
            border: 1px solid #239d46;
            border-radius: 10px;
            color: #ffffff;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton#ConfigDialogAdd:hover { background: #21994a; }
        QPushButton#ConfigDialogAdd:pressed { background: #16672f; }
        QPushButton#ConfigDialogRemove {
            background: #c62839;
            border: 1px solid #e03f52;
            border-radius: 10px;
            color: #ffffff;
            padding: 8px 16px;
            font-weight: 600;
        }
        QPushButton#ConfigDialogRemove:hover { background: #dd3a4e; }
        QPushButton#ConfigDialogRemove:pressed { background: #a5212f; }
        QPushButton#ConfigDialogOk {
            background: #f4b400;
            border: none;
            border-radius: 12px;
            color: #1f2937;
            padding: 10px 20px;
            font-weight: 800;
            letter-spacing: 0.4px;
        }
        QPushButton#ConfigDialogOk:hover { background: #ffca1a; }
        QPushButton#ConfigDialogOk:pressed { background: #d1a200; }
        QPushButton#ConfigDialogCancel {
            background: transparent;
            border: 1px solid #b9c8de;
            border-radius: 12px;
            color: #3c4a60;
            padding: 10px 20px;
            font-weight: 600;
        }
        QPushButton#ConfigDialogCancel:hover {
            background: rgba(36,97,255,0.08);
        }
        """
    # Fallback
    return """
    #Slimbar { background:#ececec; border-right:1px solid #cfcfcf; }
    #PaginaConsultas { background:#f2f2f2; }
    #TabelaConsultas { background:#ffffff; color:#222; border:1px solid #c9c9c9; gridline-color:#d9d9d9; }
    #TabelaConsultas QHeaderView::section { background:qlineargradient(x1:0,y1:0,x2:0,y2:1, stop:0 #e7e7e7, stop:1 #d8d8d8); color:#1e1e1e; border:1px solid #c2c2c2; }
    #StatusConsultaLabel { color:#444; }
    """


# ---------------- QSS para diálogos de Autenticação (Login/Registro) ---------------- #
# Onde aplica: QDialog com objectName "AuthDialog" + títulos/botões nomeados.
QSS_AUTH_DIALOG = """
QDialog#AuthDialog {
    background: #f7f9fc;
    border: 1px solid #dbe5f1;
    border-radius: 12px;
}
QDialog#AuthDialog QLabel#AuthTitle {
    font-size: 20px;
    font-weight: 800;
    color: #1a1a1a;
}
QDialog#AuthDialog QLabel#AuthSubtitle {
    font-size: 12px;
    color: #6c757d;
}
QDialog#AuthDialog QLabel#AuthIcon {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4285f4, stop:1 #1976d2);
    border-radius: 10px;
    padding: 6px;
    color: #ffffff;
}
QDialog#AuthDialog QLineEdit, QDialog#AuthDialog QComboBox {
    border: 1px solid #b8c4d2;
    border-radius: 8px;
    padding: 8px 10px;
}
QDialog#AuthDialog QLineEdit:focus, QDialog#AuthDialog QComboBox:focus {
    border: 1px solid #1976d2;
}
QDialog#AuthDialog QPushButton {
    border-radius: 8px;
    padding: 8px 14px;
}
QDialog#AuthDialog QPushButton#Primary {
    background: #1976d2;
    color: #ffffff;
    border: 1px solid #1976d2;
}
QDialog#AuthDialog QPushButton#Primary:hover { background: #1f82e6; }
QDialog#AuthDialog QPushButton#Primary:pressed { background: #1669b5; }
QDialog#AuthDialog QPushButton#Ghost {
    background: transparent;
    border: 1px solid #c5d1e0;
    color: #2e3440;
}
QDialog#AuthDialog QPushButton#Ghost:hover {
    background: #eef3fb;
}
"""


# ---------------- QSS de foco para a página Bloqueado ---------------- #
# Onde aplica: campos focados do formulário da página Bloqueado.

def qss_focus_override(modo: str) -> str:
    if modo == "escuro":
        return """
#PaginaBloqueado QLineEdit:focus,
#PaginaBloqueado QTextEdit:focus,
#PaginaBloqueado QComboBox:focus {
    background:#3a4149; /* cinza escuro de foco */
    border:1px solid #e0aa00;
    color:#ffffff;
}
"""
    else:  # claro
        return """
#PaginaBloqueado QLineEdit:focus,
#PaginaBloqueado QTextEdit:focus,
#PaginaBloqueado QComboBox:focus {
    background:#fffbe6; /* amarelo muito claro */
    border:1px solid #e0aa00;
    color:#000;
}
"""

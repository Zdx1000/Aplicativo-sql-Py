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
/* Slimbar leve e simples, com faixa inteligente na direita
    A faixa da direita é desenhada no background do Slimbar (sem border-right).
    Quando um botão está "pressed/checked", o próprio botão cobre a faixa,
    criando uma abertura alinhada ao botão. */
#Slimbar {
    /* Fundo claro simples + borda sutil à direita */
    background: #f9fafc;
    border:1px solid #002336
}

/* Botão topo: Toggle Menu */
#Slimbar #ToggleMenu {
     color: #2e3440;
     text-align: left;
     padding: 10px 14px;
     margin: 6px 8px 2px 8px;
     border: none;
     border-radius: 10px;
     background: #d3dfed;
}
#Slimbar #ToggleMenu:hover {
     background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
          stop:0 #e9f1ff, stop:1 #d9e7ff);
}

/* Botões do menu */
#Slimbar QPushButton {
     color: #2e3440;
     text-align: left;
     padding: 10px 14px;
     border: none;
     border-left: 4px solid transparent; /* destaque à esquerda */
     border-radius: 8px;
     margin: 1px 6px;
     background: #dae4f0; /* deixa a faixa direita visível por padrão */
     font-weight: 500;
}
#Slimbar QPushButton:hover {
     /* realce suave, mantendo a faixa visível ao passar o mouse */
     background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
          stop:0 #eef4ff, stop:1 #deebff);
     border-left: 4px solid #4285f4;
     color: #1a73e8;
}

/* Quando pressionado ou selecionado:
    - usamos um gradiente horizontal que "pinta" o trecho final com a cor do corpo
      do Slimbar (#f9fafc), cobrindo a faixa e criando a abertura alinhada ao botão. */
#Slimbar QPushButton:pressed,
#Slimbar QPushButton:checked {
     background: qlineargradient(
          x1:0, y1:0, x2:1, y2:0,
          stop:0.0   #eaf3ff,
          stop:0.985 #cfe3ff,
          stop:0.986 #f9fafc,  /* cobre a faixa direita (abertura) */
          stop:1.0   #f9fafc
     );
     border-left: 4px solid #1976d2;
     color: #0d47a1;
     font-weight: 600;
}

#PlaceholderLabel { color: #66717f; font-size: 17px; }

#Slimbar #AppName { font-size: 18px; font-weight: 800; color: #1a1a1a; }
#Slimbar #AppSubtitle {
     font-size: 12px;
     color: #6c757d;
     font-weight: 500;
}
#Slimbar #AppIcon {
     background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #4285f4, stop:1 #1976d2);
     border-radius: 12px;
     padding: 6px;
}

#Slimbar #UserLabel {
     font-size: 11px;
     font-weight: 600;
     color: #1976d2;
     background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e3f2fd, stop:1 #f3e5f5);
     border: 2px solid #bbdefb;
     border-radius: 10px;
     padding: 8px 12px;
}
#Slimbar #StatusLabel {
     font-size: 11px;
     color: #388e3c;
     font-weight: 500;
}
#Slimbar #VersionLabel {
     font-size: 10px;
     color: #9e9e9e;
     font-weight: 500;
}

/* Separador fino */
#Slimbar #SlimSeparator {
     background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
          stop:0 #e0e7ff, stop:1 #c7d2fe);
     height: 2px;
     border-radius: 1px;
}
"""


# ---------------- QSS adicional por tema ---------------- #
# Onde aplica: reforça estilos por tema, incluindo Slimbar, página de Consultas e
# cores de texto das páginas Bloqueado/Configurações.

def qss_tema_extra(modo: str) -> str:
    if modo == "escuro":
        return (
            """
            /* Container da Slimbar (visual dark, borda sutil) */
            #Slimbar { background:#161b22; border-right:1px solid #2a2f36; }
            /* Toggle Menu (pílula no topo) */
            #Slimbar #ToggleMenu { 
                color:#e6edf3; 
                background:rgba(255,255,255,0.06); 
                border:1px solid #2a2f36; 
                border-radius:10px; 
                padding: 10px 14px;
                margin:6px 8px 2px 8px; 
            }
            #Slimbar #ToggleMenu:hover { background:rgba(255,255,255,0.1); }
            /* Botões: cantos arredondados, leve preenchimento escuro */
            #Slimbar QPushButton { 
                color:#dbe1ea; 
                text-align:left; 
                padding: 10px 14px;
                border:1px solid transparent; 
                border-left:4px solid transparent; 
                border-radius:8px; 
                margin:1px 6px; 
                background:rgba(255,255,255,0.03);
            }
            #Slimbar QPushButton:hover { 
                background:rgba(255,255,255,0.06); 
                border-left:4px solid #6ea8fe; 
                color:#ffffff; 
            }
            #Slimbar QPushButton:checked { 
                background:rgba(110,168,254,0.15); 
                border-left:4px solid #6ea8fe; 
                color:#ffffff; 
                font-weight:600; 
            }
            #PlaceholderLabel { color:#9aa2af; }
            #Slimbar #AppName { color:#e6edf3; }
            #Slimbar #AppSubtitle { color:#9da7b3; }
            #Slimbar #UserLabel { background:rgba(255,255,255,0.06); color:#e6edf3; border:1px solid #2a2f36; }
            /* Reforço de caixa do UserLabel para não sumir em fundos escuros */
            #Slimbar QLabel#UserLabel { 
                padding: 8px 12px; 
                border-radius: 10px; 
                background: rgba(255,255,255,0.08); 
                color: #e6edf3; 
                border: 1px solid #2a2f36; 
            }
            #Slimbar #StatusLabel { color:#7fbf7f; }
            #Slimbar #VersionLabel { color:#9aa2af; }

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

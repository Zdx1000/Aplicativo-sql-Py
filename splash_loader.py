from PySide6.QtWidgets import QApplication, QLabel
from PySide6.QtGui import QMovie
from PySide6.QtCore import Qt, QTimer
import sys
import os


# Caminho do GIF compatível com .exe e .py
if getattr(sys, 'frozen', False):
    BASE_PATH = sys._MEIPASS
else:
    BASE_PATH = os.path.dirname(os.path.abspath(__file__))
GIF_PATH = os.path.join(BASE_PATH, "assets", "loading.gif")

app = QApplication(sys.argv)

# Splash com GIF animado centralizado e acima de todos os aplicativos
# Qt.WindowStaysOnTopHint garante que fique acima de tudo
gif_label = QLabel()
gif_label.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
gif_label.setAttribute(Qt.WA_TranslucentBackground)
gif_label.setStyleSheet("background: transparent;")
movie = QMovie(GIF_PATH)
movie.setCacheMode(QMovie.CacheAll)
movie.setSpeed(100)
gif_label.setMovie(movie)
gif_label.setFixedSize(287, 141)
screen = app.primaryScreen().geometry()
gif_label.move((screen.width() - 498) // 2, (screen.height() - 498) // 2)
gif_label.show()
movie.start()
app.processEvents()

# Aguarda 2 segundos antes de fechar o splash e abrir o login
def show_login():
    gif_label.close()
    from servidor import LoginDialog, MainWindow
    login = LoginDialog()
    if not login.exec():
        sys.exit(0)
    main = MainWindow()
    main.show()

QTimer.singleShot(2000, show_login)
sys.exit(app.exec())
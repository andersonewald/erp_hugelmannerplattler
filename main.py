# main.py
import sys
from PyQt6.QtWidgets import QApplication
from views.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # A MainWindow iniciará diretamente e abrirá a tela de login embutida na área MDI
    window = MainWindow()
    window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
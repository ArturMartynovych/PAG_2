from PyQt5.QtWidgets import QApplication
import sys
import gui


if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = gui.MainWindow()
    app.exec_()
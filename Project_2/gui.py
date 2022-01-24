from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint, QSize
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QGridLayout, QPlainTextEdit, QPushButton, QMessageBox, QMainWindow, \
    QApplication, QFileDialog, QDesktopWidget, QMenu, QDateEdit
import sys
import main


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.file_name = None
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.oldPos = self.pos()
        self.setStyleSheet('background-color: rgb(29, 32, 40); color:white; ')
        self.textArea = QPlainTextEdit()
        self.textArea.setReadOnly(True)
        self.textArea.setStyleSheet("background-color: rgb(45, 51, 69); border-radius: 16.5px;")
        # self.textArea.setStyleSheet('border: 3px solid red; background-image: url(grey.png)')
        self.textArea.verticalScrollBar().setStyleSheet('background: rgb(255,215,0); width: 20px')
        self.textArea.setFont(QtGui.QFont('Courier', 10))
        menu_btn = QPushButton('', self)
        # self.icon = QPixmap('icons/menu.png')
        menu_btn.setIcon(QIcon('icons/menu.png'))
        menu_btn.setIconSize(QSize(24, 24))
        menu = QMenu(self)
        menu.setFont(QtGui.QFont('Courier', 9))
        menu.setStyleSheet('QMenu:item{font:bold; padding: 2px 20px 2px 5px;border: 4px solid transparent; '
                           'border-radius: 13px; spacing: 0px;}'
                           'QMenu:item:selected{background-color: rgb(45, 51, 69);font:bold}')
        menu.addSeparator()
        save = menu.addMenu('&Zapisz do pliku')
        save.setMinimumWidth(200)
        save.addAction('Zapisz do pliku tekstowego')
        save.addAction('Zapisz do pliku CSV')
        menu.addSeparator()
        clear = menu.addAction('&Wyczyść okno')
        menu_btn.setMenu(menu)
        save.setFont(QtGui.QFont('Courier', 5))
        # self.icon.setMaximumSize(25, 25)
        # self.menu_btn.setScaledContents(True)
        self.title = QLabel('  Programowanie Aplikacji Geoinformacyjnych')
        self.title.setStyleSheet("font: bold")
        self.title.setFont(QtGui.QFont('Courier', 13))
        self.title.setMinimumWidth(600)
        self.date_edit = QDateEdit(calendarPopup=True)
        self.date_edit.calendarWidget().setLocale(QtCore.QLocale(QtCore.QLocale.English))
        self.date_edit.setDateTime(QtCore.QDateTime.currentDateTime())
        self.date_edit.setStyleSheet('QDateEdit{padding: 2px 0px 2px 65px;border: none; font:bold}'
                                     'QDateEdit::drop-down{image: url(icons/arrow-bottom.png);padding:5px 5px 5px 5px;}'
                                     'QDateEdit:hover{background-color:rgb(41, 50, 69);border-radius: 16.5px}')
        self.date_edit.setFont(QtGui.QFont('Courier', 13))
        self.date_edit.setMinimumHeight(35)
        minimize_btn = QPushButton('', self)
        minimize_btn.setIcon(QIcon('icons/minimize.png'))
        minimize_btn.setIconSize(QSize(24, 24))
        end_btn = QPushButton('', self)
        end_btn.setIcon(QIcon('icons/x.png'))
        end_btn.setIconSize(QSize(24, 24))
        load_btn = QPushButton('Wczytaj plik', self)
        codes_btn = QPushButton('Wszystkie kody', self)
        corrects_btn = QPushButton('Poprawne kody', self)
        incorrects_btn = QPushButton('Niepoprawne kody', self)
        save_btn = QPushButton('Zapisz dane', self)
        clear_btn = QPushButton('Wyczyść', self)
        end_btn.resize(end_btn.sizeHint())
        minimize_btn.setMinimumSize(40, 20)
        end_btn.setMinimumSize(40, 20)
        load_btn.setMinimumSize(180, 35)
        codes_btn.setMinimumSize(180, 35)
        corrects_btn.setMinimumSize(180, 35)
        incorrects_btn.setMinimumSize(180, 35)
        save_btn.setMinimumSize(180, 35)
        clear_btn.setMinimumSize(180, 35)
        # load_btn.setMaximumWidth(245)
        # save_btn.setMaximumWidth(245)
        # clear_btn.setMaximumWidth(245)
        # end_btn.setMaximumWidth(245)
        minimize_btn.setFont(QtGui.QFont('Arial', 13))
        end_btn.setFont(QtGui.QFont('Arial', 13))
        codes_btn.setFont(QtGui.QFont('Courier', 13))
        incorrects_btn.setFont(QtGui.QFont('Courier', 13))
        load_btn.setFont(QtGui.QFont('Courier', 13))
        save_btn.setFont(QtGui.QFont('Courier', 13))
        clear_btn.setFont(QtGui.QFont('Courier', 13))
        corrects_btn.setFont(QtGui.QFont('Courier', 13))
        style2 = 'QPushButton{background: transparent; font:bold}'\
                 'QPushButton:menu-indicator{width:0px;}'\
                 'QPushButton:pressed{background-color: rgb(41, 50, 69)}' \
                 'QPushButton:hover{background-color: rgb(41, 50, 69); border-radius: 16.2px;}'
        menu_btn.setStyleSheet(style2)
        minimize_btn.setStyleSheet(style2)
        end_btn.setStyleSheet(style2)
        style = 'QPushButton{background:transparent; color:white; font:bold}'\
                'QPushButton:pressed{background-color: rgb(41, 50, 69)}' \
                'QPushButton:hover{background-color: rgb(41, 50, 69); border-radius: 16.5px;}'
        load_btn.setStyleSheet(style)
        codes_btn.setStyleSheet(style)
        corrects_btn.setStyleSheet(style)
        incorrects_btn.setStyleSheet(style)
        save_btn.setStyleSheet(style)
        clear_btn.setStyleSheet(style)
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.addWidget(menu_btn, 0, 0, 1, 1)
        layout.addWidget(self.title, 0, 1, 1, 9)
        layout.addWidget(minimize_btn, 0, 10, 1, 1)
        layout.addWidget(end_btn, 0, 11, 1, 1)
        layout.addWidget(load_btn, 1, 8, 1, 4)
        layout.addWidget(codes_btn, 2, 8, 1, 4)
        layout.addWidget(corrects_btn, 3, 8, 1, 4)
        layout.addWidget(incorrects_btn, 4, 8, 1, 4)
        layout.addWidget(save_btn, 5, 8, 1, 4)
        layout.addWidget(clear_btn, 6, 8, 1, 4)
        layout.addWidget(self.date_edit, 7, 8, 1, 4)
        layout.addWidget(self.textArea, 1, 0, 8, 8)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        # menu_btn.clicked.connect(self.context_menu)
        clear.triggered.connect(self.clear_wind)
        minimize_btn.clicked.connect(self.minimize_window)
        load_btn.clicked.connect(self.open_file)
        codes_btn.clicked.connect(self.set_text)
        corrects_btn.clicked.connect(self.set_text)
        incorrects_btn.clicked.connect(self.set_text)
        save_btn.clicked.connect(self.save_file)
        clear_btn.clicked.connect(self.clear_wind)
        end_btn.clicked.connect(self.end)
        self.setGeometry(100, 50, 700, 900)
        # self.setFont(myFont)
        self.setCentralWidget(widget)
        self.setWindowIcon(QIcon('pw.png'))
        self.setWindowTitle('  PAG')
        self.show()

    def minimize_window(self):
        self.showMinimized()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

    def msg_box(self, text, info, msg_type):
        msg = QMessageBox(self)
        msg.setFont(QtGui.QFont('Courier', 10))
        msg.setWindowFlags(Qt.FramelessWindowHint)
        msg.setWindowTitle('Komunikat')
        msg.setStyleSheet('QMessageBox{background-color:rgb(71, 88, 125);font:bold;'
                          'border: 2px solid rgb(204, 209, 219); border-radius: 35.5px; width: 500px; spacing: 0px;}'
                          'QLabel{background:transparent; color:#fff; width: 300px; padding: 4px 10px 1px 0px; }'
                          'QPushButton{background:transparent; width: 100px; height: 25px; font:bold; }'
                          'QPushButton:pressed{background-color: rgb(51, 64, 929)}' 
                          'QPushButton:hover{background-color: rgb(51, 64, 92); border-radius: 15.5px;}')
        msg.setText(f'{text}\n{info}')
        if msg_type == 'crit-error':
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Critical)
        if msg_type == 'error':
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Warning)
        if msg_type == 'info':
            msg.setStandardButtons(QMessageBox.Ok)
            msg.setIcon(QMessageBox.Information)
        if msg_type == 'question':
            msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            msg.setIcon(QMessageBox.NoIcon)
        msg.show()
        return msg

    def end(self):
        self.close()

    def open_file(self):
        try:
            file_dialog = QFileDialog()
            path = str(file_dialog.getOpenFileName(filter="Text files (*.txt)")[0])
        except (FileNotFoundError, OSError):
            pass
        else:
            self.file_name = path

    def set_text(self):
        send = self.sender()
        date = self.date_edit.dateTime().toString("yyyyMMdd")
        year = date[0:4]
        month = date[4:6]
        filesPath = main.unzipFiles(year, month)
        data = main.readCSV(f'{filesPath}\{main.listOfCodes[0]}_{year}_{month}.csv')
        result, trim = main.getStatistics(data)
        self.textArea.appendPlainText(str(trim))

    def closeEvent(self, event):
        odp = self.msg_box('\n Czy na pewno chcesz zamknąć aplikację?', '', 'question')
        odp = odp.exec()
        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def clear_wind(self):
        self.textArea.clear()

    def save_file(self):
        if self.textArea.toPlainText():
            try:
                name = QFileDialog.getSaveFileName(self, '/', '*.txt')[0]
                save = open(name, 'w')
            except FileNotFoundError:
                pass
            else:
                save.writelines(self.textArea.toPlainText())
                save.close()
                self.msg_box('Dane zostały poprawnie zapisane!', '', 'info')
        else:
            self.msg_box('Brak informacji do zapisu!', '', 'error')

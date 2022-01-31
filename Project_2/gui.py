from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtCore import Qt, QPoint, QSize, QProcess
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QLabel, QGridLayout, QPlainTextEdit, QPushButton, QMessageBox, QMainWindow, \
    QApplication, QFileDialog, QDesktopWidget, QMenu, QComboBox, QLineEdit, QListWidgetItem, QTableView, QHeaderView
from py2neo import Graph
import geopandas as gpd
import pandas as pd
import pymongo
import redis
import datetime
import sys
import pag


class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()
                                       and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles


class GeoDataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=gpd.GeoDataFrame(), parent=None):
        super(GeoDataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(gpd.GeoDataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount()
                                       and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == GeoDataFrameModel.ValueRole:
            return val
        if role == GeoDataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            GeoDataFrameModel.DtypeRole: b'dtype',
            GeoDataFrameModel.ValueRole: b'value'
        }
        return roles


class MainWindow(QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.year, self.month, self.mt, self.save, self.woj, self.woj_10, self.powiat, self.powiat_10 = None, None, \
                                                                                                        None, None, \
                                                                                                        None, None, \
                                                                                                        None, None
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.center()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.oldPos = self.pos()
        self.setStyleSheet('background-color: rgb(29, 32, 40); color:white; ')
        self.textArea = QPlainTextEdit()
        self.textArea.setReadOnly(True)
        self.textArea.setStyleSheet("background-color: rgb(45, 51, 69); border-radius: 23px;")
        # self.textArea.setStyleSheet('border: 3px solid red; background-image: url(grey.png)')
        self.textArea.verticalScrollBar().setStyleSheet('width: 20px')
        self.textArea.setFont(QtGui.QFont('Courier', 6))
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

        save_txt = save.addAction('Zapisz do pliku tekstowego')
        save_csv = save.addAction('Zapisz do pliku CSV')
        save_json = save.addAction('Zapisz do pliku JSON')
        menu.addSeparator()
        clear = menu.addAction('&Wyczyść okno')
        menu_btn.setMenu(menu)
        save.setFont(QtGui.QFont('Courier', 5))
        self.title = QLabel('  Programowanie Aplikacji Geoinformacyjnych')
        self.title.setStyleSheet("font: bold")
        self.title.setFont(QtGui.QFont('Courier', 13))
        self.title.setMinimumWidth(600)
        self.data_lab = QLabel('Data pomiarów')
        self.data_lab.setStyleSheet("font: bold; padding-left: 120px")
        self.data_lab.setFont(QtGui.QFont('Courier', 13))
        self.data_lab.setMaximumHeight(20)
        self.year_comb = QComboBox()
        self.month_comb = QComboBox()
        self.year_comb.addItems([str(x) for x in range(2008, 2022)])
        self.month_comb.addItems([pag.month_dictionary(str(x)) for x in range(1, 13)])
        style3 = 'QComboBox{border: none; font:bold; outline: 0; padding-left: 40px} ' \
                 'QComboBox::drop-down{image: url(icons/arrow-bottom.png); padding: 2px 5px 0px 0px}' \
                 'QComboBox:hover{background-color:rgb(41, 50, 69);border-radius: 8.5px}'
        style6 = 'QLineEdit:hover{background-color:rgb(41, 50, 69);border-radius: 8.5px}'
        self.year_comb.setStyleSheet(style3)
        self.month_comb.setStyleSheet(style3)
        self.year_label = QLineEdit()
        self.year_label.setPlaceholderText('Rok')
        self.year_label.setFont(QtGui.QFont('Courier', 13))
        self.year_label.setReadOnly(True)
        self.year_label.setStyleSheet(style6)
        self.year_comb.setLineEdit(self.year_label)
        self.year_comb.setCurrentIndex(-1)
        self.month_label = QLineEdit()
        self.month_label.setPlaceholderText('Miesiąc')
        self.month_label.setFont(QtGui.QFont('Courier', 13))
        self.month_label.setReadOnly(True)
        self.month_label.setStyleSheet(style6)
        self.month_comb.setLineEdit(self.month_label)
        self.month_comb.setCurrentIndex(-1)
        # self.month_comb.setCurrentText('Miesiąc')
        self.year_comb.setFont(QtGui.QFont('Courier', 11))
        self.month_comb.setFont(QtGui.QFont('Courier', 11))
        # self.year_comb.setMaximumWidth(80)
        self.data_lab2 = QLabel('Zakres pomiarów')
        self.data_lab2.setStyleSheet("font: bold; padding-left: 110px")
        self.data_lab2.setFont(QtGui.QFont('Courier', 13))
        self.data_lab2.setMaximumHeight(20)
        style5 = 'QComboBox{border: none; font:bold; outline: 0; padding-left: 40px} ' \
                 'QComboBox::drop-down{image: url(icons/arrow-bottom.png); padding: 6px 5px 0px 0px}' \
                 'QComboBox:hover{background-color:rgb(41, 50, 69);border-radius: 13.5px}'
        measure_types = ['Temperatura powietrza [°C]', 'Temperatura gruntu [°C]', 'Kierunek wiatru [°]',
                        'Średnia prędkość wiatru [m/s]', 'Maksymalna prędkość wiatur [m/s]', 'Suma opadu 10 minutowego',
                        'Suma opadu dobowego', 'Suma opadu godzinowego', 'Względna wilgotność powietrza',
                        'Największy poryw wiatru', 'Zapas wody w śniegu']
        self.measure_comb = QComboBox()
        self.measure_comb.addItems(measure_types)
        self.measure_comb.setStyleSheet(style5)
        self.measure_comb.setFont(QtGui.QFont('Courier', 11))
        self.measure_comb.setMinimumHeight(30)
        measure_types_2 = ['Województwa dla każdego dnia', 'Województwa dla każdych 10 minut',
                           'Powiaty dla każdego dnia', 'Powiaty dla każdych 10 minut']
        self.measure_comb_2 = QComboBox()
        self.measure_comb_2.addItems(measure_types_2)
        self.measure_comb_2.setStyleSheet(style5)
        self.measure_comb_2.setFont(QtGui.QFont('Courier', 11))
        self.measure_comb_2.setMinimumHeight(30)
        self.table = QTableView()
        self.table.setStyleSheet('QTableView{border:none; outline: 0; background-color:rgb(41, 50, 69);'
                                 'border-radius: 26px;}'
                                 'QHeaderView:section{border:none; background-color:rgb(60,74,105);padding-left: 8px}'
                                 'QTableCornerButton:section{background-color: rgb(60, 74, 105)}')
        self.table.setFont(QtGui.QFont('Courier', 6))
        self.table.verticalScrollBar().setStyleSheet('width: 20px')
        minimize_btn = QPushButton('', self)
        minimize_btn.setIcon(QIcon('icons/minimize.png'))
        minimize_btn.setIconSize(QSize(24, 24))
        end_btn = QPushButton('', self)
        end_btn.setIcon(QIcon('icons/x.png'))
        end_btn.setIconSize(QSize(24, 24))
        load_btn = QPushButton('Pobierz pomiary', self)
        stats_btn = QPushButton('Oblicz statystyki', self)
        stations_btn = QPushButton('Wyświetl stacje meteo', self)
        mongo_btn = QPushButton('Wyślij do MongoDB', self)
        redis_btn = QPushButton('Wyślij do Redis', self)
        neo4j_btn = QPushButton('Wyślij do Neo4j', self)
        end_btn.resize(end_btn.sizeHint())
        minimize_btn.setMinimumSize(40, 20)
        end_btn.setMinimumSize(40, 20)
        load_btn.setMinimumSize(180, 35)
        stats_btn.setMinimumSize(180, 35)
        stations_btn.setMinimumSize(180, 35)
        mongo_btn.setMinimumSize(180, 35)
        neo4j_btn.setMinimumSize(180, 35)
        redis_btn.setMinimumSize(180, 35)
        # load_btn.setMaximumWidth(245)
        # save_btn.setMaximumWidth(245)
        # clear_btn.setMaximumWidth(245)
        # end_btn.setMaximumWidth(245)
        minimize_btn.setFont(QtGui.QFont('Arial', 13))
        end_btn.setFont(QtGui.QFont('Arial', 13))
        stats_btn.setFont(QtGui.QFont('Courier', 13))
        mongo_btn.setFont(QtGui.QFont('Courier', 13))
        load_btn.setFont(QtGui.QFont('Courier', 13))
        neo4j_btn.setFont(QtGui.QFont('Courier', 13))
        redis_btn.setFont(QtGui.QFont('Courier', 13))
        stations_btn.setFont(QtGui.QFont('Courier', 13))
        style2 = 'QPushButton{background: transparent; font:bold; outline: 0}'\
                 'QPushButton:menu-indicator{width:0px;}'\
                 'QPushButton:pressed{background-color: rgb(41, 50, 69)}' \
                 'QPushButton:hover{background-color: rgb(41, 50, 69); border-radius: 16.2px;}'
        menu_btn.setStyleSheet(style2)
        minimize_btn.setStyleSheet(style2)
        end_btn.setStyleSheet(style2)
        style = 'QPushButton{background:transparent; color:white; font:bold; outline: 0}'\
                'QPushButton:pressed{background-color: rgb(41, 50, 69)}' \
                'QPushButton:hover{background-color: rgb(41, 50, 69); border-radius: 16.5px;}'
        load_btn.setStyleSheet(style)
        stats_btn.setStyleSheet(style)
        stations_btn.setStyleSheet(style)
        mongo_btn.setStyleSheet(style)
        neo4j_btn.setStyleSheet(style)
        redis_btn.setStyleSheet(style)
        layout = QGridLayout()
        layout.setVerticalSpacing(20)
        layout.addWidget(menu_btn, 0, 0, 1, 1)
        layout.addWidget(self.title, 0, 1, 1, 9)
        layout.addWidget(minimize_btn, 0, 10, 1, 1)
        layout.addWidget(end_btn, 0, 11, 1, 1)
        layout.addWidget(self.data_lab, 1, 8, 1, 4)
        layout.addWidget(self.year_comb, 2, 8, 1, 2)
        layout.addWidget(self.month_comb, 2, 10, 1, 2)
        layout.addWidget(load_btn, 3, 8, 1, 4)
        layout.addWidget(self.data_lab2, 4, 8, 1, 4)
        layout.addWidget(self.measure_comb, 5, 8, 1, 4)
        layout.addWidget(self.measure_comb_2, 6, 8, 1, 4)
        layout.addWidget(stats_btn, 7, 8, 1, 4)
        layout.addWidget(stations_btn, 8, 8, 1, 4)
        layout.addWidget(mongo_btn, 9, 8, 1, 4)
        layout.addWidget(redis_btn, 10, 8, 1, 4)
        layout.addWidget(neo4j_btn, 11, 8, 1, 4)
        # layout.addWidget(self.date_edit, 11, 8, 1, 4)
        layout.addWidget(self.textArea, 1, 0, 3, 8)
        layout.addWidget(self.table, 4, 0, 9, 8)
        widget = QtWidgets.QWidget()
        widget.setLayout(layout)
        # menu_btn.clicked.connect(self.context_menu)
        clear.triggered.connect(self.clear_wind)
        save_txt.triggered.connect(self.save_txt)
        save_csv.triggered.connect(self.save_csv)
        save_json.triggered.connect(self.save_json)
        minimize_btn.clicked.connect(self.minimize_window)
        load_btn.clicked.connect(self.download_file)
        stats_btn.clicked.connect(self.get_statistics)
        stations_btn.clicked.connect(self.meteo_stations)
        mongo_btn.clicked.connect(self.get_statistics)
        redis_btn.clicked.connect(self.get_statistics)
        neo4j_btn.clicked.connect(self.get_statistics)
        end_btn.clicked.connect(self.end)
        self.setGeometry(100, 50, 850, 900)
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

    def get_df(self):
        df = None
        if self.save == 1:
            df = pag.names_of_miejc()
            df.drop(['lat', 'lon'], axis=1, inplace=True)
        if self.save == 2:
            df = self.woj
        if self.save == 3:
            df = self.woj_10
        if self.save == 4:
            df = self.powiat
        if self.save == 5:
            df = self.powiat_10
        if 'Województwo' in df.columns:
            df.rename(columns={'Województwo': 'Wojewodztwo', 'W ciągu dnia': 'Day', 'Średnia obcięta': 'trim_mean'},
                      inplace=True)
        return df

    def save_csv(self):
        print(self.save)
        try:
            if not self.save:
                raise ValueError
            path = QFileDialog.getSaveFileName(self, 'Zapis', '/', 'CSV Files (*.csv)')[0]
            df = self.get_df()
            df.to_csv(path, sep=';')

        except ValueError:
            self.msg_box('Brak informacji do zapisu!', '', 'error')
        except FileNotFoundError:
            pass
        else:
            self.msg_box('Dane zostały poprawnie zapisane!', '', 'info')

    def save_txt(self):
        print(self.save)
        try:
            if not self.save:
                raise ValueError
            path = QFileDialog.getSaveFileName(self, 'Zapis', '/', 'Text Files (*.txt)')[0]
            df = self.get_df()
            df.to_csv(path, sep=';')

        except ValueError:
            self.msg_box('Brak informacji do zapisu!', '', 'error')
        except FileNotFoundError:
            pass
        else:
            self.msg_box('Dane zostały poprawnie zapisane!', '', 'info')

    def save_json(self):
        print(self.save)
        try:
            if not self.save:
                raise ValueError
            if self.save == 1:
                raise TypeError
            path = QFileDialog.getSaveFileName(self, 'Zapis', '/', 'JSON Files (*.json);;GEOJSON Files (*.geojson)')[0]
            df = self.get_df()
            df.to_json(path, orient='records')

        except ValueError:
            self.msg_box('Brak informacji do zapisu!', '', 'error')
        except TypeError:
            self.msg_box('Wybierz poprawne dane do zapisu!', '', 'error')
        except FileNotFoundError:
            pass
        else:
            self.msg_box('Dane zostały poprawnie zapisane!', '', 'info')

    def download_file(self):
        try:
            year = self.year_comb.currentText()
            month = self.month_comb.currentText()
            if len(year) == 0 or len(month) == 0:
                raise ValueError
            month = pag.month_dictionary_2(month)
            self.textArea.insertPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                          f'Pobieranie plików z pomiarami dla {month} {year}...')
            self.textArea.repaint()
            if not pag.check_directory(f'dane-imgw\Meteo_{year}-{month}.zip'):
                pag.unzipFiles(year, month)
            self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                          f'Pliki zostały pobrane')
            self.textArea.repaint()
        except ValueError:
            self.msg_box('Wybierz datę pomiarów', '', 'error')

    def meteo_stations(self):
        self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                          f'Wczytywanie informacji na temat stacji meteorologicznych...')
        self.textArea.repaint()
        stations = pag.names_of_miejc()
        self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                      f'Informacje zostały wczytane')
        self.textArea.repaint()
        self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                          f'Tworzenie modelu...')
        self.textArea.repaint()
        stations.drop(['lat', 'lon'], axis=1, inplace=True)
        copy = stations.rename(columns={'Name of Station': 'Nazwa'})
        model = GeoDataFrameModel(copy)
        self.table.setModel(model)
        self.table.resizeColumnsToContents()
        self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                      f'Model został stworzony')
        self.textArea.repaint()
        self.save = 1

    def get_statistics(self):
        send = self.sender()
        print(self.year)
        print(self.month)
        print(self.woj)
        print(self.woj_10)
        print(self.powiat)
        print(self.powiat_10)
        m_type = self.measure_comb.currentText()
        m_type2 = self.measure_comb_2.currentIndex()
        year = self.year_comb.currentText()
        month = self.month_comb.currentText()
        self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                          f'Wyliczanie statystyk...')
        self.textArea.repaint()
        try:
            if len(year) == 0 or len(month) == 0:
                raise ValueError
            month = pag.month_dictionary_2(month)
            if m_type == 'Zapas wody w śniegu' and month not in ['01', '02', '03', '11', '12']:
                raise ValueError
            stations = pag.names_of_miejc()
            if not (year == self.year and month == self.month and m_type == self.mt):
                data_stations = pag.adding_sun_day(year, month, pag.code_dictionary(m_type), stations)
                value_wojew, value_powiat = pag.value_in(data_stations)
                self.year = year
                self.month = month
                self.mt = m_type
                self.woj = value_wojew[0]
                self.woj_10 = value_wojew[1]
                self.powiat = value_powiat[0]
                self.powiat_10 = value_powiat[1]
        except (KeyError, ValueError):
            self.msg_box('Wybierz poprawną datę i zakres pomiarów!', '', 'error')
        except FileNotFoundError:
            self.msg_box('Brak danych dla wybranej daty!', '', 'error')
        else:
            if send.text() == 'Oblicz statystyki':
                if m_type2 == 0:
                    df = self.woj
                    self.save = 2
                if m_type2 == 1:
                    df = self.woj_10
                    self.save = 3
                if m_type2 == 2:
                    df = self.powiat
                    self.save = 4
                if m_type2 == 3:
                    df = self.powiat_10
                    self.save = 5
                if 'index' in df.columns:
                    df.drop('index', axis=1, inplace=True)
                if m_type2 in [0, 2]:
                    # df.rename(columns={'Date': 'Data', 'day': 'W ciągu dnia', 'Value': 'Średnia obcięta'}, inplace=True)
                    model = DataFrameModel(df)
                    self.table.setModel(model)
                    self.table.resizeColumnsToContents()
                if m_type2 in [1, 3]:
                    # df.rename(columns={'Date': 'Data', 'Time': 'Godzina', 'day': 'W ciągu dnia',
                    #                    'Value': 'Średnia obcięta'}, inplace=True)
                    model = DataFrameModel(df)
                    self.table.setModel(model)
                    self.table.resizeColumnsToContents()
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                                  f'Statystyki zostały policzone')
                self.textArea.repaint()
            if send.text() == 'Wyślij do MongoDB':
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Trwa umieszczanie danych w bazie MongoDB...')
                self.textArea.repaint()
                mt = pag.code_dictionary(m_type)
                my_client = pymongo.MongoClient('mongodb://localhost:27017/adnmin')
                mydb = my_client['pag']
                names = [f'statWoj {mt} {month}-{year}', f'statiWoj10 {mt} {month}-{year}',
                         f'statPow {mt} {month}-{year}', f'statPow10 {mt} {month}-{year}']
                collections = mydb.list_collection_names()
                if not set(names).issubset(set(collections)):
                    pag.mongo_add_collection(mydb, names[0], self.woj, ['Date'])
                    pag.mongo_add_collection(mydb, names[1], self.woj_10, ['Date', 'Time'])
                    pag.mongo_add_collection(mydb, names[2], self.powiat, ['Date'])
                    pag.mongo_add_collection(mydb, names[3], self.powiat_10, ['Date', 'Time'])
                    # pag.mongo_add_collection(mydb, 'stacjeMeteorologiczne', stations, ['geometry'])
                    self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                                  f'Dodano następujące kolekcje: {names}')
                    self.textArea.repaint()
                else:
                    self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                                  f'Kolekcje znajdują się już w bazie')
                    self.textArea.repaint()
                stacje = mydb.stacjeMeteorologiczne
                query = {'Name of Station': 'Mirsk'}
                doc = stacje.find_one(query)
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Wynik dla przykładowego zapytania do bazy MongoDB: '
                                              f'"{query}" -> "{doc}"')
                self.textArea.repaint()
                my_client.close()
            if send.text() == 'Wyślij do Redis':
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Trwa umieszczanie danych w bazie Redis...')
                self.textArea.repaint()
                pool = redis.ConnectionPool(host='127.0.0.1', port=6379, db=0, decode_responses=True)
                db = redis.Redis(connection_pool=pool)
                db.flushdb()
                # pag.db_redis(db, self.woj, ['Date'])
                pag.db_redis(db, self.woj_10, ['Date', 'Time'])
                # pag.db_redis(db, self.powiat, ['Date'])
                # pag.db_redis(db, self.powiat_10, ['Date', 'Time'])
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Dane zostały umieszczone w bazie danych Redis')
                self.textArea.repaint()
                query = "{'Województwo': 'świętokrzyskie', 'Date': '2021-09-30', 'Time': '23:50:00', 'day': False}"
                doc = db.hgetall(query)
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Wynik dla przykładowego zapytania do bazy Redis: '
                                              f'"{query}" -> "{doc}"')
                self.textArea.repaint()
            if send.text() == 'Wyślij do Neo4j':
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Trwa umieszczanie danych w bazie Neo4j...')
                self.textArea.repaint()
                graph = Graph("bolt://localhost:7687", user="neo4j", password="haslo")
                pag.save2neo4j(graph, self.woj, self.powiat)
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Dane zostały umieszczone w bazie danych Neo4j')
                self.textArea.repaint()
                queries = []
                # Wyszukiwanie średnich temperatur dla wszystkich powiatów w województwie mazowieckim  w danym dniu.
                queries.append(''' MATCH(t:time{date:'2021-09-05',day:TRUE})<-[WHEN]-(v:temp)-[r1:LOCATION]->(p:powiat)-[r2:IN]->(w:wojew{name:'mazowieckie'}) 
                            RETURN p.name,v.value''')
                # Zwrócenie najwyższej pomierzonej średniej temeratury województwa w danym miesiącu wraz z nazwą województwa, datą jego pomiaru
                queries.append('''MATCH (w:wojew)<-[r1:LOCATION]-(t:temp)
                            WITH  max(t.value) AS max
                            MATCH (w:wojew)<-[r2:LOCATION]-(t:temp{value:max})-[:WHEN]->(d:time)
                            RETURN t.value,w.name,d.date''')
                result_1 = graph.run(queries[0]).data()
                result_2 = graph.run(queries[1]).data()
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Wynik dla przykładowego zapytania do bazy Neo4j: '
                                              f'"{queries[0]}" -> "{result_1}"')
                self.textArea.repaint()
                self.textArea.appendPlainText(f'[{datetime.datetime.now().time().strftime("%H:%M:%S")}] '
                                              f'Wynik dla przykładowego zapytania do bazy Neo4j: '
                                              f'"{queries[1]}" -> "{result_2}"')
                self.textArea.repaint()

    def closeEvent(self, event):
        odp = self.msg_box('\n Czy na pewno chcesz zamknąć aplikację?', '', 'question')
        odp = odp.exec()
        if odp == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def clear_wind(self):
        self.textArea.clear()
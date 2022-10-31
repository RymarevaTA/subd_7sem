import PyQt6.QtGui
from PyQt6.QtSql import *
from PyQt6.QtWidgets import QApplication, QWidget, QDialog, QMessageBox
from dateutil.parser import parse
from PyQt6 import QtCore
from Main_menu import *
from edit_market import *
import sys
db_name = 'testo.db'

def connect_db(db_name):
    db = QSqlDatabase.addDatabase('QSQLITE')
    db.setDatabaseName(db_name)
    if not db.open():
        print('Не удалось подключиться к базе')
        return False
    else:
        print('connection OK')
        return db

class ModelMarket (QSqlTableModel):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setTable("market")
        self.select()

class ModelStruc_fut (QSqlTableModel):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.setTable("struc_futures")
        self.select()

class EditMarket(QtWidgets.QDialog):
    def __init__(self, sqltable:ModelMarket, sqltable_1:ModelStruc_fut,window:QtWidgets.QTableView):
        super().__init__()
        self.ql_table = sqltable
        self.ql_table_1 = sqltable_1
        self.window_tabl = window
        self.s = QDialog()
        self.s_root = Ui_Dialog()
        self.s_root.setupUi(self.s)
        self.msgBox = QMessageBox()

        sql = f"""SELECT name from struc_futures"""
        query = QSqlQuery(sql)
        name_futures = []
        while query.next():
            name_futures.append(query.value(0))

        for name in name_futures:
            self.s_root.comboBox.addItem(name)
        self.s_root.pushButton_2.clicked.connect(self.s.close)
        self.s_root.pushButton.clicked.connect(self.get_record)


        self.s.show()

    def get_record(self):
        format_bd = '%Y-%d-%m'
        format_us = '%m.%d.%Y'
        msg_box_text = ''
        self.new_row = []
        self.new_row.append(self.s_root.comboBox.currentText()) #код фьючерса 0
        try:
            res = bool(parse(self.s_root.textEdit_2.toPlainText()))
            res_1 = bool(parse(self.s_root.textEdit_3.toPlainText()))
        except ValueError:
            res = False
            res_1 = False
        if res == False:
            msg_box_text = "Ошибка. Поле: 'Дата торгов'. Неверно заданы день и\или месяц и\или год.\n"
        if res_1 == False:
            msg_box_text = msg_box_text + "Ошибка. Поле: 'Дата погашения'. Неверно заданы день и\или месяц и\или год.\n"
        else:
            self.new_row.append(parse(self.s_root.textEdit_2.toPlainText()).strftime(format_us)) #дата торгов для пользователя 1
            self.new_row.append(parse(self.s_root.textEdit_3.toPlainText()).strftime(format_us))  # дата погашения для пользователя 2
            self.new_row.append(parse(self.s_root.textEdit_2.toPlainText()).strftime(format_bd))  # дата торгов для бд 3
            self.new_row.append(parse(self.s_root.textEdit_3.toPlainText()).strftime(format_bd))  # дата погашения для бд 4

        if
        quati = abs(float(self.s_root.textEdit_4.toPlainText()))
        min_pr = abs(float(self.s_root.textEdit_5.toPlainText()))
        max_pr = abs(float(self.s_root.textEdit_6.toPlainText()))
        prodano = self.s_root.textEdit_7.toPlainText()
        if min_pr > max_pr or quati < min_pr or quati > max_pr:
            msg_box_text = msg_box_text + 'Ошибка. Задан неверный ценовой диапазон.\n'
        else:
            self.new_row.append(abs(float(quati))) #текущая цена 5
            self.new_row.append(abs(float(min_pr))) # мин цена 6
            self.new_row.append(abs(float(max_pr))) # макс цена 7
        try:
            abs(int(prodano)) # продано 8
        except ValueError:
            msg_box_text = msg_box_text + "Ошибка. Поле: 'Продано'. Введите целое число."
        else:
            self.new_row.append(abs(int(prodano))) # продано 8

        if len(msg_box_text) != 0:
            war = self.msgBox.warning(self,'Warning',msg_box_text)
            if war == self.msgBox.StandardButton.Ok:
                self.msgBox.close()
        else:
            QSqlQuery(f"""INSERT INTO market(name,torg_date_us,day_end_us,torg_date,day_end,quotation,min_quot,max_quot,num_contr)
                    VALUES ('{self.new_row[0]}','{self.new_row[1]}','{self.new_row[2]}','{self.new_row[3]}','{self.new_row[4]}',{self.new_row[5]},{self.new_row[6]},{self.new_row[7]},{self.new_row[8]})""")
            self.ql_table.select()
            self.s.close()
        print(self.new_row)


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.w = QtWidgets.QMainWindow()
        self.w_root = Ui_MainWindow()
        self.w_root.setupUi(self.w)
        # self.dialog = EditMarket() #наследуем класс
        self.db = connect_db(db_name)
        self.market = ModelMarket(self.db)
        self.struc_fu = ModelStruc_fut(self.db)
        self.msgBox = QMessageBox()
        self.w.setWindowFlags(QtCore.Qt.WindowType.WindowCloseButtonHint | QtCore.Qt.WindowType.MSWindowsFixedSizeDialogHint)

        self.select_table(0)

        self.w_root.pushButton_2.setEnabled(False)
        self.w_root.tableView.selectionModel().selectionChanged.connect(self.activation_button)
        self.w_root.pushButton_2.clicked.connect(self.delete_row)
        self.w_root.comboBox.activated.connect(self.select_table)
        self.w_root.pushButton_4.clicked.connect(self.open_edit_market)
        self.w.show()

    def open_edit_market(self):
        self.dialog_market = EditMarket(self.market, self.struc_fu,self.w_root.tableView)

    def select_table (self, value):
        # if self.w_root.comboBox.currentIndex() == 0:
        if not value:
            self.w_root.tableView.setModel(self.market)
            header_lables_market = ["Код фьючерса", "Дата торгов", "Дата погашения", "Текущая цена", "Мин. цена", "Макс. цена",
                                    "Продано"]
            columns_market = [0, 1, 2, 5, 6, 7, 8]
            i=0
            for header in header_lables_market:
                self.market.setHeaderData(columns_market[i], QtCore.Qt.Orientation.Horizontal, header)
                i+=1
            self.w_root.tableView.setGeometry(QtCore.QRect(0, 150, 750, 451))
            self.w_root.tableView.setFixedWidth(750)
            self.w_root.pushButton_2.setEnabled(False)
            self.w_root.pushButton_4.setEnabled(True)
            self.w_root.tableView.selectionModel().selectionChanged.connect(self.activation_button)
        # if self.w_root.comboBox.currentIndex() == 1:
        if value:
            self.w_root.tableView.setModel(self.struc_fu)
            header_lables_struc_futures = ["Код фьючерса", "Код серии", "Дата исполнения"]
            columns_struc_futures = [0, 1, 2]
            i=0
            for header in header_lables_struc_futures:
                self.struc_fu.setHeaderData(columns_struc_futures[i], QtCore.Qt.Orientation.Horizontal, header)
                i+=1
            self.w_root.tableView.setGeometry(QtCore.QRect(195, 150, 360, 451))
            self.w_root.tableView.setFixedWidth(350)
            self.w_root.pushButton_2.setEnabled(False)
            self.w_root.pushButton_4.setEnabled(False)
            self.w_root.tableView.selectionModel().selectionChanged.connect(self.activation_button)
        self.w_root.tableView.setSortingEnabled(True)
        columns_to_hide = [3, 4]
        for number in columns_to_hide:
            self.w_root.tableView.hideColumn(number)



    def activation_button(self):
        if self.w_root.tableView.selectionModel().selectedRows():
            self.w_root.pushButton_2.setEnabled(True)
        else:
            self.w_root.pushButton_2.setEnabled(False)


    def delete_row(self):
        if not self.w_root.comboBox.currentIndex():
            warning = self.msgBox.question(self, "Warning", "Вы действительно хотите удалить выбранные записи?")
            # self.msgBox.setIcon(QMessageBox.Icon.Question)
            sel = self.w_root.tableView.selectedIndexes()
            if warning == self.msgBox.StandardButton.Yes:
                count = 0
                for index in sel:
                    if count % 7 == 0:
                        self.market.removeRow(index.row())
                        self.market.select()
                    count += 1
        if self.w_root.comboBox.currentIndex():
            warning_1 = self.msgBox.question(self, "Warning", "Вы действительно хотите удалить выбранные записи?\n"
                                                              "Все записи, содержащие информацию по данному фьючерсу, будут так же удалены из таблицы торги")
            # self.msgBox.setIcon(QMessageBox.Icon.Question)
            sel = self.w_root.tableView.selectedIndexes()
            self.name_list = []
            if warning_1 == self.msgBox.StandardButton.Yes:
                count = 0
                for index in sel:
                    if count % 3 == 0:
                        self.name_list.append(self.struc_fu.data(index))
                        self.struc_fu.removeRow(index.row())
                        self.struc_fu.select()
                    count += 1
                self.sql = """DELETE FROM market WHERE name='{0}'""".format(self.name_list[0])
                if len(self.name_list) > 1:
                    for i in self.name_list[1:]:
                        self.sql =self.sql + " OR name='{0}'".format(i)

                QSqlQuery(self.sql)
                self.market.select()
                print(self.name_list)
                print(self.sql)
                print(len(self.name_list))


        self.w_root.pushButton_2.setEnabled(False)

app = QApplication(sys.argv)
ex = App()
app.exec()
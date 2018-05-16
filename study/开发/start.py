# -*- coding: utf-8 -*-
import sys

import os
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtSql import QSqlDatabase, QSqlTableModel
from common import *

def initializeModel(model):
    model.setTable('深渊统计')
    model.setEditStrategy(QSqlTableModel.OnFieldChange)
    model.select()
    model.setHeaderData(日期, Qt.Horizontal, "日期")
    model.setHeaderData(图, Qt.Horizontal, "图")
    model.setHeaderData(角色, Qt.Horizontal, "角色")
    model.setHeaderData(深渊次数, Qt.Horizontal, "深渊次数")
    model.setHeaderData(爆货次数, Qt.Horizontal, "爆货次数")
    model.setHeaderData(灵魂爆数, Qt.Horizontal, "灵魂爆数")
    model.setHeaderData(加百利次数, Qt.Horizontal, "加百利次数")
    model.setHeaderData(晶石, Qt.Horizontal, "晶石")
    model.setHeaderData(SS1, Qt.Horizontal, "SS1")
    model.setHeaderData(SS2, Qt.Horizontal, "SS2")
    model.setHeaderData(SS3, Qt.Horizontal, "SS3")
    model.setHeaderData(SS4, Qt.Horizontal, "SS4")
    model.setHeaderData(SS5, Qt.Horizontal, "SS5")
    model.setHeaderData(SS6, Qt.Horizontal, "SS6")
    model.setHeaderData(SS7, Qt.Horizontal, "SS7")
    model.setHeaderData(SS8, Qt.Horizontal, "SS8")


def createView(title, model):
    view = QTableView()
    view.setModel(model)
    view.setWindowTitle(title)
    return view


def addrow():
    ret = model.insertRows(model.rowCount(), 1)
    print('insertRows=%s' % str(ret))


def findrow(i):
    delrow = i.row()
    print('del row=%s' % str(delrow))


if __name__ == '__main__':
    app = QApplication(sys.argv)

    filename = ".\db\database.db"
    create = not QFile.exists(filename)
    print(create)

    if create:
        common.create_or_open_db(filename)

    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName(filename)
    if not db.open():
        QMessageBox.warning(None, "Reference Data",
            "Database Error: {0}".format(db.lastError().text()))
        sys.exit(1)



    model = QSqlTableModel()
    delrow = -1
    initializeModel(model)
    view1 = createView("Table Model (View 1)", model)
    view1.clicked.connect(findrow)

    dlg = QDialog()
    layout = QVBoxLayout()
    layout.addWidget(view1)
    addBtn = QPushButton("添加一行")
    addBtn.clicked.connect(addrow)
    layout.addWidget(addBtn)

    delBtn = QPushButton("删除一行")
    delBtn.clicked.connect(lambda: model.removeRow(view1.currentIndex().row()))
    layout.addWidget(delBtn)
    dlg.setLayout(layout)
    dlg.setWindowTitle("Database 例子")
    dlg.resize(430, 450)
    dlg.show()
    sys.exit(app.exec_())





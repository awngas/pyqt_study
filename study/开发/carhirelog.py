#!/usr/bin/env python3

import bisect
import os
import sys
from PyQt5.QtCore import (QAbstractTableModel, QDate, QModelIndex,
        QVariant, Qt,pyqtSignal)
from PyQt5.QtWidgets import (QApplication, QMainWindow,
        QShortcut, QTableView)
from PyQt5.QtGui import QKeySequence
import genericdelegates
from common import *
from PyQt5.QtSql import QSqlDatabase,QSqlQuery

#(日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) = range(16)

class DNFSSLog(object):

    def __init__(self,id,日期, 图, 角色, 深渊次数,爆货次数=0,灵魂爆数=0, 加百利次数=0,晶石=0,SS1="",SS2="",SS3="",SS4="",SS5="",SS6="",SS7="",SS8=""):
        self.id = id
        self.日期 = 日期
        self.图 = 图
        self.角色 = 角色
        self.深渊次数 = 深渊次数
        self.爆货次数 = 爆货次数
        self.灵魂爆数 = 灵魂爆数
        self.加百利次数 = 加百利次数
        self.晶石 = 晶石
        self.SS1 = SS1
        self.SS2 = SS2
        self.SS3 = SS3
        self.SS4 = SS4
        self.SS5 = SS5
        self.SS6 = SS6
        self.SS7 = SS7
        self.SS8 = SS8



    def field(self, column):
        if column == 日期:
            return self.日期
        elif column == 图:
            return self.图
        elif column == 角色:
            return self.角色
        elif column == 深渊次数:
            return self.深渊次数
        elif column == 爆货次数:
            return self.爆货次数
        elif column == 灵魂爆数:
            return self.灵魂爆数
        elif column == 加百利次数:
            return self.加百利次数
        elif column == 晶石:
            return self.晶石
        elif column == SS1:
            return self.SS1
        elif column == SS2:
            return self.SS2
        elif column == SS3:
            return self.SS3
        elif column == SS4:
            return self.SS4
        elif column == SS5:
            return self.SS5
        elif column == SS6:
            return self.SS6
        elif column == SS7:
            return self.SS7
        elif column == SS8:
            return self.SS8
        assert False

    def __hash__(self):
        return super(DNFSSLog, self).__hash__()

    def __eq__(self, other):
        if self.日期 != other.日期:
            return False
        if self.图 != other.图:
            return False
        if self.角色 != other.角色:
            return False
        if self.深渊次数 != other.深渊次数:
            return False
        if self.爆货次数 != other.爆货次数:
            return False
        if self.灵魂爆数 != other.灵魂爆数:
            return False
        if self.加百利次数 != other.加百利次数:
            return False
        if self.晶石 != other.晶石:
            return False
        return id(self) == id(other)


    def __lt__(self, other):
        if self.日期 < other.日期:
            return True
        if self.深渊次数 < other.深渊次数:
            return True
        return id(self) < id(other)



class DNFSSLogModel(QAbstractTableModel):
    dataChanged = pyqtSignal(QModelIndex,QModelIndex)
    def __init__(self, parent=None):
        super(DNFSSLogModel, self).__init__(parent)
        self.logs = []


        db = QSqlDatabase.addDatabase("QSQLITE")
        db.setDatabaseName("./db/database.db")
        if not db.open():
            print("数据库没打开!")
            return False;
        query = QSqlQuery()
        query.exec_("select id,日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8 from 深渊统计 ORDER  by 日期 DESC ")
        while query.next():
            id = query.value(0)
            日期 = query.value(1)
            图 = str(query.value(2))
            角色 = str(query.value(3))
            深渊次数 = query.value(4)
            爆货次数 = query.value(5)
            灵魂爆数 = query.value(6)
            加百利次数 = query.value(7)
            晶石 = query.value(8)
            SS1 = str(query.value(9))
            SS2 = str(query.value(10))
            SS3 = str(query.value(11))
            SS4 = str(query.value(12))
            SS5 = str(query.value(13))
            SS6 = str(query.value(14))
            SS7 = str(query.value(15))
            SS8 = str(query.value(16))

            print("{0}: {1} [{2}] {3} {4}".format(日期, 图, 角色, 深渊次数,id))
            log = DNFSSLog(id,日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8)
            bisect.insort(self.logs, log)

    def rowCount(self, index=QModelIndex()):
        return len(self.logs)


    def columnCount(self, index=QModelIndex()):
        return 16


    def data(self, index, role):
        if not index.isValid():
            return QVariant()
        if role == Qt.DisplayRole:
            log = self.logs[index.row()]
            value = log.field(index.column())
            return value
        if (role == Qt.TextAlignmentRole):
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role == Qt.BackgroundColorRole:
            palette = QApplication.palette()
            return QVariant(palette.base())
        return QVariant()

    def updateDataToDb(self,id,value,columnsName):
        query = QSqlQuery()
        query.exec_(
            "update set {0}={1} from 深渊统计 where id ={2}".format(columnsName,value,id))

    # (日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) = range(16)
    def setData(self, index, value, role=Qt.EditRole):
        if (index.isValid() and role == Qt.EditRole):
            log = self.logs[index.row()]
            column = index.column()
            if column == 日期:
                log.日期 = value
                updateDataToDb("日期",value,log.id)
            elif column == 图:
                #log.hired = value.toDate()
                log.图 = value
            elif column == 角色:
                log.角色 = value
            elif column == 深渊次数:
                #log.returned = value.toDate()
                log.深渊次数 = value
            elif column == 爆货次数:
                log.爆货次数 = value
            elif column == 灵魂爆数:
                log.灵魂爆数 = value
            elif column == 加百利次数:
                log.灵魂爆数 = value
            elif column == 晶石:
                log.灵魂爆数 = value
            elif column == SS1:
                log.SS1 = value
            elif column == SS2:
                log.SS2 = value
            elif column == SS3:
                log.SS3 = value
            elif column == SS4:
                log.SS4 = value
            elif column == SS5:
                log.SS5 = value
            elif column == SS6:
                log.SS6 = value
            elif column == SS7:
                log.SS7 = value
            elif column == SS8:
                log.SS8 = value
            self.dataChanged[QModelIndex,QModelIndex].emit(index,index)
            return True
        return False

    def headerData(self, section, orientation, role):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == 日期:
                return "日期"
            elif section == 图:
                return "图"
            elif section == 角色:
                return "角色"
            elif section == 深渊次数:
                return "深渊次数"
            elif section == 爆货次数:
                return "爆货次数"
            elif section == 灵魂爆数:
                return "灵魂爆数"
            elif section == 加百利次数:
                return "加百利次数"
            elif section == 晶石:
                return "晶石"
            elif section == SS1:
                return "SS1"
            elif section == SS2:
                return "SS2"
            elif section == SS3:
                return "SS3"
            elif section == SS4:
                return "SS4"
            elif section == SS5:
                return "SS5"
            elif section == SS6:
                return "SS6"
            elif section == SS7:
                return "SS7"
            elif section == SS8:
                return "SS8"
        return section + 1


    def flags(self, index):
        flag = QAbstractTableModel.flags(self, index)
        flag |= Qt.ItemIsEditable
        return flag


class HireDateColumnDelegate(genericdelegates.DateColumnDelegate):

    def createEditor(self, parent, option, index):
        i = index.sibling(index.row(), RETURNED)
        self.maximum = i.model().data(i, Qt.DisplayRole).addDays(-1)
        return genericdelegates.DateColumnDelegate.createEditor(
                self, parent, option, index)


class ReturnDateColumnDelegate(genericdelegates.DateColumnDelegate):

    def createEditor(self, parent, option, index):
        i = index.sibling(index.row(), HIRED)
        self.minimum = i.model().data(i, Qt.DisplayRole).addDays(1)
        return genericdelegates.DateColumnDelegate.createEditor(
                self, parent, option, index)


class MileageOutColumnDelegate(genericdelegates.IntegerColumnDelegate):

    def createEditor(self, parent, option, index):
        i = index.sibling(index.row(), MILEAGEBACK)
        maximum = i.model().data(i, Qt.DisplayRole)
        self.maximum = 1000000 if maximum == 0 else maximum - 1
        return genericdelegates.IntegerColumnDelegate.createEditor(
                self, parent, option, index)


class MileageBackColumnDelegate(genericdelegates.IntegerColumnDelegate):

    def createEditor(self, parent, option, index):
        i = index.sibling(index.row(), MILEAGEOUT)
        self.minimum = i.model().data(i, Qt.DisplayRole) + 1
        return genericdelegates.IntegerColumnDelegate.createEditor(
                self, parent, option, index)


class MainForm(QMainWindow):

    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        model = DNFSSLogModel(self)

        self.view = QTableView()
        self.view.setModel(model)
        self.view.resizeColumnsToContents()

        delegate = genericdelegates.GenericDelegate(self)
        # delegate.insertColumnDelegate(CUSTOMER,
        #         genericdelegates.PlainTextColumnDelegate())
        # earliest = QDate.currentDate().addYears(-3)
        # delegate.insertColumnDelegate(HIRED,
        #         HireDateColumnDelegate(earliest))
        # delegate.insertColumnDelegate(MILEAGEOUT,
        #         MileageOutColumnDelegate(0, 1000000))
        # delegate.insertColumnDelegate(RETURNED,
        #         ReturnDateColumnDelegate(earliest))
        # delegate.insertColumnDelegate(MILEAGEBACK,
        #         MileageBackColumnDelegate(0, 1000000))
        # delegate.insertColumnDelegate(NOTES,
        #         genericdelegates.RichTextColumnDelegate())

        self.view.setItemDelegate(delegate)
        self.setCentralWidget(self.view)

        QShortcut(QKeySequence("Escape"), self, self.close)
        QShortcut(QKeySequence("Ctrl+Q"), self, self.close)

        self.setWindowTitle("Car Hire Logs")

def initda():
    print(111)
    db = QSqlDatabase.addDatabase("QSQLITE")
    db.setDatabaseName("./db/database.db")
    query = QSqlQuery()
    query.exec_("INSERT INTO 深渊统计 (日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) VALUES "
                "('2018-05-07', '裂缝','hehe',1,2,3,4,5,'SS1','SS2','SS3','SS4','SS5','','','')")
    print(222)
    query.exec_("INSERT INTO 深渊统计 (日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) VALUES "
                "('2018-05-07', '裂缝','123',1,2,3,4,5,'SS1','SS2','SS3','SS4','SS5','','','')")
    query.exec_("INSERT INTO 深渊统计 (日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) VALUES "
                "('2018-05-07', '裂缝','124',1,2,3,4,5,'SS1','SS2','SS3','SS4','SS5','','','')")
    query.exec_("INSERT INTO 深渊统计 (日期, 图, 角色, 深渊次数, 爆货次数, 灵魂爆数,加百利次数, 晶石, SS1,SS2,SS3,SS4,SS5,SS6,SS7,SS8) VALUES "
                "('2018-05-07', '裂缝','453',1,2,3,4,5,'SS1','SS2','SS3','SS4','SS5','','','')")

initda()
app = QApplication(sys.argv)
form = MainForm()
rect = QApplication.desktop().availableGeometry()
form.resize(int(rect.width() * 0.7), int(rect.height() * 0.8))
form.move(0, 0)
form.show()
app.exec_()
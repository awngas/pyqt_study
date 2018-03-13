#!/usr/bin/env python3
import sys
from PyQt5.QtCore import QFile, QTimer, Qt
from PyQt5.QtWidgets import (QApplication, QDialog, QHBoxLayout, QLabel,
                             QMessageBox, QPushButton, QSplitter, QTableView, QVBoxLayout,
                             QWidget)
import ships

# MAC = True
MAC = False

try:
    from PyQt5.QtGui import qt_mac_set_native_menubar
except ImportError:
    MAC = False


class MainForm(QDialog):
    def __init__(self, parent=None):
        super(MainForm, self).__init__(parent)

        self.model = ships.ShipTableModel("ships.dat") #创建一个shipmodel
        tableLabel1 = QLabel("Table &1")
        self.tableView1 = QTableView()
        tableLabel1.setBuddy(self.tableView1)
        self.tableView1.setModel(self.model)
        tableLabel2 = QLabel("Table &2")
        self.tableView2 = QTableView()
        tableLabel2.setBuddy(self.tableView2)
        self.tableView2.setModel(self.model)

        addShipButton = QPushButton("&Add Ship")
        removeShipButton = QPushButton("&Remove Ship")
        quitButton = QPushButton("&Quit")
        if not MAC:
            addShipButton.setFocusPolicy(Qt.NoFocus) #设置按钮接受键盘焦点方式,NoFocus不接受焦点
            removeShipButton.setFocusPolicy(Qt.NoFocus)
            quitButton.setFocusPolicy(Qt.NoFocus)

        buttonLayout = QHBoxLayout()
        buttonLayout.addWidget(addShipButton)
        buttonLayout.addWidget(removeShipButton)
        buttonLayout.addStretch()
        buttonLayout.addWidget(quitButton)
        splitter = QSplitter(Qt.Horizontal)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel1)
        vbox.addWidget(self.tableView1)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        vbox = QVBoxLayout()
        vbox.addWidget(tableLabel2)
        vbox.addWidget(self.tableView2)
        widget = QWidget()
        widget.setLayout(vbox)
        splitter.addWidget(widget)
        layout = QVBoxLayout()
        layout.addWidget(splitter)
        layout.addLayout(buttonLayout)
        self.setLayout(layout)

        # 为每个水平标题连接到sortTable方法上
        for tableView in (self.tableView1, self.tableView2):
            header = tableView.horizontalHeader()  # 返回水平标题,QHeaderView
            header.sectionClicked[int].connect(self.sortTable)  # 点击标题绑定信号,点击某个部分时会发出此信号。该部分的逻辑索引由logicalIndex指定

        addShipButton.clicked.connect(self.addShip)
        removeShipButton.clicked.connect(self.removeShip)
        quitButton.clicked.connect(self.accept)

        self.setWindowTitle("Ships (model)")
        QTimer.singleShot(0, self.initialLoad)  # 设置定时器,启动时间0,调用initialLoad方法初始化数据

    def initialLoad(self):
        if not QFile.exists(self.model.filename):
            self.model.beginResetModel()
            for ship in ships.generateFakeShips():  # generateFakeShips构造Ship对象列表
                self.model.ships.append(ship)
                self.model.owners.add(str(ship.owner))
                self.model.countries.add(str(ship.country))
            self.model.endResetModel()
            self.model.dirty = False
        else:
            try:
                self.model.load()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to load: {0}".format(e))
        self.model.sortByName()
        self.resizeColumns()

    # 对两个表格视图NAME,OWNER,COUNTRY,TEU列,按照内容改变列大小
    def resizeColumns(self):
        for tableView in (self.tableView1, self.tableView2):
            for column in (ships.NAME, ships.OWNER, ships.COUNTRY,
                           ships.TEU):
                tableView.resizeColumnToContents(column)

    # QDialog.reject() 隐藏模式对话框并将result code 设置为Rejected 拒绝
    def reject(self):
        print()
        self.accept()

    # QDialog.accept() 隐藏模式对话框并将result code 设置为Accepted 接受
    def accept(self):
        if (self.model.dirty and
                    QMessageBox.question(self, "Ships - Save?",
                                         "Save unsaved changes?",
                                         QMessageBox.Yes | QMessageBox.No) ==
                    QMessageBox.Yes):
            try:
                self.model.save()
            except IOError as e:
                QMessageBox.warning(self, "Ships - Error",
                                    "Failed to save: {0}".format(e))
        QDialog.accept(self)

    #table视图排序方法
    def sortTable(self, section):
        if section in (ships.OWNER, ships.COUNTRY):
            self.model.sortByCountryOwner()
        else:
            self.model.sortByName()
        self.resizeColumns()

    # 槽方法,添加一个船
    def addShip(self):
        row = self.model.rowCount()  # 获取模型数据条数
        self.model.insertRows(row)   # 在最后插入一条
        index = self.model.index(row, 0) # 获得插入的index
        # 判断键盘焦点在哪个表格视图上
        tableView = self.tableView1
        if self.tableView2.hasFocus():
            tableView = self.tableView2
        tableView.setFocus()  # 设置焦点
        tableView.setCurrentIndex(index) # 设置当前行
        tableView.edit(index) # 编辑当前行

    # 槽方法,删除一个船
    def removeShip(self):
        # 判断键盘焦点在哪个表格视图上
        tableView = self.tableView1
        if self.tableView2.hasFocus():
            tableView = self.tableView2
        index = tableView.currentIndex()
        if not index.isValid():  # PyQt5.QtCore.QModelIndex.isValid() 此模型索引有效返回true,无效返回false
            return
        row = index.row()   # 返回此模型索引引用的行
        name = self.model.data(
            self.model.index(row, ships.NAME))   # QModelIndex QAbstractTableModel.index() 返回指定行,列的索引
        owner = self.model.data(                 # QVariant QAbstractItemModel.data() 返回索引所引用项目的给定角色下存储的数据
            self.model.index(row, ships.OWNER))
        country = self.model.data(
            self.model.index(row, ships.COUNTRY))
        if (QMessageBox.question(self, "Ships - Remove",
                                 "Remove {0} of {1}/{2}?".format(name, owner, country),
                                 QMessageBox.Yes | QMessageBox.No) ==
                QMessageBox.No):
            return
        self.model.removeRows(row)
        self.resizeColumns()


app = QApplication(sys.argv)
form = MainForm()
form.show()
app.exec_()
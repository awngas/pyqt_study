#!/usr/bin/env python3

import sys
from PyQt5.QtCore import QAbstractNativeEventFilter, QPoint, Qt,QCoreApplication
from PyQt5.QtWidgets import QMainWindow, QWidget, QTableView, QApplication, QVBoxLayout, QPushButton, QHBoxLayout, \
    QLineEdit, QListWidget
from PyQt5.QtGui import QStandardItemModel, QBrush, QColor, QStandardItem,QGuiApplication
from abc import abstractmethod
from StockSortFilterProxyModel import *
from StockItemDelegate import *

DropWidgetMaxHeight = 170
DropWidgetMaxWidth = 230


class IView(object):
    @abstractmethod
    def SetMouseOver(self, row):
        pass


class StockTableView(QTableView, IView):
    currHovered = -1
    m_pSourceModel = None

    def __init__(self, model, parent=None):
        super(StockTableView, self).__init__(parent)
        self.currHovered = -1
        self.m_pSourceModel = model
        self.setMouseTracking(True)

    def SetMouseOver(self, row):
        if row == self.currHovered:
            return
        sortModel = self.model()
        if sortModel.rowCount() <= row:
            return
        for col in range(sortModel.columnCount()):
            index = sortModel.index(row, col)
            if index.isValid():
                item = self.m_pSourceModel.itemFromIndex(sortModel.mapToSource(index))
                if item is not None:
                    item.setBackground(QBrush(QColor(43, 92, 151)))
        if self.currHovered != -1:
            self.disableMouseOver()

        self.currHovered = row

    def disableMouseOver(self):
        sortModel = self.model()
        for col in range(sortModel.columnCount()):
            index = sortModel.index(self.currHovered, col)
            if index.isValid():
                item = self.m_pSourceModel.itemFromIndex(sortModel.mapToSource(index))
                if item is not None:
                    item.setBackground(QBrush(QColor(60, 69, 77)))

    def mouseMoveEvent(self, event):
        row = self.rowAt(event.pos().y())
        if row != -1:
            sortModel = self.model()
            for col in range(sortModel.columnCount()):
                index = sortModel.index(self.currHovered, col)
                if index.isValid():
                    item = self.m_pSourceModel.itemFromIndex(sortModel.mapToSource(index))
                    if item is not None:
                        item.setBackground(QBrush(QColor(43, 92, 151)))
        QTableView.mouseMoveEvent(self,event)

    def leaveEvent(self, event):
        self.disableMouseOver()
        return QWidget.leaveEvent(self,event)

    def mousePressEvent(self, event):
        clickRow = self.rowAt(event.pos().y())
        if clickRow != -1:
            sortModel = self.model()
            index = sortModel.index(clickRow, 0)
            if index.isValid():
                item = self.m_pSourceModel.itemFromIndex(sortModel.mapToSource(index))
                if item is not None:
                    print(item.text())
        return QWidget.mousePressEvent(self,event)


class StockListWidgetPrivate():
    m_pListModel = None
    m_pFilterModel = None
    m_pSearchLineEdit = None
    m_pTitleWidget = None
    m_pStockList = None
    m_pStockPreview = None
    m_pStockPreviewWidget = None


class StockListWidget(QWidget, QAbstractNativeEventFilter):
    d_ptr = None

    def __init__(self, parent=None):
        super(StockListWidget, self).__init__(parent)
        self.d_ptr = StockListWidgetPrivate()
        self.InitializeUI()
        self.setStyleSheet("QWidget#StockListTitle{ background:#1B1D21; }"
                           "QPushButton#StockListSearchButton{border:0px;background:white;}"
                           "QLineEdit#StockListSearchEdit{border:0px;background:white;}"
                           "QWidget#StockPreviewWidget{border:0;}"
                           "QWidget#StockPreviewWidget QTableView{border:0;}");
        # QCoreApplication.instance().installNativeEventFilter(self)

    def NativeParentWindowMove(self):
        if self.d_ptr.m_pStockPreviewWidget is not None:
            self.d_ptr.m_pStockPreviewWidget.move(self.d_ptr.m_pTitleWidget.mapToGlobal(QPoint(0, self.d_ptr.m_pTitleWidget.height() - 2)))

    def moveEvent(self, event):
        self.NativeParentWindowMove()
        return QWidget.moveEvent(self,event)

    def nativeEventFilter(self, eventType, message, result):
        if eventType == "windows_generic_MSG" or eventType == "windows_dispatcher_MSG":
            pMsg = message
            if pMsg.message == 0x0003:  # define WM_MOVE 0x0003
                self.NativeParentWindowMove()
        return False

    def func1(self, text):
        if self.d_ptr.m_pFilterModel is not None:
            self.d_ptr.m_pFilterModel.SetFilterContext(text)
        if self.d_ptr.m_pStockPreviewWidget is not None:
            self.d_ptr.m_pStockPreviewWidget.move(
                self.d_ptr.m_pTitleWidget.mapToGlobal(QPoint(0, self.d_ptr.m_pTitleWidget.height())))
            rowHeight = self.d_ptr.m_pStockPreview.rowHeight(0)
            rowCount = self.d_ptr.m_pFilterModel.rowCount()
            if rowHeight * rowCount > DropWidgetMaxHeight:
                self.d_ptr.m_pStockPreviewWidget.setFixedHeight(DropWidgetMaxHeight)
            else:
                self.d_ptr.m_pStockPreviewWidget.setFixedHeight(rowHeight * rowCount)
                self.d_ptr.m_pStockPreviewWidget.show()

    def func2(self):
        if self.d_ptr.m_pStockPreviewWidget is not None:
            self.d_ptr.m_pStockPreviewWidget.setVisible(False)

    def InitializeUI(self):
        backgroundWidget = QWidget()
        mainLayout = QVBoxLayout()

        backgroundWidget.setObjectName("StockListBg")

        mainLayout.setSpacing(0)
        # mainLayout.setMargin(0)

        # 水平编辑框
        self.d_ptr.m_pTitleWidget = QWidget()
        titleLayout = QHBoxLayout()
        searchButton = QPushButton()
        self.d_ptr.m_pSearchLineEdit = QLineEdit()

        self.d_ptr.m_pSearchLineEdit.installEventFilter(self)

        self.d_ptr.m_pSearchLineEdit.textChanged.connect(self.func1)

        self.d_ptr.m_pSearchLineEdit.editingFinished.connect(self.func2)

        self.d_ptr.m_pSearchLineEdit.setPlaceholderText("缩小检索范围")

        self.d_ptr.m_pTitleWidget.setObjectName("StockListTitle")
        searchButton.setObjectName("StockListSearchButton")
        self.d_ptr.m_pSearchLineEdit.setObjectName("StockListSearchEdit")

        self.d_ptr.m_pTitleWidget.setFixedHeight(25)

        titleLayout.setSpacing(0)
        titleLayout.setContentsMargins(10, 2, 10, 2)
        searchButton.setFixedSize(16, 16)

        titleLayout.addWidget(searchButton)
        titleLayout.addWidget(self.d_ptr.m_pSearchLineEdit, 1)
        self.d_ptr.m_pTitleWidget.setLayout(titleLayout)
        mainLayout.addWidget(self.d_ptr.m_pTitleWidget)

        # 已选个股列表
        self.d_ptr.m_pStockList = QListWidget()
        mainLayout.addWidget(self.d_ptr.m_pStockList, 1)

        backgroundWidget.setLayout(mainLayout)

        fwLayout = QVBoxLayout()
        fwLayout.setSpacing(0)
        # fwLayout.setMargin(0)
        fwLayout.addWidget(backgroundWidget)
        self.setLayout(fwLayout)
        # 调用父方法有三种方式
        # Student.__init__(self,name) 使用父类名称直接调用
        # super(Score,self).__init__(name) 通过super函数  super(StockListWidget,self).setLayout(fwLayout)
        # super().__init__(name)

        # 初始化搜索个股列表
        self.d_ptr.m_pStockPreviewWidget = QWidget(self)
        previewLayout = QVBoxLayout()
        self.d_ptr.m_pListModel = QStandardItemModel()
        self.d_ptr.m_pStockPreview = StockTableView(self.d_ptr.m_pListModel)
        self.d_ptr.m_pFilterModel = StockSortFilterProxyModel()

        self.d_ptr.m_pStockPreviewWidget.setObjectName("StockPreviewWidget")

        self.d_ptr.m_pStockPreview.horizontalHeader().setVisible(False)
        self.d_ptr.m_pStockPreview.verticalHeader().setVisible(False)
        self.d_ptr.m_pStockPreview.setShowGrid(False)
        self.d_ptr.m_pStockPreview.horizontalHeader().setStretchLastSection(True)

        self.d_ptr.m_pStockPreview.setMouseTracking(True)
        self.d_ptr.m_pStockPreview.installEventFilter(self)

        previewLayout.setSpacing(0)
        # previewLayout.setMargin(0)

        previewLayout.addWidget(self.d_ptr.m_pStockPreview)
        self.d_ptr.m_pStockPreviewWidget.setLayout(previewLayout)

        # self.model(100, 2)
        for row in range(100):
            for column in range(2):
                item = QStandardItem(str(row + column))
                item.setData(QColor(60, 69, 77), Qt.BackgroundRole)
                item.setSelectable(False)
                self.d_ptr.m_pListModel.setItem(row, column, item)

        itemDelegate = StockItemDelegate(self.d_ptr.m_pStockPreview)
        self.d_ptr.m_pStockPreview.setItemDelegate(itemDelegate)
        itemDelegate.setView(self.d_ptr.m_pStockPreview)

        self.d_ptr.m_pStockPreviewWidget.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.Popup)

        self.d_ptr.m_pFilterModel.setSourceModel(self.d_ptr.m_pListModel)
        self.d_ptr.m_pStockPreview.setModel(self.d_ptr.m_pFilterModel)

        self.d_ptr.m_pStockPreviewWidget.setFixedWidth(DropWidgetMaxWidth)


app = QApplication(sys.argv)
mainWidget = QMainWindow()
w = StockListWidget()
# app.installNativeEventFilter(w)
mainWidget.setCentralWidget(w)
mainWidget.show()
# w.show()
app.exec_()

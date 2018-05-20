#!/usr/bin/env python3


from PyQt5.QtWidgets import QStyledItemDelegate, QStyle


class StockItemDelegatePrivate(object):
    column = 1  # 进度条所在列，下标从0开始
    parent = None
    view = None


class StockItemDelegate(QStyledItemDelegate):
    d_ptr = None

    def __init__(self, parent=None):
        super(StockItemDelegate, self).__init__(parent)
        self.d_ptr = StockItemDelegatePrivate()
        self.d_ptr.parent = parent

    def setView(self, view):
        self.d_ptr.view = view

    def paint(self, painter, option, index):
        opt = option
        self.initStyleOption(opt, index)
        if opt.state and QStyle.State_MouseOver:
            self.d_ptr.view.SetMouseOver(index.row())

        opt.state &= ~QStyle.State_MouseOver
        QStyledItemDelegate.paint(self, painter, opt, index)

    def sizeHint(self, option, index):
        return QStyledItemDelegate.sizeHint(self, option, index)

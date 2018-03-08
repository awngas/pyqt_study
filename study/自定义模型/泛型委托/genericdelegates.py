#!/usr/bin/env python3

from PyQt5.QtCore import (QDate, QSize, Qt)
from PyQt5.QtWidgets import (QApplication, QDateEdit, QLineEdit,
        QSpinBox, QStyledItemDelegate,QStyle)
from PyQt5.QtGui import QColor,QTextDocument
import richtextlineedit


class GenericDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(GenericDelegate, self).__init__(parent)
        self.delegates = {}


    def insertColumnDelegate(self, column, delegate):
        delegate.setParent(self)
        self.delegates[column] = delegate


    def removeColumnDelegate(self, column):
        if column in self.delegates:
            del self.delegates[column]


    def paint(self, painter, option, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.paint(painter, option, index)
        else:
            QStyledItemDelegate.paint(self, painter, option, index)


    def createEditor(self, parent, option, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            return delegate.createEditor(parent, option, index)
        else:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)


    def setEditorData(self, editor, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.setEditorData(editor, index)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        delegate = self.delegates.get(index.column())
        if delegate is not None:
            delegate.setModelData(editor, model, index)
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)


class IntegerColumnDelegate(QStyledItemDelegate):

    def __init__(self, minimum=0, maximum=100, parent=None):
        super(IntegerColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum


    def createEditor(self, parent, option, index):
        spinbox = QSpinBox(parent)
        spinbox.setRange(self.minimum, self.maximum)
        spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        return spinbox


    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setValue(value)


    def setModelData(self, editor, model, index):
        editor.interpretText()
        model.setData(index, editor.value())


class DateColumnDelegate(QStyledItemDelegate):

    def __init__(self, minimum=QDate(),
                 maximum=QDate.currentDate(),
                 format="yyyy-MM-dd", parent=None):
        super(DateColumnDelegate, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.format = format


    def createEditor(self, parent, option, index):
        dateedit = QDateEdit(parent)
        #dateedit=QDateTimeEdit(parent)
        dateedit.setDateRange(self.minimum, self.maximum)
        dateedit.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
        dateedit.setDisplayFormat(self.format)
        dateedit.setCalendarPopup(True)
        return dateedit


    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        #if value.isNull:
        editor.setDate(value)
        #editor.setDisplayFormat(self.format)

    def setModelData(self, editor, model, index):
        model.setData(index, editor.date())
    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.DisplayRole).toString(self.format)
        palette = QApplication.palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.State_Selected:
            document.setHtml("<font color={0}>{1}</font>".format(palette.highlightedText().color().name(),text))
        else:
            document.setHtml(text)
        painter.save()
        color = (palette.highlight().color()
                 if option.state & QStyle.State_Selected
                 else QColor(index.model().data(index,
                             Qt.BackgroundColorRole)))
        painter.fillRect(option.rect, color)
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()


class PlainTextColumnDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(PlainTextColumnDelegate, self).__init__(parent)


    def createEditor(self, parent, option, index):
        lineedit = QLineEdit(parent)
        return lineedit


    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setText(value)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.text())


class RichTextColumnDelegate(QStyledItemDelegate):

    def __init__(self, parent=None):
        super(RichTextColumnDelegate, self).__init__(parent)


    def paint(self, painter, option, index):
        text = index.model().data(index, Qt.DisplayRole)
        palette = QApplication.palette()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        if option.state & QStyle.State_Selected:
            document.setHtml("<font color={0}>{1}</font>".format(palette.highlightedText().color().name(),text))
        else:
            document.setHtml(text)
        painter.save()
        color = (palette.highlight().color()
                 if option.state & QStyle.State_Selected
                 else QColor(index.model().data(index,
                             Qt.BackgroundColorRole)))
        painter.fillRect(option.rect, color)
        painter.translate(option.rect.x(), option.rect.y())
        document.drawContents(painter)
        painter.restore()


    def sizeHint(self, option, index):
        text = index.model().data(index).toString()
        document = QTextDocument()
        document.setDefaultFont(option.font)
        document.setHtml(text)
        return QSize(document.idealWidth() + 5,
                     option.fontMetrics.height())


    def createEditor(self, parent, option, index):
        lineedit = richtextlineedit.RichTextLineEdit(parent)
        return lineedit


    def setEditorData(self, editor, index):
        value = index.model().data(index, Qt.DisplayRole)
        editor.setHtml(value)


    def setModelData(self, editor, model, index):
        model.setData(index, editor.toSimpleHtml())
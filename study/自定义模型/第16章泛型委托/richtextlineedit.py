#!/usr/bin/env python3

import platform
import sys
import html
from PyQt5.QtCore import QSize, Qt,pyqtSignal
from PyQt5.QtGui import QColor, QFont,QFontMetrics, QIcon, QKeySequence, QPixmap,QTextCharFormat
from PyQt5.QtWidgets import QAction,QApplication,QMenu,QTextEdit



class RichTextLineEdit(QTextEdit):
    returnPressed=pyqtSignal()
    (Bold, Italic, Underline, StrikeOut, Monospaced, Sans, Serif,
     NoSuperOrSubscript, Subscript, Superscript) = range(10)


    def __init__(self, parent=None):
        super(RichTextLineEdit, self).__init__(parent)

        self.monofamily = "courier"
        self.sansfamily = "helvetica"
        self.seriffamily = "times"
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setTabChangesFocus(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        fm = QFontMetrics(self.font())
        h = int(fm.height() * (1.4 if platform.system() == "Windows"
                                   else 1.2))
        self.setMinimumHeight(h)
        self.setMaximumHeight(int(h * 1.2))
        self.setToolTip("Press <b>Ctrl+M</b> for the text effects "
                "menu and <b>Ctrl+K</b> for the color menu")


    def toggleItalic(self):
        self.setFontItalic(not self.fontItalic())


    def toggleUnderline(self):
        self.setFontUnderline(not self.fontUnderline())


    def toggleBold(self):
        self.setFontWeight(QFont.Normal
                if self.fontWeight() > QFont.Normal else QFont.Bold)


    def sizeHint(self):
        return QSize(self.document().idealWidth() + 5,
                     self.maximumHeight())


    def minimumSizeHint(self):
        fm = QFontMetrics(self.font())
        return QSize(fm.width("WWWW"), self.minimumHeight())


    def contextMenuEvent(self, event):
        self.textEffectMenu()


    def keyPressEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            handled = False
            if event.key() == Qt.Key_B:
                self.toggleBold()
                handled = True
            elif event.key() == Qt.Key_I:
                self.toggleItalic()
                handled = True
            elif event.key() == Qt.Key_K:
                self.colorMenu()
                handled = True
            elif event.key() == Qt.Key_M:
                self.textEffectMenu()
                handled = True
            elif event.key() == Qt.Key_U:
                self.toggleUnderline()
                handled = True
            if handled:
                event.accept()
                return
        if event.key() in (Qt.Key_Enter, Qt.Key_Return):
            self.returnPressed.emit()
            event.accept()
        else:
            QTextEdit.keyPressEvent(self, event)


    def colorMenu(self):
        pixmap = QPixmap(22, 22)
        menu = QMenu("Colour")
        for text, color in (
                ("&Black", Qt.black),
                ("B&lue", Qt.blue),
                ("Dark Bl&ue", Qt.darkBlue),
                ("&Cyan", Qt.cyan),
                ("Dar&k Cyan", Qt.darkCyan),
                ("&Green", Qt.green),
                ("Dark Gr&een", Qt.darkGreen),
                ("M&agenta", Qt.magenta),
                ("Dark Mage&nta", Qt.darkMagenta),
                ("&Red", Qt.red),
                ("&Dark Red", Qt.darkRed)):
            color = QColor(color)
            pixmap.fill(color)
            action = menu.addAction(QIcon(pixmap), text, self.setColor)
            action.setData(color)
        self.ensureCursorVisible()
        menu.exec_(self.viewport().mapToGlobal(
                   self.cursorRect().center()))


    def setColor(self):
        action = self.sender()
        if action is not None and isinstance(action, QAction):
            color = QColor(action.data())
            if color.isValid():
                self.setTextColor(color)


    def textEffectMenu(self):
        format = self.currentCharFormat()
        menu = QMenu("Text Effect")
        for text, shortcut, data, checked in (
                ("&Bold", "Ctrl+B", RichTextLineEdit.Bold,
                 self.fontWeight() > QFont.Normal),
                ("&Italic", "Ctrl+I", RichTextLineEdit.Italic,
                 self.fontItalic()),
                ("Strike &out", None, RichTextLineEdit.StrikeOut,
                 format.fontStrikeOut()),
                ("&Underline", "Ctrl+U", RichTextLineEdit.Underline,
                 self.fontUnderline()),
                ("&Monospaced", None, RichTextLineEdit.Monospaced,
                 format.fontFamily() == self.monofamily),
                ("&Serifed", None, RichTextLineEdit.Serif,
                 format.fontFamily() == self.seriffamily),
                ("S&ans Serif", None, RichTextLineEdit.Sans,
                 format.fontFamily() == self.sansfamily),
                ("&No super or subscript", None,
                 RichTextLineEdit.NoSuperOrSubscript,
                 format.verticalAlignment() ==
                 QTextCharFormat.AlignNormal),
                ("Su&perscript", None, RichTextLineEdit.Superscript,
                 format.verticalAlignment() ==
                 QTextCharFormat.AlignSuperScript),
                ("Subs&cript", None, RichTextLineEdit.Subscript,
                 format.verticalAlignment() ==
                 QTextCharFormat.AlignSubScript)):
            action = menu.addAction(text, self.setTextEffect)
            if shortcut is not None:
                action.setShortcut(QKeySequence(shortcut))
            action.setData(data)
            action.setCheckable(True)
            action.setChecked(checked)
        self.ensureCursorVisible()
        menu.exec_(self.viewport().mapToGlobal(
                   self.cursorRect().center()))


    def setTextEffect(self):
        action = self.sender()
        if action is not None and isinstance(action, QAction):
            what = action.data()
            if what == RichTextLineEdit.Bold:
                self.toggleBold()
                return
            if what == RichTextLineEdit.Italic:
                self.toggleItalic()
                return
            if what == RichTextLineEdit.Underline:
                self.toggleUnderline()
                return
            format = self.currentCharFormat()
            if what == RichTextLineEdit.Monospaced:
                format.setFontFamily(self.monofamily)
            elif what == RichTextLineEdit.Serif:
                format.setFontFamily(self.seriffamily)
            elif what == RichTextLineEdit.Sans:
                format.setFontFamily(self.sansfamily)
            if what == RichTextLineEdit.StrikeOut:
                format.setFontStrikeOut(not format.fontStrikeOut())
            if what == RichTextLineEdit.NoSuperOrSubscript:
                format.setVerticalAlignment(
                        QTextCharFormat.AlignNormal)
            elif what == RichTextLineEdit.Superscript:
                format.setVerticalAlignment(
                        QTextCharFormat.AlignSuperScript)
            elif what == RichTextLineEdit.Subscript:
                format.setVerticalAlignment(
                        QTextCharFormat.AlignSubScript)
            self.mergeCurrentCharFormat(format)


    def toSimpleHtml(self):
        htmltext = ""
        black = QColor(Qt.black)
        block = self.document().begin()
        while block.isValid():
            iterator = block.begin()
            while iterator != block.end():
                fragment = iterator.fragment()
                if fragment.isValid():
                    format = fragment.charFormat()
                    family = format.fontFamily()
                    color = format.foreground().color()
                    text=html.escape(fragment.text())
                    if (format.verticalAlignment() ==
                        QTextCharFormat.AlignSubScript):
                        text = "<sub>{0}</sub>".format(text)
                    elif (format.verticalAlignment() ==
                          QTextCharFormat.AlignSuperScript):
                        text = "<sup>{0}</sup>".format(text)
                    if format.fontUnderline():
                        text = "<u>{0}</u>".format(text)
                    if format.fontItalic():
                        text = "<i>{0}</i>".format(text)
                    if format.fontWeight() > QFont.Normal:
                        text = "<b>{0}</b>".format(text)
                    if format.fontStrikeOut():
                        text = "<s>{0}</s>".format(text)
                    if color != black or family:
                        attribs = ""
                        if color != black:
                            attribs += ' color="{0}"'.format(color.name())
                        if family:
                            attribs += ' face="{0}"'.format(family)
                        text = "<font{0}>{1}</font>".format(attribs,text)
                    htmltext += text
                iterator += 1
            block = block.next()
        return htmltext

if __name__ == "__main__":
    def printout(lineedit):
        print(str(lineedit.toHtml()))
        print(str(lineedit.toPlainText()))
        print(str(lineedit.toSimpleHtml()))
    app = QApplication(sys.argv)
    lineedit = RichTextLineEdit()
    lineedit.returnPressed.connect(lambda:printout(lineedit))
    lineedit.show()
    lineedit.setWindowTitle("RichTextEdit")
    app.exec_()
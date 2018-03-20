#!/usr/bin/env python3

import platform
import re
from PyQt5.QtCore import (QAbstractTableModel, QDataStream, QFile,
                          QIODevice, QModelIndex,QRegExp, QSize,QVariant, Qt,pyqtSignal)
from PyQt5.QtGui import QColor,QTextDocument
from PyQt5.QtWidgets import QApplication, QWidget,QComboBox, QLineEdit,QSpinBox, QStyle,QStyledItemDelegate, QTextEdit
import richtextlineedit

NAME, OWNER, COUNTRY, DESCRIPTION, TEU = range(5)

MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1


class Ship(object):

    def __init__(self, name, owner, country, teu=0, description=""):
        self.name = name
        self.owner = owner
        self.country = country
        self.teu = teu
        self.description = description


    def __hash__(self):
        return super(Ship, self).__hash__()


    def __lt__(self, other):
        return bool(self.name.lower()<other.name.lower())


    def __eq__(self, other):
        return bool(self.name.lower()==other.name.lower())


class ShipTableModel(QAbstractTableModel):
    dataChanged = pyqtSignal(QModelIndex,QModelIndex)
    def __init__(self, filename=""):
        super(ShipTableModel, self).__init__()
        self.filename = filename
        self.dirty = False
        self.ships = []
        self.owners = set()
        self.countries = set()


    def sortByName(self):
        self.beginResetModel()
        self.ships = sorted(self.ships)
        self.endResetModel()


    def sortByTEU(self):
        self.beginResetModel()
        ships = [(ship.teu, ship) for ship in self.ships]
        ships.sort()
        self.ships = [ship for teu, ship in ships]
        self.endResetModel()


    def sortByCountryOwner(self):
        self.beginResetModel()
        self.ships = sorted(self.ships,
                            key=lambda x: (x.country, x.owner, x.name))
        self.endResetModel()


    def flags(self, index):
        if not index.isValid():
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(QAbstractTableModel.flags(self, index)|
                            Qt.ItemIsEditable)


    def data(self, index, role=Qt.DisplayRole):
        if (not index.isValid() or
            not (0 <= index.row() < len(self.ships))):
            return QVariant()
        ship = self.ships[index.row()]
        column = index.column()
        if role == Qt.DisplayRole:
            if column == NAME:
                return ship.name
            elif column == OWNER:
                return ship.owner
            elif column == COUNTRY:
                return ship.country
            elif column == DESCRIPTION:
                return ship.description
            elif column == TEU:
                return "{0}".format(ship.teu)
        elif role == Qt.TextAlignmentRole:
            if column == TEU:
                return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
        elif role == Qt.TextColorRole and column == TEU:
            if ship.teu < 80000:
                return QVariant(QColor(Qt.black))
            elif ship.teu < 100000:
                return QVariant(QColor(Qt.darkBlue))
            elif ship.teu < 120000:
                return QVariant(QColor(Qt.blue))
            else:
                return QVariant(QColor(Qt.red))
        elif role == Qt.BackgroundColorRole:
            if ship.country in ("Bahamas", "Cyprus", "Denmark",
                    "France", "Germany", "Greece"):
                return QVariant(QColor(250, 230, 250))
            elif ship.country in ("Hong Kong", "Japan", "Taiwan"):
                return QVariant(QColor(250, 250, 230))
            elif ship.country in ("Marshall Islands",):
                return QVariant(QColor(230, 250, 250))
            else:
                return QVariant(QColor(210, 230, 230))
        elif role == Qt.ToolTipRole:
            msg = "<br>(minimum of 3 characters)"
            if column == NAME:
                return ship.name + msg
            elif column == OWNER:
                return ship.owner + msg
            elif column == COUNTRY:
                return ship.country + msg
            elif column == DESCRIPTION:
                return ship.description
            elif column == TEU:
                return "{0} twenty foot equivalents".format(ship.teu)
        return QVariant()


    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:
                return QVariant(int(Qt.AlignLeft|Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight|Qt.AlignVCenter))
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal:
            if section == NAME:
                return "Name"
            elif section == OWNER:
                return "Owner"
            elif section == COUNTRY:
                return "Country"
            elif section == DESCRIPTION:
                return "Description"
            elif section == TEU:
                return "TEU"
        return QVariant(int(section + 1))


    def rowCount(self, index=QModelIndex()):
        return len(self.ships)


    def columnCount(self, index=QModelIndex()):
        return 5


    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.ships):
            ship = self.ships[index.row()]
            column = index.column()
            if column == NAME:
                ship.name = value
            elif column == OWNER:
                ship.owner = value
            elif column == COUNTRY:
                ship.country = value
            elif column == DESCRIPTION:
                ship.description = value
            elif column == TEU:
                if str(value).isdecimal():
                    ship.teu=int(value)
            self.dirty = True
            self.dataChanged[QModelIndex,QModelIndex].emit(index,index)
            return True
        return False


    def insertRows(self, position, rows=1, index=QModelIndex()):
        self.beginInsertRows(QModelIndex(), position, position + rows - 1)
        for row in range(rows):
            self.ships.insert(position + row,
                              Ship(" Unknown", " Unknown", " Unknown"))
        self.endInsertRows()
        self.dirty = True
        return True


    def removeRows(self, position, rows=1, index=QModelIndex()):
        self.beginRemoveRows(QModelIndex(), position, position + rows - 1)
        self.ships = (self.ships[:position] + self.ships[position + rows:])
        self.endRemoveRows()
        self.dirty = True
        return True


    def load(self):
        exception = None
        fh = None
        try:
            if not self.filename:
                raise IOError("no filename specified for loading")
            fh = QFile(self.filename)
            if not fh.open(QIODevice.ReadOnly):
                raise IOError(str(fh.errorString()))
            stream = QDataStream(fh)
            magic = stream.readInt32()
            if magic != MAGIC_NUMBER:
                raise IOError("unrecognized file type")
            fileVersion = stream.readInt16()
            if fileVersion != FILE_VERSION:
                raise IOError("unrecognized file type version")
            self.ships = []
            while not stream.atEnd():
                name = ""
                owner = ""
                country = ""
                description = ""
                name=stream.readQString()
                owner=stream.readQString()
                country=stream.readQString()
                description=stream.readQString()
                teu = stream.readInt32()
                self.ships.append(Ship(name, owner, country, teu,
                                       description))
                self.owners.add(str(owner))
                self.countries.add(str(country))
            self.dirty = False
        except IOError as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


    def save(self):
        exception = None
        fh = None
        try:
            if not self.filename:
                raise IOError("no filename specified for saving")
            fh = QFile(self.filename)
            if not fh.open(QIODevice.WriteOnly):
                raise IOError(str(fh.errorString()))
            stream = QDataStream(fh)
            stream.writeInt32(MAGIC_NUMBER)
            stream.writeInt16(FILE_VERSION)
            stream.setVersion(QDataStream.Qt_5_7)
            for ship in self.ships:
                stream.writeQString(ship.name)
                stream.writeQString(ship.owner)
                stream.writeQString(ship.country)
                stream.writeQString(ship.description)
                stream.writeInt32(ship.teu)
            self.dirty = False
        except IOError as e:
            exception = e
        finally:
            if fh is not None:
                fh.close()
            if exception is not None:
                raise exception


class ShipDelegate(QStyledItemDelegate):
    commitData = pyqtSignal(QWidget)
    closeEditor = pyqtSignal(QWidget)
    def __init__(self, parent=None):
        super(ShipDelegate, self).__init__(parent)


    def paint(self, painter, option, index):
        if index.column() == DESCRIPTION:
            text = str(index.model().data(index))
            palette = QApplication.palette()
            document = QTextDocument()
            document.setDefaultFont(option.font)
            if option.state & QStyle.State_Selected:
                #document.setHtml("<font color={0}>{1}</font>".format("#FF0000",text))
                document.setHtml("<font color={0}>{1}</font>".format(palette.highlightedText().color().name(),text))
            else:
                document.setHtml(text)
            color = (palette.highlight().color()
                     if option.state & QStyle.State_Selected
                     else QColor(index.model().data(index,
                                 Qt.BackgroundColorRole)))
            # print(palette.highlight().color().name())
            painter.save()
            painter.fillRect(option.rect, color)
            painter.translate(option.rect.x(), option.rect.y())
            document.drawContents(painter)
            painter.restore()
        else:
            QStyledItemDelegate.paint(self, painter, option, index)


    def sizeHint(self, option, index):
        fm = option.fontMetrics
        if index.column() == TEU:
            return QSize(fm.width("9,999,999"), fm.height())
        if index.column() == DESCRIPTION:
            text = str(index.model().data(index))
            document = QTextDocument()
            document.setDefaultFont(option.font)
            document.setHtml(text)
            return QSize(document.idealWidth() + 5, fm.height())
        return QStyledItemDelegate.sizeHint(self, option, index)


    def createEditor(self, parent, option, index):
        if index.column() == TEU:
            spinbox = QSpinBox(parent)
            spinbox.setRange(0, 200000)
            spinbox.setSingleStep(1000)
            spinbox.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            #add by yrd
            spinbox.valueChanged.connect(self.commitAndCloseEditor)
            return spinbox
        elif index.column() == OWNER:
            combobox = QComboBox(parent)
            combobox.addItems(sorted(index.model().owners))
            combobox.setEditable(True)
            #add by yrd
            #combobox.currentTextChanged.connect(self.commitAndCloseEditor)
            combobox.editTextChanged.connect(self.commitAndCloseEditor)
            return combobox
        elif index.column() == COUNTRY:
            combobox = QComboBox(parent)
            combobox.addItems(sorted(index.model().countries))
            combobox.setEditable(True)
            #add by yrd
            combobox.editTextChanged.connect(self.commitAndCloseEditor)
            return combobox
        elif index.column() == NAME:
            editor = QLineEdit(parent)
            editor.returnPressed.connect(self.commitAndCloseEditor)
            return editor
        elif index.column() == DESCRIPTION:
            editor = richtextlineedit.RichTextLineEdit(parent)
            editor.returnPressed.connect(self.commitAndCloseEditor)
            return editor
        else:
            return QStyledItemDelegate.createEditor(self, parent, option,
                                                    index)



    def commitAndCloseEditor(self):
        editor = self.sender()
        if isinstance(editor, (QTextEdit, QLineEdit,QSpinBox,QComboBox)):
            self.commitData[QWidget].emit(editor)
            self.closeEditor[QWidget].emit(editor)





    def setEditorData(self, editor, index):
        text = index.model().data(index, Qt.DisplayRole)
        if index.column() == TEU:
            value=int(re.sub("[., ]","",text))
            editor.setValue(value)
        elif index.column() in (OWNER, COUNTRY):
            i = editor.findText(text)
            if i == -1:
                i = 0
            editor.setCurrentIndex(i)
        elif index.column() == NAME:
            editor.setText(text)
        elif index.column() == DESCRIPTION:
            editor.setHtml(text)
        else:
            QStyledItemDelegate.setEditorData(self, editor, index)


    def setModelData(self, editor, model, index):
        if index.column() == TEU:
            model.setData(index, editor.value())
        elif index.column() in (OWNER, COUNTRY):
            text = editor.currentText()
            if len(text) >= 3:
                model.setData(index, text)
        elif index.column() == NAME:
            text = editor.text()
            if len(text) >= 3:
                model.setData(index, text)
        elif index.column() == DESCRIPTION:
            model.setData(index, editor.toSimpleHtml())
        else:
            QStyledItemDelegate.setModelData(self, editor, model, index)


def generateFakeShips():
    for name, owner, country, teu, description in (
("Emma M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
 "<b>W\u00E4rtsil\u00E4-Sulzer RTA96-C</b> main engine,"
 "<font color=green>109,000 hp</font>"),
("MSC Pamela", "MSC", "Liberia", 90449,
 "Draft <font color=green>15m</font>"),
("Colombo Express", "Hapag-Lloyd", "Germany", 93750,
 "Main engine, <font color=green>93,500 hp</font>"),
("Houston Express", "Norddeutsche Reederei", "Germany", 95000,
 "Features a <u>twisted leading edge full spade rudder</u>. "
 "Sister of <i>Savannah Express</i>"),
("Savannah Express", "Norddeutsche Reederei", "Germany", 95000,
 "Sister of <i>Houston Express</i>"),
("MSC Susanna", "MSC", "Liberia", 90449, ""),
("Eleonora M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
 "Captain <i>Hallam</i>"),
("Estelle M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
 "Captain <i>Wells</i>"),
("Evelyn M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
  "Captain <i>Byrne</i>"),
("Georg M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
("Gerd M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
("Gjertrud M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
("Grete M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
("Gudrun M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
("Gunvor M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
("CSCL Le Havre", "Danaos Shipping", "Cyprus", 107200, ""),
("CSCL Pusan", "Danaos Shipping", "Cyprus", 107200,
 "Captain <i>Watts</i>"),
("Xin Los Angeles", "China Shipping Container Lines (CSCL)",
 "Hong Kong", 107200, ""),
("Xin Shanghai", "China Shipping Container Lines (CSCL)", "Hong Kong",
 107200, ""),
("Cosco Beijing", "Costamare Shipping", "Greece", 99833, ""),
("Cosco Hellas", "Costamare Shipping", "Greece", 99833, ""),
("Cosco Guangzho", "Costamare Shipping", "Greece", 99833, ""),
("Cosco Ningbo", "Costamare Shipping", "Greece", 99833, ""),
("Cosco Yantian", "Costamare Shipping", "Greece", 99833, ""),
("CMA CGM Fidelio", "CMA CGM", "France", 99500, ""),
("CMA CGM Medea", "CMA CGM", "France", 95000, ""),
("CMA CGM Norma", "CMA CGM", "Bahamas", 95000, ""),
("CMA CGM Rigoletto", "CMA CGM", "France", 99500, ""),
("Arnold M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
 "Captain <i>Morrell</i>"),
("Anna M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
 "Captain <i>Lockhart</i>"),
("Albert M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
 "Captain <i>Tallow</i>"),
("Adrian M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
 "Captain <i>G. E. Ericson</i>"),
("Arthur M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496, ""),
("Axel M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496, ""),
("NYK Vega", "Nippon Yusen Kaisha", "Panama", 97825, ""),
("MSC Esthi", "MSC", "Liberia", 99500, ""),
("MSC Chicago", "Offen Claus-Peter", "Liberia", 90449, ""),
("MSC Bruxelles", "Offen Claus-Peter", "Liberia", 90449, ""),
("MSC Roma", "Offen Claus-Peter", "Liberia", 99500, ""),
("MSC Madeleine", "MSC", "Liberia", 107551, ""),
("MSC Ines", "MSC", "Liberia", 107551, ""),
("Hannover Bridge", "Kawasaki Kisen Kaisha", "Japan", 99500, ""),
("Charlotte M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Clementine M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Columbine M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Cornelia M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Chicago Express", "Hapag-Lloyd", "Germany", 93750, ""),
("Kyoto Express", "Hapag-Lloyd", "Germany", 93750, ""),
("Clifford M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Sally M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Sine M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Skagen M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Sofie M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Sor\u00F8 M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Sovereing M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Susan M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Svend M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Svendborg M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("A.P. M\u00F8ller", "M\u00E6rsk Line", "Denmark", 91690,
 "Captain <i>Ferraby</i>"),
("Caroline M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Carsten M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Chastine M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("Cornelius M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 91690, ""),
("CMA CGM Otello", "CMA CGM", "France", 91400, ""),
("CMA CGM Tosca", "CMA CGM", "France", 91400, ""),
("CMA CGM Nabucco", "CMA CGM", "France", 91400, ""),
("CMA CGM La Traviata", "CMA CGM", "France", 91400, ""),
("CSCL Europe", "Danaos Shipping", "Cyprus", 90645, ""),
("CSCL Africa", "Seaspan Container Line", "Cyprus", 90645, ""),
("CSCL America", "Danaos Shipping ", "Cyprus", 90645, ""),
("CSCL Asia", "Seaspan Container Line", "Hong Kong", 90645, ""),
("CSCL Oceania", "Seaspan Container Line", "Hong Kong", 90645,
 "Captain <i>Baker</i>"),
("M\u00E6rsk Seville", "Blue Star GmbH", "Liberia", 94724, ""),
("M\u00E6rsk Santana", "Blue Star GmbH", "Liberia", 94724, ""),
("M\u00E6rsk Sheerness", "Blue Star GmbH", "Liberia", 94724, ""),
("M\u00E6rsk Sarnia", "Blue Star GmbH", "Liberia", 94724, ""),
("M\u00E6rsk Sydney", "Blue Star GmbH", "Liberia", 94724, ""),
("MSC Heidi", "MSC", "Panama", 95000, ""),
("MSC Rania", "MSC", "Panama", 95000, ""),
("MSC Silvana", "MSC", "Panama", 95000, ""),
("M\u00E6rsk Stralsund", "Blue Star GmbH", "Liberia", 95000, ""),
("M\u00E6rsk Saigon", "Blue Star GmbH", "Liberia", 95000, ""),
("M\u00E6rsk Seoul", "Blue Star Ship Managment GmbH", "Germany",
 95000, ""),
("M\u00E6rsk Surabaya", "Offen Claus-Peter", "Germany", 98400, ""),
("CMA CGM Hugo", "NSB Niederelbe", "Germany", 90745, ""),
("CMA CGM Vivaldi", "CMA CGM", "Bahamas", 90745, ""),
("MSC Rachele", "NSB Niederelbe", "Germany", 90745, ""),
("Pacific Link", "NSB Niederelbe", "Germany", 90745, ""),
("CMA CGM Carmen", "E R Schiffahrt", "Liberia", 89800, ""),
("CMA CGM Don Carlos", "E R Schiffahrt", "Liberia", 89800, ""),
("CMA CGM Don Giovanni", "E R Schiffahrt", "Liberia", 89800, ""),
("CMA CGM Parsifal", "E R Schiffahrt", "Liberia", 89800, ""),
("Cosco China", "E R Schiffahrt", "Liberia", 91649, ""),
("Cosco Germany", "E R Schiffahrt", "Liberia", 89800, ""),
("Cosco Napoli", "E R Schiffahrt", "Liberia", 89800, ""),
("YM Unison", "Yang Ming Line", "Taiwan", 88600, ""),
("YM Utmost", "Yang Ming Line", "Taiwan", 88600, ""),
("MSC Lucy", "MSC", "Panama", 89954, ""),
("MSC Maeva", "MSC", "Panama", 89954, ""),
("MSC Rita", "MSC", "Panama", 89954, ""),
("MSC Busan", "Offen Claus-Peter", "Panama", 89954, ""),
("MSC Beijing", "Offen Claus-Peter", "Panama", 89954, ""),
("MSC Toronto", "Offen Claus-Peter", "Panama", 89954, ""),
("MSC Charleston", "Offen Claus-Peter", "Panama", 89954, ""),
("MSC Vittoria", "MSC", "Panama", 89954, ""),
("Ever Champion", "NSB Niederelbe", "Marshall Islands", 90449,
 "Captain <i>Phillips</i>"),
("Ever Charming", "NSB Niederelbe", "Marshall Islands", 90449,
 "Captain <i>Tonbridge</i>"),
("Ever Chivalry", "NSB Niederelbe", "Marshall Islands", 90449, ""),
("Ever Conquest", "NSB Niederelbe", "Marshall Islands", 90449, ""),
("Ital Contessa", "NSB Niederelbe", "Marshall Islands", 90449, ""),
("Lt Cortesia", "NSB Niederelbe", "Marshall Islands", 90449, ""),
("OOCL Asia", "OOCL", "Hong Kong", 89097, ""),
("OOCL Atlanta", "OOCL", "Hong Kong", 89000, ""),
("OOCL Europe", "OOCL", "Hong Kong", 89097, ""),
("OOCL Hamburg", "OOCL", "Marshall Islands", 89097, ""),
("OOCL Long Beach", "OOCL", "Marshall Islands", 89097, ""),
("OOCL Ningbo", "OOCL", "Marshall Islands", 89097, ""),
("OOCL Shenzhen", "OOCL", "Hong Kong", 89097, ""),
("OOCL Tianjin", "OOCL", "Marshall Islands", 89097, ""),
("OOCL Tokyo", "OOCL", "Hong Kong", 89097, "")):
        yield Ship(name, owner, country, teu, description)
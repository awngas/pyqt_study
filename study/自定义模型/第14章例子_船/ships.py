#!/usr/bin/env python3

import platform
from PyQt5.QtCore import (QAbstractTableModel, QDataStream, QFile,
                          QIODevice, QModelIndex, QVariant, Qt, pyqtSignal)
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QApplication

NAME, OWNER, COUNTRY, DESCRIPTION, TEU = range(5)

MAGIC_NUMBER = 0x570C4
FILE_VERSION = 1

# 每条船都可以用Ship来表示
class Ship(object):
    def __init__(self, name, owner, country, teu=0, description=""):
        self.name = name            # 名字
        self.owner = owner          # 所属人
        self.country = country      # 国家
        self.teu = teu              # 该船可以放下多少标准集装箱
        self.description = description  # 描述信息

    # 魔术方法:定义hash()方法返回的值
    def __hash__(self):
        return super(Ship, self).__hash__()

    # 魔术方法:定义小于行为
    def __lt__(self, other):
        return bool(self.name.lower())

    # 魔术方法:定义等于行为
    def __eq__(self, other):
        return bool(self.name.lower() == other.name.lower())

# 自定义模型
class ShipTableModel(QAbstractTableModel):
    dataChanged = pyqtSignal(QModelIndex, QModelIndex)

    def __init__(self, filename=""):
        super(ShipTableModel, self).__init__()
        self.filename = filename
        self.dirty = False  # 标识model数据是否做过等该
        self.ships = []
        self.owners = set()
        self.countries = set()

    def sortByName(self):
        self.beginResetModel()
        self.ships = sorted(self.ships)
        self.endResetModel()

    def sortByCountryOwner(self):
        self.beginResetModel()
        self.ships = sorted(self.ships,
                            key=lambda x: (x.country, x.owner, x.name))
        self.endResetModel()

    # 自定义可编辑模型时需要实现: 返回给定索引的项目标志。
    def flags(self, index):
        if not index.isValid():  # 索引无效返回Qt.ItemIsEnabled标识
            return Qt.ItemIsEnabled
        return Qt.ItemFlags(     # 索引有效,在原有标识基础上添加一个Qt.ItemIsEditable(可编辑标识)
            QAbstractTableModel.flags(self, index) |
            Qt.ItemIsEditable)

    # 自定义模型必须实现: 返回给定索引引用的项目和给定的角色下存储的数据。
    # 有关角色见 https://doc.qt.io/qt-5/qt.html#ItemDataRole-enum
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
                return ship.teu
        elif role == Qt.TextAlignmentRole:  # 项目的文本对齐方式
            if column == TEU:
                return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
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
        return QVariant()

    # 以指定的方向返回标题中给定角色和部分的数据。
    # 当orientation是Qt.Vertical时,section会是行偏移,当是Qt.Horizontal时,section是列偏移
    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.TextAlignmentRole:
            if orientation == Qt.Horizontal:  # 列标题左对齐
                return QVariant(int(Qt.AlignLeft | Qt.AlignVCenter))
            return QVariant(int(Qt.AlignRight | Qt.AlignVCenter))  # 行标题右对齐
        if role != Qt.DisplayRole:
            return QVariant()
        if orientation == Qt.Horizontal: # 列偏移从1开始
            if section == NAME:
                return QVariant("Name")
            elif section == OWNER:
                return QVariant("Owner")
            elif section == COUNTRY:
                return QVariant("Country")
            elif section == DESCRIPTION:
                return QVariant("Description")
            elif section == TEU:
                return QVariant("TEU")
        return QVariant(int(section + 1))

    # 自定义模型必须实现: 返回行数
    def rowCount(self, index=QModelIndex()):
        return len(self.ships)

    # 自定义模型必须实现: 返回列数
    def columnCount(self, index=QModelIndex()):
        return 5

    # 自定义可编辑模型时需要实现: 将索引处的项目的角色数据设置为值。
    # 这里忽略了角色,
    def setData(self, index, value, role=Qt.EditRole):
        if index.isValid() and 0 <= index.row() < len(self.ships):
            # self.beginResetModel()
            ship = self.ships[index.row()]  # 根据行号获取数据
            column = index.column()  # 取得列
            if column == NAME:
                ship.name = str(value)
            elif column == OWNER:
                ship.owner = str(value)
            elif column == COUNTRY:
                ship.country = str(value)
            elif column == DESCRIPTION:
                ship.description = str(value)
            elif column == TEU:  # 如果是TEU列,判断是否是数字,是数字才存储
                if str(value).isdecimal():
                    ship.teu = int(value)
            self.dirty = True
            self.dataChanged[QModelIndex, QModelIndex].emit(index, index)
            # self.endResetModel()
            return True
        return False

    # 自定义可编辑模型时需要实现: 插入一行或多行,position插入行的位置
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
        self.ships = (self.ships[:position] +
                      self.ships[position + rows:])
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
                name = stream.readQString()
                owner = stream.readQString()
                country = stream.readQString()
                description = stream.readQString()
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


def generateFakeShips():
    for name, owner, country, teu, description in (
            ("Emma M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
             "W\u00E4rtsil\u00E4-Sulzer RTA96-C main engine,"
             "109,000 hp"),
            ("MSC Pamela", "MSC", "Liberia", 90449,
             "Draft 15m"),
            ("Colombo Express", "Hapag-Lloyd", "Germany", 93750,
             "Main engine, 93,500 hp"),
            ("Houston Express", "Norddeutsche Reederei", "Germany", 95000,
             "Features a twisted leading edge full spade rudder. "
             "Sister of Savannah Express"),
            ("Savannah Express", "Norddeutsche Reederei", "Germany", 95000,
             "Sister of Houston Express"),
            ("MSC Susanna", "MSC", "Liberia", 90449, ""),
            ("Eleonora M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
             "Captain Hallam"),
            ("Estelle M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
             "Captain Wells"),
            ("Evelyn M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 151687,
             "Captain Byrne"),
            ("Georg M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
            ("Gerd M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
            ("Gjertrud M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
            ("Grete M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
            ("Gudrun M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
            ("Gunvor M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 97933, ""),
            ("CSCL Le Havre", "Danaos Shipping", "Cyprus", 107200, ""),
            ("CSCL Pusan", "Danaos Shipping", "Cyprus", 107200,
             "Captain Watts"),
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
             "Captain Morrell"),
            ("Anna M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
             "Captain Lockhart"),
            ("Albert M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
             "Captain Tallow"),
            ("Adrian M\u00E6rsk", "M\u00E6rsk Line", "Denmark", 93496,
             "Captain G. E. Ericson"),
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
             "Captain Ferraby"),
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
             "Captain Baker"),
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
             "Captain Phillips"),
            ("Ever Charming", "NSB Niederelbe", "Marshall Islands", 90449,
             "Captain Tonbridge"),
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

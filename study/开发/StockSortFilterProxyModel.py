#!/usr/bin/env python3

from PyQt5.QtCore import QSortFilterProxyModel, QRegExp


class StockSortFilterProxyModel(QSortFilterProxyModel):
    sortColumn = 0

    def __init__(self, parent=None):
        super(StockSortFilterProxyModel, self).__init__(parent)

    def SetFilterContext(self, pattern):
        self.sortColumn = self.columnCount()
        regExp = QRegExp("*%s*" % (pattern))
        regExp.setPatternSyntax(QRegExp.Wildcard)
        self.setFilterRegExp(regExp)
        print("func:SetFilterContext:heeeeeeeeeeeeeeee")

    def lessThan(self, left, right):
        return QSortFilterProxyModel.lessThan(self, left, right);

    def filterAcceptsRow(self, source_row, source_parent):
        regExp = self.filterRegExp()
        result = False
        for i in range(self.sortColumn):
            print(i)
            index = self.sourceModel().index(source_row, i, source_parent)
            print(self.sourceModel().data(index))
            context = str(self.sourceModel().data(index))
            print(context)
            if regExp.isEmpty() == False:
                regExpStr = regExp.pattern()
                result = regExp.exactMatch(context);
            if result:
                break

        return result


regExp = QRegExp("*%s*" % ("1"))
print(regExp)
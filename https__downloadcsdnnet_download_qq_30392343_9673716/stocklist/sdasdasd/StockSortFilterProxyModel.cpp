#include "stdafx.h"

#include "StockSortFilterProxyModel.h"

StockSortFilterProxyModel::StockSortFilterProxyModel(QObject *parent)
	: QSortFilterProxyModel(parent)
{
	
}

StockSortFilterProxyModel::~StockSortFilterProxyModel()
{
	
}

void StockSortFilterProxyModel::SetFilterContext(const QString & pattern)
{
	sortColumn = columnCount();

    QRegExp regExp(QString("*%1*").arg(pattern));
    regExp.setPatternSyntax(QRegExp::Wildcard);
	setFilterRegExp(regExp);
}

bool StockSortFilterProxyModel::lessThan(const QModelIndex &left
									  , const QModelIndex &right) const
{
	return QSortFilterProxyModel::lessThan(left, right);
}

bool StockSortFilterProxyModel::filterAcceptsRow(int source_row
											  , const QModelIndex & source_parent) const
{
	QRegExp regExp = filterRegExp();
	bool result = false;
	for (int i = 0; i < sortColumn; ++i)
	{
		QModelIndex index = sourceModel()->index(source_row, i, source_parent);
		QString context = sourceModel()->data(index).toString();

		if (regExp.isEmpty() == false)
		{
			QString regExpStr = regExp.pattern();
			result = regExp.exactMatch(context);
		}

		if (result)
		{
			break;
		}
	}

	return result;
}

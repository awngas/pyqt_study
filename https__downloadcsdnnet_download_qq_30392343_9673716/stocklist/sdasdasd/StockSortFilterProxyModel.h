#ifndef CCSORTFILTERPROXYMODEL_H
#define CCSORTFILTERPROXYMODEL_H

#include <QSortFilterProxyModel>

class StockSortFilterProxyModel : public QSortFilterProxyModel
{
	Q_OBJECT

public:
	StockSortFilterProxyModel(QObject *parent = nullptr);
	~StockSortFilterProxyModel();

	void SetFilterContext(const QString & pattern);

protected:
	bool lessThan(const QModelIndex &left
				  , const QModelIndex &right) const;
	bool filterAcceptsRow(int source_row
						  , const QModelIndex & source_parent) const;
private:
	size_t sortColumn = 0;
};

#endif // CCSORTFILTERPROXYMODEL_H

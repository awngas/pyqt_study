#ifndef RLPROGRESSBARDELEGATE_H
#define RLPROGRESSBARDELEGATE_H

#include <QtCore/QScopedPointer>

#include <QtWidgets/QStyledItemDelegate>
#include <QTableView>

class IView;

struct StockItemDelegatePrivate
{
	int column = 1;//进度条所在列，下标从0开始
	QTableView * parent = nullptr;
	IView * view = nullptr;
};

class StockItemDelegate : public QStyledItemDelegate
{
	Q_OBJECT

public:
	StockItemDelegate(QTableView * parent = nullptr);
	~StockItemDelegate(){};

public:
	void setView(IView * view);

protected:
	virtual void paint(QPainter * painter
		, const QStyleOptionViewItem & option
		, const QModelIndex & index) const Q_DECL_OVERRIDE;

	virtual QSize sizeHint(const QStyleOptionViewItem &option,
		const QModelIndex &index) const Q_DECL_OVERRIDE;

private:
	QScopedPointer<StockItemDelegatePrivate> d_ptr;
};

#endif // RLPROGRESSBARDELEGATE_H

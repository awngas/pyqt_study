#include "stdafx.h"

#include "StockListWidget.h"

#include "StockItemDelegate.h"

StockItemDelegate::StockItemDelegate(QTableView * parent)
	: QStyledItemDelegate(parent)
	, d_ptr(new StockItemDelegatePrivate)
{
	d_ptr->parent = parent;
}

void StockItemDelegate::setView(IView * view)
{
	d_ptr->view = view;
}

void StockItemDelegate::paint(QPainter * painter
	, const QStyleOptionViewItem & option
	, const QModelIndex & index) const
{
	QStyleOptionViewItemV4 opt = option;
	initStyleOption(&opt, index);

	if (opt.state & QStyle::State_MouseOver)
	{
		d_ptr->view->SetMouseOver(index.row());
	}

	opt.state &= ~QStyle::State_MouseOver;
	QStyledItemDelegate::paint(painter, opt, index);
}

QSize StockItemDelegate::sizeHint(const QStyleOptionViewItem &option
	, const QModelIndex &index) const
{
	return QStyledItemDelegate::sizeHint(option, index);
}

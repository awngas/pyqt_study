#include "stdafx.h"

#include <QtGui/QStandardItemModel>

#include <QtWidgets/QLineEdit>
#include <QtWidgets/QTableView>
#include <QtWidgets/QListWidget>
#include <QtWidgets/QPushButton>
#include <QtWidgets/QVBoxLayout>
#include <QtWidgets/QHBoxLayout>

#include "StockItemDelegate.h"
#include "StockSortFilterProxyModel.h"

#include "StockListWidget.h"

#define DropWidgetMaxHeight 170
#define DropWidgetMaxWidth 230

StockTableView::StockTableView(QStandardItemModel * model, QWidget * parent) 
	: QTableView(parent)
	, currHovered(-1)
{
	m_pSourceModel = model;
	setMouseTracking(true);
}

void StockTableView::SetMouseOver(int row)
{
	if (row == currHovered)
	{
		return;
	}

	StockSortFilterProxyModel * sortModel = static_cast<StockSortFilterProxyModel *>(model());
	if (sortModel->rowCount() <= row)
	{
		return;
	}
	for (int col = 0; col < sortModel->columnCount(); col++)
	{
		QModelIndex index = sortModel->index(row, col);
		if (index.isValid())
		{
			if (QStandardItem * item = m_pSourceModel->itemFromIndex(sortModel->mapToSource(index)))
			{
				item->setBackground(QBrush(QColor(43, 92, 151)));
			}
		}
	}

	if (currHovered != -1)
	{
		disableMouseOver();
	}
	currHovered = row;
}

void StockTableView::disableMouseOver()
{
	StockSortFilterProxyModel * sortModel = static_cast<StockSortFilterProxyModel *>(model());
	for (int col = 0; col < sortModel->columnCount(); col++)
	{
		QModelIndex index = sortModel->index(currHovered, col);
		if (index.isValid())
		{
			if (QStandardItem * item = m_pSourceModel->itemFromIndex(sortModel->mapToSource(index)))
			{
				item->setBackground(QBrush(QColor(60, 69, 77)));
			}
		}
	}
}

void StockTableView::mouseMoveEvent(QMouseEvent * event)
{
	int row = rowAt(event->pos().y());
	if (row != -1)
	{
		StockSortFilterProxyModel * sortModel = static_cast<StockSortFilterProxyModel *>(model());
		for (int col = 0; col < sortModel->columnCount(); col++)
		{
			QModelIndex index = sortModel->index(currHovered, col);
			if (index.isValid())
			{
				if (QStandardItem * item = m_pSourceModel->itemFromIndex(sortModel->mapToSource(index)))
				{
					item->setBackground(QBrush(QColor(43, 92, 151)));
				}
			}
		}
	}
	QTableView::mouseMoveEvent(event);
}

void StockTableView::leaveEvent(QEvent * event)
{
	disableMouseOver();

    return QWidget::leaveEvent(event);
}

void StockTableView::mousePressEvent(QMouseEvent * event)
{
	int clickRow = rowAt(event->pos().y());
	if (clickRow != -1)
	{
		StockSortFilterProxyModel * sortModel = static_cast<StockSortFilterProxyModel *>(model());
		{
			QModelIndex index = sortModel->index(clickRow, 0);
			if (index.isValid())
			{
				if (QStandardItem * item = m_pSourceModel->itemFromIndex(sortModel->mapToSource(index)))
				{
					qDebug() << item->text();
				}
			}
		}
	}

    return QWidget::mousePressEvent(event);
}

struct StockListWidgetPrivate
{
	QStandardItemModel * m_pListModel = nullptr;
	StockSortFilterProxyModel * m_pFilterModel = nullptr;
	QLineEdit * m_pSearchLineEdit = nullptr;
	QWidget * m_pTitleWidget = nullptr;
	QListWidget * m_pStockList = nullptr;
	StockTableView * m_pStockPreview = nullptr;
	QWidget * m_pStockPreviewWidget	= nullptr;
};

StockListWidget::StockListWidget(QWidget * parent)
	: QWidget(parent)
	, d_ptr(new StockListWidgetPrivate)
{
	InitializeUI();

	setStyleSheet(QString("QWidget#StockListTitle{ background:#1B1D21; }"
		"QPushButton#StockListSearchButton{border:0px;background:white;}"
		"QLineEdit#StockListSearchEdit{border:0px;background:white;}"
		"QWidget#StockPreviewWidget{border:0;}"
		"QWidget#StockPreviewWidget QTableView{border:0;}"));

	qApp->installNativeEventFilter(this);
}

StockListWidget::~StockListWidget()
{

}

void StockListWidget::NativeParentWindowMove()
{
	if (d_ptr->m_pStockPreviewWidget)
	{
		d_ptr->m_pStockPreviewWidget->move(d_ptr->m_pTitleWidget->mapToGlobal(QPoint(0, d_ptr->m_pTitleWidget->height() - 2)));
	}
}

void StockListWidget::moveEvent(QMoveEvent * event)
{
	NativeParentWindowMove();

    return QWidget::moveEvent(event);
}

bool StockListWidget::nativeEventFilter(const QByteArray & eventType, void * message, long * result)
{
	if (eventType == "windows_generic_MSG" || eventType == "windows_dispatcher_MSG")
	{
		MSG * pMsg = reinterpret_cast<MSG *>(message);

		if (pMsg->message == WM_MOVE)
		{
			NativeParentWindowMove();
		}
	}

	return false;
}

void StockListWidget::InitializeUI()
{
	QWidget * backgroundWidget = new QWidget;
	QVBoxLayout * mainLayout = new QVBoxLayout;

	backgroundWidget->setObjectName(QStringLiteral("StockListBg"));

	mainLayout->setSpacing(0);
	mainLayout->setMargin(0);

	//水平编辑框
	d_ptr->m_pTitleWidget = new QWidget;
	QHBoxLayout * titleLayout = new QHBoxLayout;
	QPushButton * searchButton = new QPushButton;
	d_ptr->m_pSearchLineEdit = new QLineEdit;

	d_ptr->m_pSearchLineEdit->installEventFilter(this);

	connect(d_ptr->m_pSearchLineEdit, &QLineEdit::textChanged, this, [this](const QString & text){
		if (d_ptr->m_pFilterModel)
		{
			d_ptr->m_pFilterModel->SetFilterContext(text);
		}
		if (d_ptr->m_pStockPreviewWidget)
		{
			d_ptr->m_pStockPreviewWidget->move(d_ptr->m_pTitleWidget->mapToGlobal(QPoint(0, d_ptr->m_pTitleWidget->height())));
			int rowHeight = d_ptr->m_pStockPreview->rowHeight(0);
			int rowCount = d_ptr->m_pFilterModel->rowCount();
			d_ptr->m_pStockPreviewWidget->setFixedHeight(rowHeight * rowCount > DropWidgetMaxHeight ? DropWidgetMaxHeight : rowHeight * rowCount);
			d_ptr->m_pStockPreviewWidget->show();
		}
	});

	connect(d_ptr->m_pSearchLineEdit, &QLineEdit::editingFinished, this, [this]{
		if (d_ptr->m_pStockPreviewWidget)
		{
			d_ptr->m_pStockPreviewWidget->setVisible(false);
		}
	});

	d_ptr->m_pSearchLineEdit->setPlaceholderText(QStringLiteral("缩小检索范围"));

	d_ptr->m_pTitleWidget->setObjectName(QStringLiteral("StockListTitle"));
	searchButton->setObjectName(QStringLiteral("StockListSearchButton"));
	d_ptr->m_pSearchLineEdit->setObjectName(QStringLiteral("StockListSearchEdit"));

	d_ptr->m_pTitleWidget->setFixedHeight(25);

	titleLayout->setSpacing(0);
	titleLayout->setContentsMargins(10, 2, 10, 2);
	searchButton->setFixedSize(16, 16);

	titleLayout->addWidget(searchButton);
	titleLayout->addWidget(d_ptr->m_pSearchLineEdit, 1);
	d_ptr->m_pTitleWidget->setLayout(titleLayout);
	mainLayout->addWidget(d_ptr->m_pTitleWidget);

	//已选个股列表
	d_ptr->m_pStockList = new QListWidget;
	mainLayout->addWidget(d_ptr->m_pStockList, 1);
	
	backgroundWidget->setLayout(mainLayout);

	QVBoxLayout * fwLayout = new QVBoxLayout;
	fwLayout->setSpacing(0);
	fwLayout->setMargin(0);
	fwLayout->addWidget(backgroundWidget);
	setLayout(fwLayout);

	//初始化搜索个股列表
	d_ptr->m_pStockPreviewWidget = new QWidget(this);
	QVBoxLayout * previewLayout = new QVBoxLayout;
	d_ptr->m_pListModel = new QStandardItemModel;
	d_ptr->m_pStockPreview = new StockTableView(d_ptr->m_pListModel);
	d_ptr->m_pFilterModel = new StockSortFilterProxyModel;

	d_ptr->m_pStockPreviewWidget->setObjectName(QStringLiteral("StockPreviewWidget"));

	d_ptr->m_pStockPreview->horizontalHeader()->setVisible(false);
	d_ptr->m_pStockPreview->verticalHeader()->setVisible(false);
	d_ptr->m_pStockPreview->setShowGrid(false);
	d_ptr->m_pStockPreview->horizontalHeader()->setStretchLastSection(true);

	d_ptr->m_pStockPreview->setMouseTracking(true);
	d_ptr->m_pStockPreview->installEventFilter(this);

	previewLayout->setSpacing(0);
	previewLayout->setMargin(0);

	previewLayout->addWidget(d_ptr->m_pStockPreview);
	d_ptr->m_pStockPreviewWidget->setLayout(previewLayout);

	QStandardItemModel model(100, 2);
	for (int row = 0; row < 100; ++row)
	{
		for (int column = 0; column < 2; ++column)
		{
			QStandardItem * item = new QStandardItem(QString::number(row + column));
			item->setData(QColor(60, 69, 77), Qt::BackgroundRole);
			item->setSelectable(false);
			d_ptr->m_pListModel->setItem(row, column, item);
		}
	}
	StockItemDelegate * itemDelegate = new StockItemDelegate(d_ptr->m_pStockPreview);
	d_ptr->m_pStockPreview->setItemDelegate(itemDelegate);
	itemDelegate->setView(d_ptr->m_pStockPreview);

	d_ptr->m_pStockPreviewWidget->setWindowFlags(Qt::FramelessWindowHint | Qt::Tool | Qt::Popup);

	d_ptr->m_pFilterModel->setSourceModel(d_ptr->m_pListModel);
	d_ptr->m_pStockPreview->setModel(d_ptr->m_pFilterModel);

	d_ptr->m_pStockPreviewWidget->setFixedWidth(DropWidgetMaxWidth);
//	d_ptr->m_pStockPreviewWidget->setVisible(true);
}


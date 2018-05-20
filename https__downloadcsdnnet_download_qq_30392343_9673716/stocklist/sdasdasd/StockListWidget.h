#ifndef STOCKLIST_H
#define STOCKLIST_H

#include <QtCore/QAbstractNativeEventFilter>

#include <QtWidgets/QWidget>
#include <QTableView>
#include <QStandardItemModel>

class IView
{
public:  
	virtual void SetMouseOver(int) = 0;
};

class StockTableView : public QTableView, public IView
{
	Q_OBJECT
public:   
	StockTableView(QStandardItemModel * model, QWidget * parent = 0);
		   
public:
	void SetMouseOver(int);

protected:
	virtual void mouseMoveEvent(QMouseEvent * event) override;
	virtual void leaveEvent(QEvent * event) override;
	virtual void mousePressEvent(QMouseEvent * event) override;

private:
	int currHovered;
	void disableMouseOver();

private:
	QStandardItemModel * m_pSourceModel;
};

struct StockListWidgetPrivate;

class StockListWidget : public QWidget, public QAbstractNativeEventFilter
{
	Q_OBJECT

public:
	StockListWidget(QWidget * parent = nullptr);
	~StockListWidget();

public slots:
	void NativeParentWindowMove();

protected:
	virtual void moveEvent(QMoveEvent * event) override;
	virtual bool nativeEventFilter(const QByteArray & eventType, void * message, long * result) override;

private:
	void InitializeUI();

private:
	QScopedPointer<StockListWidgetPrivate> d_ptr;
};

#endif // STOCKLIST_H

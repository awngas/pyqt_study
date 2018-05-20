#include "stdafx.h"

#include <QtWidgets/QApplication>

#include "StockListWidget.h"

int main(int argc, char *argv[])
{

//    for (int i = 0; i < 10; ++i){
//        qDebug() << i;
//    }

    QApplication a(argc, argv);

    QMainWindow * mainWidget = new QMainWindow;
    StockListWidget w;

    mainWidget->setCentralWidget(&w);
    mainWidget->show();

    return a.exec();
}

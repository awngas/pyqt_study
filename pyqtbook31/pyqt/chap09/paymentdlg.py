#!/usr/bin/env python3
# Copyright (c) 2008-10 Qtrac Ltd. All rights reserved.
# This program or module is free software: you can redistribute it and/or
# modify it under the terms of the GNU General Public License as published
# by the Free Software Foundation, either version 2 of the License, or
# version 3 of the License, or (at your option) any later version. It is
# provided for educational purposes and is distributed in the hope that
# it will be useful, but WITHOUT ANY WARRANTY; without even the implied
# warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See
# the GNU General Public License for more details.

import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import ui_paymentdlg


class PaymentDlg(QDialog, ui_paymentdlg.Ui_PaymentDlg):

    def __init__(self, parent=None):
        super(PaymentDlg, self).__init__(parent)
        self.setupUi(self)
        for lineEdit in (self.forenameLineEdit, self.surnameLineEdit,
                self.checkNumLineEdit, self.accountNumLineEdit,
                self.bankLineEdit, self.sortCodeLineEdit,
                self.creditCardLineEdit):
            self.connect(lineEdit, SIGNAL("textEdited(QString)"),
                         self.updateUi)
        for dateEdit in (self.validFromDateEdit, self.expiryDateEdit):
            self.connect(dateEdit, SIGNAL("dateChanged(QDate)"),
                         self.updateUi)
        self.connect(self.paidCheckBox, SIGNAL("clicked()"),
                     self.updateUi)
        self.updateUi()
        self.forenameLineEdit.setFocus()


    def updateUi(self):
        today = QDate.currentDate()
        enable = (bool(self.forenameLineEdit.text()) or
                  bool(self.surnameLineEdit.text()))
        if enable: ### TODO CHECK THE LOGIC!!!
            enable = (self.paidCheckBox.isChecked() or
                  (bool(self.checkNumLineEdit.text()) and
                   bool(self.accountNumLineEdit.text()) and
                   bool(self.bankLineEdit.text()) and
                   bool(self.sortCodeLineEdit.text())) or
                  (bool(self.creditCardLineEdit.text()) and
                   self.validFromDateEdit.date() <= today and
                   self.expiryDateEdit.date() >= today))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(enable)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    form = PaymentDlg()
    form.show()
    app.exec_()


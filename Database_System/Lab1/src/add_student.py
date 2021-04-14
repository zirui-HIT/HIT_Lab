# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/add_student.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_AddStudentWidget(object):
    def setupUi(self, AddStudentWidget):
        AddStudentWidget.setObjectName("AddStudentWidget")
        AddStudentWidget.resize(800, 480)
        self.student_name_label = QtWidgets.QLabel(AddStudentWidget)
        self.student_name_label.setGeometry(QtCore.QRect(160, 70, 240, 40))
        self.student_name_label.setObjectName("student_name_label")
        self.student_id_label = QtWidgets.QLabel(AddStudentWidget)
        self.student_id_label.setGeometry(QtCore.QRect(160, 150, 240, 40))
        self.student_id_label.setObjectName("student_id_label")
        self.student_name_edit = QtWidgets.QLineEdit(AddStudentWidget)
        self.student_name_edit.setGeometry(QtCore.QRect(400, 70, 240, 40))
        self.student_name_edit.setObjectName("student_name_edit")
        self.student_id_edit = QtWidgets.QLineEdit(AddStudentWidget)
        self.student_id_edit.setGeometry(QtCore.QRect(400, 150, 240, 40))
        self.student_id_edit.setObjectName("student_id_edit")
        self.college_label = QtWidgets.QLabel(AddStudentWidget)
        self.college_label.setGeometry(QtCore.QRect(160, 230, 240, 40))
        self.college_label.setObjectName("college_label")

        self.college_box = QtWidgets.QComboBox(AddStudentWidget)
        self.college_box.setGeometry(QtCore.QRect(400, 230, 240, 40))
        self.college_box.setObjectName("college_box")

        database = sqlite3.connect('Database_System/Lab1/data/data.db')
        colleges = database.execute('SELECT NAME, ID FROM COLLEGE ORDER BY id')
        colleges = [row[0] + ' ' + str(row[1]) for row in colleges]
        self.college_box.addItems(colleges)

        self.accept_button = QtWidgets.QPushButton(AddStudentWidget)
        self.accept_button.setGeometry(QtCore.QRect(280, 320, 240, 40))
        self.accept_button.setObjectName("accept_button")
        self.accept_button.clicked.connect(self._add_student)

        self.retranslateUi(AddStudentWidget)
        QtCore.QMetaObject.connectSlotsByName(AddStudentWidget)
        self.widget = AddStudentWidget

    def retranslateUi(self, AddStudentWidget):
        _translate = QtCore.QCoreApplication.translate
        AddStudentWidget.setWindowTitle(_translate("AddStudentWidget", "添加学生"))
        self.student_name_label.setText(_translate("AddStudentWidget", "学生姓名"))
        self.student_id_label.setText(_translate("AddStudentWidget", "学号"))
        self.accept_button.setText(_translate("AddStudentWidget", "添加"))
        self.college_label.setText(_translate("AddStudentWidget", "所属院系"))

    def _add_student(self):
        database = sqlite3.connect('Database_System/Lab1/data/data.db')

        student_name = self.student_name_edit.text()
        student_id = self.student_id_edit.text()
        if student_id.isnumeric() == False:
            QtWidgets.QMessageBox.warning(self.widget, '警告', '学号必须为纯数字')
            return
        student_id = int(student_id)

        exist_id = database.execute('SELECT id FROM STUDENT')
        for row in exist_id:
            if row[0] == student_id:
                QtWidgets.QMessageBox.warning(self.widget, '警告', '该学号已存在')
                return

        college_id = int((self.college_box.currentText().split())[1])

        command = 'INSERT INTO STUDENT VALUES (%d, \'%s\', %d)' % (
            student_id, student_name, college_id)
        database.execute(command)

        QtWidgets.QMessageBox.information(self.widget, '提示', '添加成功')
        database.execute('COMMIT;')
        database.close()

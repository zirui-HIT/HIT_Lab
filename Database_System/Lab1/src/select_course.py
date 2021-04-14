# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/select_course.ui'
#
# Created by: PyQt5 UI code generator 5.15.2
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.

import sqlite3
from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_SelectCourseWidget(object):
    def setupUi(self, SelectCourseWidget):
        SelectCourseWidget.setObjectName("SelectCourseWidget")
        SelectCourseWidget.resize(800, 480)
        self.student_id_label = QtWidgets.QLabel(SelectCourseWidget)
        self.student_id_label.setGeometry(QtCore.QRect(160, 110, 240, 40))
        self.student_id_label.setObjectName("student_id_label")
        self.student_id_edit = QtWidgets.QLineEdit(SelectCourseWidget)
        self.student_id_edit.setGeometry(QtCore.QRect(400, 110, 240, 40))
        self.student_id_edit.setObjectName("student_id_edit")

        self.accept_button = QtWidgets.QPushButton(SelectCourseWidget)
        self.accept_button.setGeometry(QtCore.QRect(280, 280, 240, 40))
        self.accept_button.setObjectName("accept_button")
        self.accept_button.clicked.connect(self._select_course)

        self.course_box = QtWidgets.QComboBox(SelectCourseWidget)
        self.course_box.setGeometry(QtCore.QRect(400, 190, 240, 40))
        self.course_box.setObjectName("course_box")

        self.course_label = QtWidgets.QLabel(SelectCourseWidget)
        self.course_label.setGeometry(QtCore.QRect(160, 190, 240, 40))
        self.course_label.setObjectName("course_label")

        self.search_button = QtWidgets.QPushButton(SelectCourseWidget)
        self.search_button.setGeometry(QtCore.QRect(660, 110, 75, 40))
        self.search_button.setObjectName("search_button")
        self.search_button.clicked.connect(self._search_course)

        self.retranslateUi(SelectCourseWidget)
        QtCore.QMetaObject.connectSlotsByName(SelectCourseWidget)
        self.widget = SelectCourseWidget

    def retranslateUi(self, SelectCourseWidget):
        _translate = QtCore.QCoreApplication.translate
        SelectCourseWidget.setWindowTitle(
            _translate("SelectCourseWidget", "选课"))
        self.student_id_label.setText(_translate("SelectCourseWidget", "学号"))
        self.accept_button.setText(_translate("SelectCourseWidget", "选课"))
        self.course_label.setText(_translate("SelectCourseWidget", "候选课程"))
        self.search_button.setText(_translate("SelectCourseWidget", "查询"))

    def _search_course(self):
        database = sqlite3.connect('Database_System/Lab1/data/data.db')
        self.course_box.clear()

        student_id = self.student_id_edit.text()
        if student_id.isnumeric() == False:
            QtWidgets.QMessageBox.warning(self.widget, '警告', '学号必须为纯数字')
            return
        student_id = int(student_id)

        students = database.execute(
            'SELECT college_id FROM STUDENT WHERE id = %d' % student_id)
        students = list(students)
        if len(students) == 0:
            QtWidgets.QMessageBox.warning(self.widget, '警告', '该学号不存在')
            return
        college_id = students[0][0]

        courses = database.execute(
            'SELECT name, id FROM COURSE WHERE college_id = %d' % college_id)
        courses = [row[0] + ' ' + str(row[1]) for row in courses]
        self.course_box.addItems(courses)
        self.student_id_edit.setEnabled(False)

    def _select_course(self):
        database = sqlite3.connect('Database_System/Lab1/data/data.db')

        student_id = int(self.student_id_edit.text())
        course_id = int((self.course_box.currentText().split())[1])
        database.execute('INSERT INTO SCHEDULE VALUES (%d, %d)' %
                         (student_id, course_id))

        QtWidgets.QMessageBox.information(self.widget, '提示', '添加成功')
        database.execute('COMMIT;')
        database.close()

        self.student_id_edit.setEnabled(True)

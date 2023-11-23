from PySide6.QtUiTools import QUiLoader
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QTableWidget, QTableWidgetItem, QTableView, QHeaderView, \
    QLabel, QWidget
from ultralytics import YOLO
from webcam_widget import WebcamWidget
from table_model import TableModel
import pandas as pd


class Attendance(QWidget):
    def __init__(self):
        super().__init__()
        self.model = YOLO("best.pt")
        loader = QUiLoader()
        self.window = loader.load('auto-form.ui', None)
        self.window.setParent(self)
        self.people = pd.read_csv('ds.csv')

        self.present = pd.DataFrame({'Họ tên': [],
                                     'MSSV': [],
                                     'ID': []})
        self.absent = self.people

        self.isAttendance = []

        self.layout = QVBoxLayout()
        self.tableModel = TableModel(self.absent)
        self.tableView = QTableView()
        self.tableView.setModel(self.tableModel)
        self.tableView.setColumnWidth(0, 260)
        self.tableView.setColumnWidth(1, 130)
        self.tableView.horizontalHeader().setStretchLastSection(True)
        layout1 = QVBoxLayout()
        layout1.addWidget(self.tableView)
        self.window.absent_2.setLayout(layout1)

        self.tablePresentModel = TableModel(self.present)
        self.tablePresentView = QTableView()
        self.tablePresentView.setModel(self.tablePresentModel)
        self.tablePresentView.setColumnWidth(0, 260)
        self.tablePresentView.setColumnWidth(1, 130)
        self.tablePresentView.horizontalHeader().setStretchLastSection(True)
        layout2 = QVBoxLayout()
        layout2.addWidget(self.tablePresentView)
        self.window.present_2.setLayout(layout2)
        self.window.webcamWidget_2.setLayout(self.layout)
        self.window.btnAttendance_2.clicked.connect(self.detect)
        self.window.btnStop_2.clicked.connect(self.remove_widgets)

    def detect(self):
        self.layout.addWidget(WebcamWidget(model=self.model, setData=self.loadList, setLabel=self.set_label))

    def remove_widgets(self):
        while self.layout.count():
            item = self.layout.takeAt(0)
            widget = item.widget()
            self.isAttendance = widget.isAttendance
            if widget:
                widget.setParent(None)
        print(self.isAttendance)
        self.window.lblName_2.setText('')

    def set_label(self, list):
        text = 'Chào '
        list = self.people['Họ tên'][self.people['ID'].isin(list)]
        if len(list) == 0:
            text = ""
        else:
            for s in list:
                text += s + ', '

        self.window.lblName_2.setText(text)

    def loadList(self, list):
        self.isAttendance = list
        self.absent = self.people[~self.people['ID'].isin(self.isAttendance)]
        self.tableModel.update_data(self.absent)
        self.present = self.people[self.people['ID'].isin(self.isAttendance)]
        self.tablePresentModel.update_data(self.present)

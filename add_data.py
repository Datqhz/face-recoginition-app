import math
import os
import uuid
import cv2
import pandas as pd
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtUiTools import QUiLoader
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QTableWidget, QTableWidgetItem, QTableView, QHeaderView, \
    QWidget, QLabel, QProgressBar, QMessageBox, QTextEdit

from some_module import move_files, write_config


class AddForm(QWidget):
    def __init__(self):
        super().__init__()
        loader = QUiLoader()
        self.window = loader.load('add-form.ui', None)
        self.window.setParent(self)
        self.image_label = QLabel()
        self.image_label.setFixedSize(QSize(640, 480))
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.window.webcamWidget.setLayout(self.main_layout)
        self.numImg = 0;
        self.isGet = False
        self.window.btnGetImage.clicked.connect(self.setup_camera)
        self.window.btnStop.clicked.connect(self.stop)
        self.window.btnGet.clicked.connect(self.collectImage)
        self.window.btnSave.clicked.connect(self.save)
        self.IMAGES_PATH = os.path.join('data', 'images')
        self.LABELS_PATH = os.path.join('data', 'labels')
        self.imageNames = []
        self.window.progressBar.setValue(0)
        self.window.btnSave.setEnabled(False)
        self.window.btnGet.setEnabled(False)
        self.window.btnStop.setEnabled(False)
        self.window.txtName.textChanged.connect(self.txtChange)
        self.window.txtMS.textChanged.connect(self.txtChange)
    def setup_camera(self):
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Thông báo")
        dlg.setInformativeText("Tháo khẩu trang trước khi chụp (nếu có)")
        dlg.setText("Vui lòng di chuyển khuôn mặt của bạn đến vị trí được đánh dấu.\nSau đó ấn 'Lấy' để tiến hành chụp ảnh.")
        dlg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        button = dlg.exec_()
        if button == QMessageBox.Ok:
            self.capture = cv2.VideoCapture(0)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

            self.timer = QTimer()
            self.timer.timeout.connect(self.display_video_stream)
            self.timer.start(30)
            self.window.btnStop.setEnabled(True)
            self.window.btnGetImage.setEnabled(False)
            self.window.btnGet.setEnabled(True)
            self.window.btnSave.setEnabled(False)

    def display_video_stream(self):
        """Read frame from camera and repaint QLabel widget.
            """
        _, frame = self.capture.read()
        width = 640 * 0.39
        height = 480 * 0.67
        x_center = 640 * 0.5
        y_center = 480 * 0.5
        x = x_center - width / 2
        y = y_center - height / 2
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        if self.isGet and self.numImg < 30:
            id = str(uuid.uuid1())
            imgname = os.path.join(self.IMAGES_PATH, f'{id}.jpg')
            cv2.imwrite(imgname, frame)
            self.imageNames.append(id)
            self.numImg += 1
            self.window.progressBar.setValue(math.floor((self.numImg/30)*100))
        elif self.isGet and self.numImg >= 30:
            self.stop()
            name = self.window.txtName.toPlainText()
            ms = self.window.txtMS.toPlainText()
            if not self.checkEmpty():
                self.window.btnSave.setEnabled(True)
        cv2.rectangle(frame, tuple((int(x), int(y))), tuple((int(x + width), int(y + height))), (255, 0, 0), 2)
        image = QImage(frame, frame.shape[1], frame.shape[0],
                       frame.strides[0], QImage.Format_RGB888).rgbSwapped()
        self.image_label.setPixmap(QPixmap.fromImage(image))
        s = " ddd"
        s.isspace()
    def collectImage(self):
        self.deleteImage()
        self.isGet = True
        self.numImg = 0
        self.imageNames = []
        self.window.btnStop.setEnabled(False)
        self.window.progressBar.setValue(0)
        self.window.btnGet.setEnabled(False)


    def stop(self):
        self.timer.stop()
        self.capture.release()
        self.isGet = False
        self.window.btnStop.setEnabled(False)
        self.window.btnGet.setEnabled(False)
        self.window.btnGetImage.setEnabled(True)
        print(self.imageNames)

    def deleteImage(self):
        if len(self.imageNames)!=0:
            for img in self.imageNames:
                os.remove(img)

    def checkEmpty(self):
        name = self.window.txtName.toPlainText()
        ms = self.window.txtMS.toPlainText()
        return not name.strip() or not ms.strip()

    def txtChange(self):
        if self.checkEmpty() or self.numImg<30:
            self.window.btnSave.setEnabled(False)
        elif (not self.checkEmpty()) and self.numImg>=30:
            self.window.btnSave.setEnabled(True)

    def save(self):
        df = pd.read_csv('ds.csv')
        index = df.shape[0]
        name = self.window.txtName.toPlainText()
        ms = self.window.txtMS.toPlainText()
        for i in self.imageNames:
            txtname = os.path.join(self.LABELS_PATH, f'{i}.txt')
            with open(txtname, 'w') as file:
                file.write(f'{str(index)}: 0.5 0.5 0.39 0.67 ')

        move_files(self.imageNames)
        new_row = pd.DataFrame({'Họ tên': [name], 'MSSV': [ms], 'ID': [index]})
        # Concatenate the original DataFrame with the new row
        df = pd.concat([df, new_row], ignore_index=True)
        df.to_csv('ds.csv', index=False)
        write_config(df)
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Thông báo")
        dlg.setText(
            "Lưu thành công")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()

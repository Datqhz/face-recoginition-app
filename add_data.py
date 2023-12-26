import math
import os
import uuid
import cv2
import numpy as np
import pandas as pd
import yaml
from PySide6.QtCore import QTimer, QSize
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtUiTools import QUiLoader
import sys
from PySide6.QtWidgets import QApplication, QVBoxLayout, QTableWidget, QTableWidgetItem, QTableView, QHeaderView, \
    QWidget, QLabel, QProgressBar, QMessageBox, QTextEdit
from ultralytics import YOLO

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
        self.model = YOLO('face.pt')
        self.df = pd.read_csv('ds.csv')
        self.window.btnGetImage.clicked.connect(self.setup_camera)
        self.window.btnStop.clicked.connect(self.stop)
        self.window.btnGet.clicked.connect(self.collectImage)
        self.window.btnSave.clicked.connect(self.save)
        self.window.btnTrain.clicked.connect(self.train)
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
        dlg.setText("Vui lòng di chuyển khuôn mặt của bạn nằm trong khung hình.\nSau đó ấn 'Lấy' để tiến hành chụp ảnh.")
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
        backup_frame = np.copy(frame)
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.model(frame)[0]
        x1, y1, x2, y2 = [0, 0 , 0 ,0]
        for result in results.boxes.data.tolist():
            x1, y1, x2, y2, score, class_id = result
            if score > 0.8:
                cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (255, 0, 0), 2)
                cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2, cv2.LINE_AA)
                # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.isGet and self.numImg < 30:
                    id = str(uuid.uuid1())
                    imgname = os.path.join(self.IMAGES_PATH, f'{id}.jpg')
                    cv2.imwrite(imgname, backup_frame)
                    txtname = os.path.join(self.LABELS_PATH, f'{id}.txt')
                    with open(txtname, 'w') as file:
                        file.write(f'{str(self.df.shape[0])} {str(round((x1 + (x2 - x1) / 2) / 640, 2))} {str(round((y1 + (y2 - y1) / 2) / 480, 2))} {str(round((x2 - x1) / 640, 2))} {str(round((y2 - y1) / 480, 2))}')
                    self.imageNames.append(id)
                    self.numImg += 1
                    self.window.progressBar.setValue(math.floor((self.numImg/30)*100))
            elif self.isGet and self.numImg >= 30:
                self.stop()
                name = self.window.txtName.toPlainText()
                ms = self.window.txtMS.toPlainText()
                if not self.checkEmpty():
                    self.window.btnSave.setEnabled(True)

        image = QImage(frame, frame.shape[1], frame.shape[0],
                       frame.strides[0], QImage.Format_RGB888).rgbSwapped()
        self.image_label.setPixmap(QPixmap.fromImage(image))
    def collectImage(self):
        if(len(os.listdir(os.path.join('data', 'images')))!=0):
            self.resetData()
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

    def resetData(self):
        if len(self.imageNames)!=0:
            for img in self.imageNames:
                os.remove(os.path.join('data', 'images', img+'.jpg'))
                os.remove(os.path.join('data', 'labels', img + '.txt'))
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
        index = self.df.shape[0]
        name = self.window.txtName.toPlainText()
        ms = self.window.txtMS.toPlainText()
        move_files(self.imageNames)
        new_row = pd.DataFrame({'Họ tên': [name], 'MSSV': [ms], 'ID': [index]})
        # Concatenate the original DataFrame with the new row
        self.df = pd.concat([self.df, new_row], ignore_index=True)
        self.df.to_csv('ds.csv', index=False)
        write_config(self.df)
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Thông báo")
        dlg.setText(
            "Lưu thành công")
        dlg.setStandardButtons(QMessageBox.Ok)
        dlg.exec_()
    def train(self):
        with open("data.yaml", 'r') as file:
            yaml_data = yaml.safe_load(file)
        with open("config.yaml", 'r') as file:
            config_data = yaml.safe_load(file)
        if(len(yaml_data['names'])>len(config_data['names'])):
            dlg = QMessageBox(self)
            dlg.setWindowTitle("Thông báo")
            dlg.setText(
                "Hiện đang có thông tin mới của "+str(len(yaml_data['names'])-len(config_data['names']))+" sinh viên./nBạn có muốn đào tạo lại model hay không?")
            dlg.setStandardButtons(QMessageBox.Ok| QMessageBox.Cancel)
            button = dlg.exec_()
            if button == QMessageBox.Ok:
                ms1 = QMessageBox(self)
                ms1.setWindowTitle("Thông báo")
                ms1.setText(
                    "Hiện đang có thông tin mới của " + str(len(yaml_data['names']) - len(
                        config_data['names'])) + " sinh viên. Bạn có muốn đào tạo lại model hay không?")
                ms1.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                btn = ms1.exec_()
                if btn == QMessageBox.Ok:
                    with open('config.yaml', 'w') as outfile:
                        yaml.dump(yaml_data, outfile, default_flow_style=False)
                        model = YOLO("yolov8m.pt")
                        model.train(data="config.yaml", epochs=1)
                        QMessageBox.information(self, "Thông báo", "Đào tạo lại mô hình thành công!")
        else:
            QMessageBox.information(self, "Thông báo", "Hiện tại vẫn chưa có thông tin sinh viên mới. Vui lòng thêm trước khi đào tạo.")


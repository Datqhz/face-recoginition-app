import cv2
from PySide6.QtGui import QImage, QPixmap
from PySide6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget
from PySide6.QtCore import Qt, QTimer, QSize

class WebcamWidget(QWidget):
    def __init__(self, model, setData, setLabel):
        super(WebcamWidget, self).__init__()
        self.image_label = QLabel()
        self.model = model
        self.isAttendance = []
        self.setData = setData
        self.setLabel = setLabel
        self.image_label.setFixedSize(QSize(300,300))
        self.main_layout = QVBoxLayout()
        self.main_layout.addWidget(self.image_label)
        self.setLayout(self.main_layout)
        self.setup_camera()

    def execute_function(self, *args, **kwargs):
        return self.setData(*args, **kwargs)
    def execute_setLabel(self, *args, **kwargs):
        return self.setLabel(*args, **kwargs)
    def setup_camera(self):
            self.capture = cv2.VideoCapture(0)
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 300)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

            self.timer = QTimer()
            self.timer.timeout.connect(self.display_video_stream)
            self.timer.start(30)

    def display_video_stream(self):
            """Read frame from camera and repaint QLabel widget.
            """
            _, frame = self.capture.read()
            results = self.model(frame)[0]
            list = []
            for result in results.boxes.data.tolist():
                x1, y1, x2, y2, score, class_id = result

                if score > 0.75:
                    cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
                    cv2.putText(frame, results.names[int(class_id)].upper(), (int(x1), int(y1 - 10)),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2, cv2.LINE_AA)
                    if class_id not in self.isAttendance:
                        self.isAttendance.append(class_id)
                        self.execute_function(self.isAttendance)
                    list.append(class_id)
                self.execute_setLabel(list)

            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = QImage(frame, frame.shape[1], frame.shape[0],
                           frame.strides[0], QImage.Format_RGB888)
            self.image_label.setPixmap(QPixmap.fromImage(image))
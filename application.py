
from PySide6.QtUiTools import QUiLoader
import sys
from PySide6.QtWidgets import QApplication, QTabWidget

from add_data import AddForm
from detect import Attendance

loader = QUiLoader()
app = QApplication(sys.argv)
window = loader.load('ui.ui', None)
for i in range(window.tabWidget.count()):
    window.tabWidget.removeTab(0)
window.tabWidget.insertTab(0, Attendance(),"Điểm danh")
window.tabWidget.insertTab(1, AddForm(),"Thêm sinh viên")
window.show()
app.exec()
from PySide import QtGui
import ocrSubmit

class ControlMainWindow(QtGui.QMainWindow):
  def __init__(self, parent=None):
    super(ControlMainWindow, self).__init__(parent)
    self.ui =  ocrSubmit.Ui_MainWindow()
    self.ui.setupUi(self)

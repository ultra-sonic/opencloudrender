from PySide import QtGui
import main

class ControlMainWindow(QtGui.QMainWindow):
  def __init__(self, parent=None):
    super(ControlMainWindow, self).__init__(parent)
    self.ui =  main.Ui_MainWindow()
    self.ui.setupUi(self)

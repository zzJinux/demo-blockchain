from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class UpdateSignalLogger(QtCore.QThread):
    
    log_changed = QtCore.pyqtSignal(name="log")

    def __init__(self, log_queue):
        QtCore.QThread.__init__(self)
        self.log_queue = log_queue

    def __del__(self):
        self.wait()
    
    def run(self):
        while True:
            self.log_changed.emit()
            self.msleep(1000)

class QtGuiLogger(object):
    def setup(self, main_frame, log_queue):
        main_frame.setObjectName("main_frame")
        main_frame.resize(581, 565)
        self.title = QtWidgets.QLabel(main_frame)
        self.title.setGeometry(QtCore.QRect(210, 0, 161, 61))
        self.title.setObjectName("title")
        self.log_list = QtWidgets.QListView(main_frame)
        self.log_list.setGeometry(QtCore.QRect(30, 50, 521, 501))
        self.log_list.setObjectName("log_list")

        self.retranslateUi(main_frame)
        QtCore.QMetaObject.connectSlotsByName(main_frame)

        #signal thread setting
        self.log_queue = log_queue
        self.list_update = UpdateSignalLogger(self.log_queue)
        self.list_update.log.connect(self.update_log)
        self.list_update.start()

    def retranslateUi(self, main_frame):
        _translate = QtCore.QCoreApplication.translate
        main_frame.setWindowTitle(_translate("main_frame", "Blockchain Logger"))
        self.title.setText(_translate("main_frame", "Blockchain Network Log"))
    
    def update_log(self):
        model = QtGui.QStandardItemModel()
        for x in self.log_queue:
            model.appendRow(QtGui.QStandardItem(x))
        self.log_list.setModel(model)

class WindowLogger:
    def __init__(self, log_queue):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_frame = QtWidgets.QWidget()
        self.ui = QtGuiLogger()
        self.ui.setup(self.main_frame, log_queue)

    def show(self):
        self.main_frame.show()
        sys.exit(self.app.exec_())
    
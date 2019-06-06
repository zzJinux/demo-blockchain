from PyQt5 import QtCore, QtGui, QtWidgets
import sys

class UpdateSignalNode(QtCore.QThread):
    transaction_changed = QtCore.pyqtSignal(name="transaction")
    block_changed = QtCore.pyqtSignal(name="block")

    def __init__(self, transaction_queue, block_queue):
        QtCore.QThread.__init__(self)
        self.transaction_queue = transaction_queue
        self.block_queue = block_queue
        self.transaction_queue_cache = self.transaction_queue[:]
        self.block_queue_cache = self.block_queue[:]
    
    def __del__(self):
        self.wait()
    
    def run(self):
        while True:
            if set(self.transaction_queue) & set(self.transaction_queue_cache):
                self.transaction_queue_cache = self.transaction_queue[:]
                self.transaction_changed.emit()
            if set(self.block_queue) & set(self.block_queue_cache):
                self.block_queue_cache = self.block_queue[:]
                self.block_changed.emit()
            self.msleep(1000)

class QtGuiNode(object):
    def setup(self, main_frame, transaction_queue, block_queue):
        main_frame.setObjectName("main_frame")
        main_frame.resize(494, 418)
        self.verticalLayoutWidget = QtWidgets.QWidget(main_frame)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(170, 130, 151, 201))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.my_addr = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.my_addr.setObjectName("my_addr")
        self.verticalLayout.addWidget(self.my_addr)
        self.join_addr = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.join_addr.setObjectName("join_addr")
        self.verticalLayout.addWidget(self.join_addr)
        self.join_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.join_button.setObjectName("join_button")
        self.verticalLayout.addWidget(self.join_button)
        self.gen_public_key = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.gen_public_key.setObjectName("gen_public_key")
        self.verticalLayout.addWidget(self.gen_public_key)
        self.gen_message = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.gen_message.setObjectName("gen_message")
        self.verticalLayout.addWidget(self.gen_message)
        self.gen_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.gen_button.setObjectName("gen_button")
        self.verticalLayout.addWidget(self.gen_button)
        self.quit_button = QtWidgets.QPushButton(self.verticalLayoutWidget)
        self.quit_button.setObjectName("quit_button")
        self.verticalLayout.addWidget(self.quit_button)
        self.transaction_list_name = QtWidgets.QLabel(main_frame)
        self.transaction_list_name.setGeometry(QtCore.QRect(40, 70, 71, 16))
        self.transaction_list_name.setObjectName("transaction_list_name")
        self.transaction_list = QtWidgets.QListView(main_frame)
        self.transaction_list.setGeometry(QtCore.QRect(10, 100, 141, 281))
        self.transaction_list.setObjectName("transaction_list")
        self.block_list_name = QtWidgets.QLabel(main_frame)
        self.block_list_name.setGeometry(QtCore.QRect(370, 70, 56, 12))
        self.block_list_name.setObjectName("block_list_name")
        self.node_name = QtWidgets.QLabel(main_frame)
        self.node_name.setGeometry(QtCore.QRect(220, 10, 71, 31))
        self.node_name.setObjectName("node_name")
        self.shorthand_name = QtWidgets.QLineEdit(main_frame)
        self.shorthand_name.setGeometry(QtCore.QRect(210, 40, 71, 31))
        self.shorthand_name.setObjectName("shorthand_name")
        self.block_list = QtWidgets.QListView(main_frame)
        self.block_list.setGeometry(QtCore.QRect(340, 100, 141, 281))
        self.block_list.setObjectName("block_list")

        self.join_button.pressed.connect(self.join_slot)
        self.gen_button.pressed.connect(self.gen_slot)
        self.quit_button.pressed.connect(self.quit_slot)

        self.retranslateUi(main_frame)
        QtCore.QMetaObject.connectSlotsByName(main_frame)

        #signal thread setting
        self.transaction_queue = transaction_queue
        self.block_queue = block_queue
        self.list_update = UpdateSignalNode(self.transaction_queue, self.block_queue)
        self.list_update.transaction.connect(self.update_transaction_list)
        self.list_update.block.connect(self.update_block_list)
        self.list_update.start()

    def retranslateUi(self, main_frame):
        _translate = QtCore.QCoreApplication.translate
        main_frame.setWindowTitle(_translate("main_frame", "BlockChain Node"))
        self.join_button.setText(_translate("main_frame", "Join"))
        self.quit_button.setText(_translate("main_frame", "Quit"))
        self.gen_button.setText(_translate("main_frame", "Generate Transaciton"))
        self.transaction_list_name.setText(_translate("main_frame", "Transaction"))
        self.block_list_name.setText(_translate("main_frame", "Block"))
        self.node_name.setText(_translate("main_frame", "USER"))

    def set_join_button(self, callback):
        self.join_callback = callback

    def set_gen_button(self, callback):
        self.gen_callback = callback

    def set_quit_button(self, callback):
        self.quit_callback = callback

    def join_slot(self):
        self.join_callback(str(self.join_addr.text()))

    def gen_slot(self):
        self.gen_callback(str(self.gen_public_key.text()), str(self.gen_message.text()))

    def quit_slot(self):
        self.quit_callback()

    def update_transaction_list(self):
        model = QtGui.QStandardItemModel()
        for x in self.transaction_queue:
            model.appendRow(QtGui.QStandardItem(x))
        self.transaction_list.setModel(model)
    
    def update_block_list(self):
        model = QtGui.QStandardItemModel()
        for x in self.block_queue:
            model.appendRow(QtGui.QStandardItem(x))
        self.block_list.setModel(model)

class WindowNode:
    def __init__(self, node_type, shorthand, address, join_callback_func, quit_callback_func, gen_callback_func, transaction_queue, blcok_queue):
        self.app = QtWidgets.QApplication(sys.argv)
        self.main_frame = QtWidgets.QWidget()
        self.ui = QtGuiNode()
        self.ui.setup(self.main_frame, transaction_queue, blcok_queue)
        
        if node_type == "miner":
            self.ui.node_name.setText("MINER")
            self.ui.gen_button.setText("Generate Block")
            self.ui.gen_public_key.setParent(None)

        self.ui.set_join_button(join_callback_func)
        self.ui.set_quit_button(quit_callback_func)
        self.ui.set_gen_button(gen_callback_func)
        self.ui.shorthand_name.setText(shorthand)
        self.ui.my_addr.setText(address)

    def show(self):
        self.main_frame.show()
        sys.exit(self.app.exec_())

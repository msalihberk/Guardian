from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenuBar, QPushButton, QSizePolicy, QStatusBar,
    QVBoxLayout, QWidget, QMessageBox, QFileDialog)
import qdarkstyle
import hashlib
import os
import sys
import math

from PySide6.QtCore import QThread, Signal

database = "Database/full_sha256.txt"
db_lines = 959882

class HashCheckThread(QThread):
    progress = Signal(int)
    result = Signal(bool, str)
    error = Signal(str)

    def __init__(self, location, parent=None):
        super().__init__(parent)
        self.location = location

    def run(self):
        hash_value = ""
        try:
            with open(self.location, 'rb') as file:
                file_content = file.read()
                hash_value = hashlib.sha256(file_content).hexdigest()
        except FileNotFoundError:
            self.error.emit("File Not Found!")
            return
        except Exception as e:
            self.error.emit(str(e))
            return
        try:
            with open(database, 'r') as db:
                for idx, line in enumerate(db):
                    percent = math.floor(((idx+1)/db_lines) * 100)
                    self.progress.emit(percent)
                    if hash_value == line.strip():
                        self.result.emit(True, hash_value)
                        return
                self.result.emit(False, hash_value)
        except FileNotFoundError:
            self.error.emit("Database Not Found!")
        except Exception as e:
            self.error.emit(str(e))

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.setFixedSize(1000, 700)
        self.location = ""
        self.thread = None
        self.ui.SelectLocation.clicked.connect(self.selectLocation)
        self.ui.ScanBtn.clicked.connect(self.scan)

    def selectLocation(self):
        self.location = QFileDialog.getOpenFileName(self, "Select File")[0]

    def scan(self):
        if not self.location:
            QMessageBox.warning(self, "Warning", "Please select a file!")
            return
        self.ui.proportion.setText("%0")
        self.ui.ScanBtn.setEnabled(False)
        self.thread = HashCheckThread(self.location)
        self.thread.progress.connect(self.update_progress)
        self.thread.result.connect(self.scan_result)
        self.thread.error.connect(self.scan_error)
        self.thread.finished.connect(lambda: self.ui.ScanBtn.setEnabled(True))
        self.thread.start()

    def update_progress(self, percent):
        self.ui.proportion.setText(f"%{percent}")

    def scan_result(self, virus_found, hash_value):
        if virus_found:
            QMessageBox.critical(self, "Critical", f"Virus Detected! SHA256 {hash_value}")
        else:
            QMessageBox.information(self, "Info", "Virus Not Detected")

    def scan_error(self, message):
        QMessageBox.warning(self, "Warning", message)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"Guardian")
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setMinimumSize(QSize(1000, 700))
        self.centralwidget.setMaximumSize(QSize(1200, 900))
        # Modern dark background
        self.centralwidget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23272f, stop:1 #10131a);
        """)
        self.verticalLayoutWidget_2 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        # Kartı ortalamak için daha büyük ve ortalanmış bir alan
        self.verticalLayoutWidget_2.setGeometry(QRect(200, 90, 600, 520))
        self.verticalLayoutWidget_2.setStyleSheet("""
            background: rgba(30, 34, 44, 0.97);
            border-radius: 32px;
            box-shadow: 0 12px 48px 0 rgba(0,0,0,0.45);
        """)
        self.verticalLayout_2 = QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout = QVBoxLayout()
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.MainLabel_2 = QLabel(self.verticalLayoutWidget_2)
        self.MainLabel_2.setObjectName(u"MainLabel_2")
        font = QFont()
        font.setFamilies([u"Montserrat Black", u"Arial Black", u"Segoe UI"])
        font.setBold(True)
        font.setPointSize(48)
        self.MainLabel_2.setFont(font)
        self.MainLabel_2.setStyleSheet("""
            font-weight: 900;
            font-size: 48px;
            color: #00e676;
            letter-spacing: 6px;
            text-shadow: 0 2px 16px #00e67644;
        """)
        self.MainLabel_2.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout.addWidget(self.MainLabel_2)

        self.MainLabel = QLabel(self.verticalLayoutWidget_2)
        self.MainLabel.setObjectName(u"MainLabel")
        self.MainLabel.setStyleSheet("""
            font-weight: 700;
            font-size: 28px;
            color: #e0e0e0;
            margin-bottom: 16px;
            letter-spacing: 2px;
        """)
        self.MainLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.verticalLayout.addWidget(self.MainLabel)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.ScanBtn = QPushButton(self.verticalLayoutWidget_2)
        self.ScanBtn.setObjectName(u"ScanBtn")
        font1 = QFont()
        font1.setFamilies([u"Montserrat", u"Segoe UI"])
        font1.setBold(True)
        font1.setPointSize(16)
        self.ScanBtn.setFont(font1)
        self.ScanBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ScanBtn.setStyleSheet("""
            QPushButton {
                padding: 14px 32px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00e676, stop:1 #00bfa5);
                color: #23272f;
                box-shadow: 0 2px 8px #00e67644;
                transition: 0.2s;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00bfa5, stop:1 #00e676);
                color: #fff;
            }
        """)
        self.horizontalLayout.addWidget(self.ScanBtn)

        self.SelectLocation = QPushButton(self.verticalLayoutWidget_2)
        self.SelectLocation.setObjectName(u"SelectLocation")
        self.SelectLocation.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.SelectLocation.setFont(font1)
        self.SelectLocation.setStyleSheet("""
            QPushButton {
                padding: 14px 32px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23272f, stop:1 #10131a);
                color: #00e676;
                border: 2px solid #00e676;
                margin-left: 16px;
                transition: 0.2s;
            }
            QPushButton:hover {
                background: #00e676;
                color: #23272f;
            }
        """)
        self.horizontalLayout.addWidget(self.SelectLocation)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.horizontalLayout_3 = QHBoxLayout()
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.proportion = QLabel(self.verticalLayoutWidget_2)
        self.proportion.setObjectName(u"proportion")
        font2 = QFont()
        font2.setFamilies([u"JetBrains Mono", u"Consolas", u"Rockwell"])
        font2.setBold(True)
        font2.setPointSize(22)
        font2.setUnderline(False)
        self.proportion.setFont(font2)
        self.proportion.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.proportion.setStyleSheet("""
            font-weight: bold;
            font-size: 32px;
            color: #00e676;
            background: rgba(0,0,0,0.15);
            border-radius: 8px;
            padding: 12px 0;
            margin-top: 32px;
            margin-bottom: 8px;
            letter-spacing: 2px;
        """)
        self.proportion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.horizontalLayout_3.addWidget(self.proportion)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.verticalLayout_2.addLayout(self.verticalLayout)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 900, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"Guardian", None))
        self.MainLabel_2.setText(QCoreApplication.translate("MainWindow", u"GUARDIAN", None))
        self.MainLabel.setText(QCoreApplication.translate("MainWindow", u"Virus Scanner", None))
#if QT_CONFIG(tooltip)
        self.ScanBtn.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Scan File</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.ScanBtn.setText(QCoreApplication.translate("MainWindow", u"Scan", None))
#if QT_CONFIG(tooltip)
        self.SelectLocation.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select File</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.SelectLocation.setText(QCoreApplication.translate("MainWindow", u"Select Location", None))
        self.proportion.setText(QCoreApplication.translate("MainWindow", u"%0", None))
    # retranslateUi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
    win = MainWindow()
    win.setWindowIcon(QIcon("Images/icon.png"))
    win.show()
    sys.exit(app.exec())
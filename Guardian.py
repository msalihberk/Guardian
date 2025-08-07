from PySide6.QtCore import QCoreApplication, QMetaObject, QRect, QSize, Qt, QThread, Signal
from PySide6.QtGui import QCursor, QFont, QIcon, QGuiApplication
from PySide6.QtWidgets import (QApplication, QHBoxLayout, QLabel, QMainWindow,
    QMenuBar, QPushButton, QStatusBar, QVBoxLayout, QWidget, QMessageBox, 
    QFileDialog)
import qdarkstyle
import hashlib
import sys
import os
import math
import json

def addline():
    json.dump()

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def report(self):
    hash_value = ""
    try:
        with open(self.location, 'rb') as file:
            file_content = file.read()
            hash_value = hashlib.sha256(file_content).hexdigest()
    except FileNotFoundError:
        QMessageBox.warning(self, 'Error', 'File not found!')
        return
    except Exception as error:
        QMessageBox.warning(self, 'Error', str(error))
        return
    try:
        with open(saves, 'r') as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"line": 959882, "reportedHashes": []}
    if hash_value in data.get("reportedHashes", []):
        QMessageBox.information(self, 'Info', 'This file is already reported as virus!')
        return
    data["reportedHashes"].append(hash_value)
    if "line" in data and isinstance(data["line"], int):
        data["line"] += 1
    else:
        data["line"] = 1
    try:
        with open(saves, 'w') as f:
            json.dump(data, f, indent=4)
    except Exception as error:
        QMessageBox.warning(self, 'Error', f'Failed to update report json: {error}')
        return
    try:
        with open(database, 'a') as db:
            db.write('\n' + hash_value)
        QMessageBox.information(self, 'Info', 'File successfully reported as virus!')
    except FileNotFoundError:
        QMessageBox.warning(self, 'Error', 'Database not found!')
    except Exception as error:
        QMessageBox.warning(self, 'Error', str(error))

data = {"line":959882, "reportedHashes":[]}
database = "Database/full_sha256.txt"
saves = "Database/saves.json"
if os.path.exists(saves):
    try:
        with open(saves, 'r') as _save:
            data = json.load(_save)
    except (json.JSONDecodeError, FileNotFoundError):
        data = {"line":959882, "reportedHashes":[]}
        with open(saves, 'w') as _save:
            json.dump(data, _save, indent=4)
else:
    with open(saves, 'w') as _save:
        json.dump(data, _save, indent=4)
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
            with open(saves, 'r') as f:
                data = json.load(f)
                db_lines = data["line"]
                for hash in data["reportedHashes"]:
                    if hash_value == hash:
                        self.result.emit(True, hash_value)
                        return
        except:pass
        try:
            last_emitted_percent = -5
            with open(database, 'r') as db:
                for idx, line in enumerate(db):
                    percent = math.floor(((idx+1)/db_lines) * 100)
                    if percent - last_emitted_percent >= 5:
                        self.progress.emit(percent)
                        last_emitted_percent = percent
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
        self.location = ""
        self.thread = None
        self.ui.SelectLocation.clicked.connect(self.selectLocation)
        self.ui.ScanBtn.clicked.connect(self.scan)
        self.ui.ReportBtn.clicked.connect(self.report)
        self.ui.WhitelistBtn.clicked.connect(self.add_to_whitelist)  

        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        self.resize(window_width, window_height)
        self.setMinimumSize(QSize(1000, 700))
        self.setMaximumSize(QSize(window_width, window_height))

        self.move((screen_width - window_width) // 2, (screen_height - window_height) // 2)

    def add_to_whitelist(self):
        hash_value = ""
        if not self.location:
            QMessageBox.warning(self, "Warning", "Please select a file!")
            return
        try:
            with open(self.location, 'rb') as file:
                file_content = file.read()
                hash_value = hashlib.sha256(file_content).hexdigest()
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'File not found!')
            return
        except Exception as error:
            QMessageBox.warning(self, 'Error', str(error))
            return
        try:
            with open(saves, 'r') as wl:
                if hash_value in [line.strip() for line in wl]:
                    QMessageBox.information(self, 'Info', 'This file is already in whitelist!')
                    return
        except FileNotFoundError:
            pass
        except Exception as error:
            QMessageBox.warning(self, 'Error', str(error))
            return
        try:
            with open(saves, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {"line": 959882, "reportedHashes": []}
        if not (hash_value in data.get("reportedHashes", [])):
            QMessageBox.information(self, 'Info', 'This file is already added whitelist!')
            return
        data["reportedHashes"].remove(hash_value)
        if "line" in data and isinstance(data["line"], int):
            data["line"] -= 1
        else:
            data["line"] = 0
        try:
            with open(saves, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as error:
            QMessageBox.warning(self, 'Error', f'Failed to update report json: {error}')
            return
        try:
            with open(database, 'r+') as db:
                old_db = db.read()
                new_db = old_db.replace(str(hash_value), '')
                db.write(new_db)
                QMessageBox.information(self, 'Info', 'File successfully added whitelist!')
        except FileNotFoundError:
            QMessageBox.warning(self, 'Error', 'Database not found!')
        except Exception as error:
            QMessageBox.warning(self, 'Error', str(error))
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
    
    def report(self):
        if not self.location:
            QMessageBox.warning(self, "Warning", "Please select a file!")
            return
        
        answer = QMessageBox.question(self, 'Question', 'Do You Want To Report The File? ', defaultButton=QMessageBox.No)
        if answer == QMessageBox.Yes:
            report(self)

    def update_progress(self, percent):
        self.ui.proportion.setText(f"%{percent}")

    def scan_result(self, virus_found, hash_value):
        if virus_found:
            self.ui.proportion.setText('%100')
            QMessageBox.critical(self, "Critical", f"Virus Detected! SHA256 {hash_value}")
            self.ui.proportion.setText('%0')
        else:
            QMessageBox.information(self, "Info", "Virus Not Detected")
            self.ui.proportion.setText('%0')

    def scan_error(self, message):
        QMessageBox.warning(self, "Warning", message)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"Guardian")
        MainWindow.setAutoFillBackground(False)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")

        screen = QGuiApplication.primaryScreen().availableGeometry()
        screen_width = screen.width()
        screen_height = screen.height()

        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        self.centralwidget.setMinimumSize(QSize(1000, 700))
        self.centralwidget.setMaximumSize(QSize(window_width, window_height))

        self.centralwidget.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #23272f, stop:1 #10131a);
        """)
        self.verticalLayoutWidget_2 = QWidget(self.centralwidget)
        self.verticalLayoutWidget_2.setObjectName(u"verticalLayoutWidget_2")
        
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
        self.horizontalLayout = QHBoxLayout(self.verticalLayoutWidget_2)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
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
        self.ReportBtn = QPushButton(self.verticalLayoutWidget_2)
        self.ReportBtn.setObjectName(u"ReportBtn")
        self.WhitelistBtn = QPushButton(self.verticalLayoutWidget_2)
        self.WhitelistBtn.setObjectName(u"WhitelistBtn")
        font1 = QFont()
        font1.setFamilies([u"Montserrat", u"Segoe UI"])
        font1.setBold(True)
        font1.setPointSize(14)
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
        self.WhitelistBtn.setFont(font1)
        self.WhitelistBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.WhitelistBtn.setStyleSheet("""
            QPushButton {
                padding: 14px 32px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #00ff26, stop:1 #ceff00);
                color: #23272f;
                box-shadow: 0 2px 8px #00e67644;
                transition: 0.2s;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ceff00, stop:1 #00ff26);
                color: #fff;
            }
        """)
        self.horizontalLayout.addWidget(self.WhitelistBtn)
        self.ReportBtn.setFont(font1)
        self.ReportBtn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.ReportBtn.setStyleSheet("""
            QPushButton {
                padding: 14px 32px;
                border-radius: 12px;
                font-weight: bold;
                font-size: 20px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff0000, stop:1 #ff7a00);
                color: #23272f;
                box-shadow: 0 2px 8px #00e67644;
                transition: 0.2s;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #ff7a00, stop:1 #ff0000);
                color: #fff;
            }
        """)
        self.horizontalLayout.addWidget(self.ReportBtn)

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
        self.WhitelistBtn.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Add To Whitelist</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.WhitelistBtn.setText(QCoreApplication.translate("MainWindow", u"Whitelist", None))
#if QT_CONFIG(tooltip)
        self.ReportBtn.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Report Virus</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.ReportBtn.setText(QCoreApplication.translate("MainWindow", u"Report", None))
#if QT_CONFIG(tooltip)
        self.SelectLocation.setToolTip(QCoreApplication.translate("MainWindow", u"<html><head/><body><p>Select File</p></body></html>", None))
#endif // QT_CONFIG(tooltip)
        self.SelectLocation.setText(QCoreApplication.translate("MainWindow", u"Select File", None))
        self.proportion.setText(QCoreApplication.translate("MainWindow", u"%0", None))
    # retranslateUi

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyside6())
    win = MainWindow()
    icon_path = resource_path("icon.ico")
    if os.path.exists(icon_path):
        win.setWindowIcon(QIcon(icon_path))
    win.setWindowIcon(QIcon("Images/icon.ico"))
    win.show()
    sys.exit(app.exec())
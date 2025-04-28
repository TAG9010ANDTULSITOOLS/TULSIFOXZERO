import sys
import random
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
                             QPushButton, QLabel, QLineEdit, QHBoxLayout, QTextEdit, QCheckBox, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QTimer
from PyQt5.QtGui import QPalette, QColor, QFont

class BrowserTab(QWidget):
    def __init__(self, parent=None, dark_mode=True, adblock_enabled=True, firewall_enabled=True):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.browser = QWebEngineView()
        self.fake_mac = self.generate_fake_mac()

        self.address_bar = QLineEdit()
        self.address_bar.returnPressed.connect(self.load_url)

        self.mac_label = QLabel(f"Fake MAC: {self.fake_mac}")
        self.mac_label.setFont(QFont('Courier', 10))

        self.layout.addWidget(self.mac_label)
        self.layout.addWidget(self.address_bar)
        self.layout.addWidget(self.browser)

        self.setLayout(self.layout)

        self.browser.urlChanged.connect(self.update_url_bar)

        self.adblock_enabled = adblock_enabled
        self.firewall_enabled = firewall_enabled
        self.dark_mode = dark_mode

        if self.dark_mode:
            self.enable_dark_mode()

    def generate_fake_mac(self):
        return "02:" + ":".join(["%02x" % random.randint(0, 255) for _ in range(5)])

    def load_url(self):
        url = self.address_bar.text()
        if not url.startswith('http'):
            url = 'http://' + url
        if self.firewall_enabled and any(bad in url for bad in ['malware', 'phishing', 'ads']):
            QMessageBox.warning(self, "Firewall Blocked", "Blocked potentially dangerous domain.")
            return
        self.browser.setUrl(QUrl(url))

    def update_url_bar(self, q):
        self.address_bar.setText(q.toString())

    def enable_dark_mode(self):
        palette = self.browser.palette()
        palette.setColor(QPalette.Base, QColor(30, 30, 30))
        palette.setColor(QPalette.Text, Qt.white)
        self.browser.setPalette(palette)
class TulsiFoxZero(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("TULSIFOXZERO")
        self.resize(1200, 800)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dark_mode = True
        self.adblock_enabled = True
        self.firewall_enabled = True

        self.init_ui()
        self.show_splash()

    def init_ui(self):
        toolbar = QWidget()
        layout = QHBoxLayout()

        new_tab_btn = QPushButton("New Tab")
        new_tab_btn.clicked.connect(self.add_tab)

        settings_btn = QPushButton("Settings")
        settings_btn.clicked.connect(self.open_settings)

        view_source_btn = QPushButton("View Source")
        view_source_btn.clicked.connect(self.open_source_viewer)

        layout.addWidget(new_tab_btn)
        layout.addWidget(settings_btn)
        layout.addWidget(view_source_btn)

        toolbar.setLayout(layout)

        self.addToolBar(Qt.TopToolBarArea, self.create_toolbar(toolbar))

        self.add_tab()

    def create_toolbar(self, widget):
        from PyQt5.QtWidgets import QToolBar
        toolbar = QToolBar()
        toolbar.addWidget(widget)
        return toolbar

    def add_tab(self):
        tab = BrowserTab(dark_mode=self.dark_mode,
                         adblock_enabled=self.adblock_enabled,
                         firewall_enabled=self.firewall_enabled)
        self.tabs.addTab(tab, "New Tab")

    def open_settings(self):
        self.settings_window = SettingsWindow(self)
        self.settings_window.show()

    def open_source_viewer(self):
        self.source_window = SourceCodeWindow(self)
        self.source_window.show()

    def show_splash(self):
        splash = SplashScreen(self)
        splash.show()
        QTimer.singleShot(2500, splash.close)  # 2.5 seconds splash screen
class SettingsWindow(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.setWindowTitle("Settings")

        layout = QVBoxLayout()

        self.dark_mode_checkbox = QCheckBox("Dark Mode")
        self.dark_mode_checkbox.setChecked(self.browser.dark_mode)

        self.adblock_checkbox = QCheckBox("Ad Blocker")
        self.adblock_checkbox.setChecked(self.browser.adblock_enabled)

        self.firewall_checkbox = QCheckBox("Firewall")
        self.firewall_checkbox.setChecked(self.browser.firewall_enabled)

        save_btn = QPushButton("Save Settings")
        save_btn.clicked.connect(self.save_settings)

        layout.addWidget(self.dark_mode_checkbox)
        layout.addWidget(self.adblock_checkbox)
        layout.addWidget(self.firewall_checkbox)
        layout.addWidget(save_btn)

        self.setLayout(layout)

    def save_settings(self):
        self.browser.dark_mode = self.dark_mode_checkbox.isChecked()
        self.browser.adblock_enabled = self.adblock_checkbox.isChecked()
        self.browser.firewall_enabled = self.firewall_checkbox.isChecked()

        QMessageBox.information(self, "Settings Saved", "Please restart the browser to apply all changes.")

class SourceCodeWindow(QWidget):
    def __init__(self, browser):
        super().__init__()
        self.browser = browser
        self.setWindowTitle("View Source Code")

        layout = QVBoxLayout()

        self.code_viewer = QTextEdit()
        self.code_viewer.setReadOnly(True)
        self.load_code()

        tulsi_blind_mode_btn = QPushButton("TULSI BLIND MODE")
        tulsi_blind_mode_btn.clicked.connect(self.open_blind_mode)

        layout.addWidget(self.code_viewer)
        layout.addWidget(tulsi_blind_mode_btn)

        self.setLayout(layout)

    def load_code(self):
        try:
            with open(sys.argv[0], 'r') as f:
                code = f.read()
                self.code_viewer.setPlainText(code)
        except Exception as e:
            self.code_viewer.setPlainText(f"Error loading code: {str(e)}")

    def open_blind_mode(self):
        self.blind_window = BlindModeWindow(self)
        self.blind_window.show()
class BlindModeWindow(QWidget):
    def __init__(self, source_window):
        super().__init__()
        self.source_window = source_window
        self.setWindowTitle("TULSI BLIND MODE")

        layout = QVBoxLayout()

        self.editor = QTextEdit()
        self.editor.setPlainText(self.source_window.code_viewer.toPlainText())

        self.undo_button = QPushButton("Undo Changes")
        self.undo_button.clicked.connect(self.undo_changes)

        self.check_errors_button = QPushButton("Check for Errors")
        self.check_errors_button.clicked.connect(self.check_errors)

        layout.addWidget(self.editor)
        layout.addWidget(self.undo_button)
        layout.addWidget(self.check_errors_button)

        self.setLayout(layout)

        self.original_code = self.editor.toPlainText()

    def undo_changes(self):
        self.editor.setPlainText(self.original_code)

    def check_errors(self):
        temp_code = self.editor.toPlainText()
        try:
            compile(temp_code, '<string>', 'exec')
            QMessageBox.information(self, "Check Complete", "No syntax errors detected.")
        except Exception as e:
            QMessageBox.warning(self, "Syntax Error", f"Error detected:\n{str(e)}")

class SplashScreen(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.SplashScreen | Qt.FramelessWindowHint)
        self.setAutoFillBackground(True)

        palette = self.palette()
        palette.setColor(QPalette.Window, Qt.black)
        self.setPalette(palette)

        layout = QVBoxLayout()
        self.label = QLabel("🦊 TULSIFOXZERO\nNo Masters. No Trackers.\nOnly Freedom.")
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setStyleSheet("QLabel { color : white; font-size: 24px; }")

        layout.addWidget(self.label)
        self.setLayout(layout)

        self.resize(500, 300)
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TulsiFoxZero()
    window.show()
    app.exec_()

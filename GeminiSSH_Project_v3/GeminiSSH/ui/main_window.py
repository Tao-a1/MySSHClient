import json
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QTabWidget, 
                             QHBoxLayout, QPushButton, QLabel, QStatusBar, QMessageBox, QFileDialog)
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt

from ui.login_tab import LoginTab
from ui.terminal_tab import TerminalTab
from core.ssh_manager import SSHManager

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gemini SSH Client")
        self.resize(1000, 700)
        
        # Initialize Core Logic
        self.ssh_manager = SSHManager()
        self.ssh_manager.connection_status.connect(self.update_status)
        self.ssh_manager.log_message.connect(self.append_log)

        # === Menu Bar ===
        menu = self.menuBar()
        file_menu = menu.addMenu("&File")
        
        load_action = QAction("Load Profile", self)
        load_action.setShortcut("Ctrl+O")
        load_action.triggered.connect(self.load_profile)
        file_menu.addAction(load_action)

        save_action = QAction("Save Profile", self)
        save_action.setShortcut("Ctrl+S")
        save_action.triggered.connect(self.save_profile)
        file_menu.addAction(save_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)

        # 1. Top Bar (Connect/Disconnect Buttons)
        top_bar = QHBoxLayout()
        self.btn_login = QPushButton("Login")
        self.btn_login.clicked.connect(self.handle_login)
        self.btn_logout = QPushButton("Logout")
        self.btn_logout.setEnabled(False)
        self.btn_logout.clicked.connect(self.handle_logout)
        
        top_bar.addWidget(QLabel("Profile: Default"))
        top_bar.addStretch()
        top_bar.addWidget(self.btn_login)
        top_bar.addWidget(self.btn_logout)
        main_layout.addLayout(top_bar)

        # 2. Tabs (Like Bitvise)
        self.tabs = QTabWidget()
        
        self.login_tab = LoginTab()
        self.terminal_tab = TerminalTab()
        self.terminal_tab.bind_manager(self.ssh_manager)
        
        self.tabs.addTab(self.login_tab, "Login")
        self.tabs.addTab(QWidget(), "Options") 
        self.tabs.addTab(self.terminal_tab, "Terminal")
        self.tabs.addTab(QWidget(), "SFTP") 
        self.tabs.addTab(QWidget(), "Services") 
        
        main_layout.addWidget(self.tabs)

        # 3. Activity Log (Bottom area like Bitvise)
        main_layout.addWidget(QLabel("Activity Log:"))
        self.log_area = QLabel("Ready.")
        self.log_area.setStyleSheet("background-color: white; border: 1px solid #ccc; padding: 5px;")
        self.log_area.setFixedHeight(100)
        self.log_area.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        self.log_area.setWordWrap(True)
        main_layout.addWidget(self.log_area)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Disconnected")

    def handle_login(self):
        config = self.login_tab.get_config()
        if not config['host']:
            QMessageBox.warning(self, "Error", "Host is required!")
            return
        
        self.btn_login.setEnabled(False)
        self.log_area.setText(f"Connecting to {config['host']}...")
        
        # Start connection in a separate thread (handled by SSHManager)
        self.ssh_manager.connect(config)

    def handle_logout(self):
        self.ssh_manager.disconnect()

    def update_status(self, connected, message):
        if connected:
            self.status_bar.showMessage(f"Connected: {message}")
            self.btn_login.setEnabled(False)
            self.btn_logout.setEnabled(True)
            self.tabs.setCurrentIndex(2) # Switch to Terminal tab (Simulated)
        else:
            self.status_bar.showMessage(f"Disconnected: {message}")
            self.btn_login.setEnabled(True)
            self.btn_logout.setEnabled(False)

    def append_log(self, text):
        current = self.log_area.text()
        self.log_area.setText(current + "\n" + text)
        # Keep only last few lines to prevent overflow in this simple label
        lines = self.log_area.text().split('\n')
        if len(lines) > 6:
            self.log_area.setText("\n".join(lines[-6:]))

    def save_profile(self):
        fname, _ = QFileDialog.getSaveFileName(self, "Save Profile", "", "JSON Files (*.json)")
        if fname:
            config = self.login_tab.get_config()
            try:
                with open(fname, 'w') as f:
                    json.dump(config, f, indent=4)
                self.status_bar.showMessage(f"Profile saved to {fname}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save profile: {e}")

    def load_profile(self):
        fname, _ = QFileDialog.getOpenFileName(self, "Load Profile", "", "JSON Files (*.json)")
        if fname:
            try:
                with open(fname, 'r') as f:
                    config = json.load(f)
                self.login_tab.set_config(config)
                self.status_bar.showMessage(f"Profile loaded from {fname}", 3000)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load profile: {e}")

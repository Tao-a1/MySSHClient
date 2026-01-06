import re
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QLineEdit, QGroupBox, QFormLayout, QPushButton, QFileDialog, QCheckBox, QInputDialog)

class LoginTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)

        # === Import Button ===
        self.btn_import = QPushButton("📋 Paste & Import SSH Command")
        self.btn_import.setStyleSheet("background-color: #e1f5fe; color: #0277bd; font-weight: bold;")
        self.btn_import.clicked.connect(self.import_command_logic)
        layout.addWidget(self.btn_import)

        # === Server Group ===
        server_group = QGroupBox("Server")
        server_layout = QFormLayout()
        
        self.host_input = QLineEdit()
        self.host_input.setPlaceholderText("e.g. 192.168.1.1 or example.com")
        self.port_input = QLineEdit("22")
        
        server_layout.addRow("Host:", self.host_input)
        server_layout.addRow("Port:", self.port_input)
        server_group.setLayout(server_layout)
        layout.addWidget(server_group)

        # === Authentication Group ===
        auth_group = QGroupBox("Authentication")
        auth_layout = QFormLayout()
        
        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("root")
        
        # Method selection (simplified for now)
        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        # Key File Selection
        key_layout = QHBoxLayout()
        self.key_path_input = QLineEdit()
        self.key_btn = QPushButton("...")
        self.key_btn.setFixedWidth(30)
        self.key_btn.clicked.connect(self.browse_key)
        key_layout.addWidget(self.key_path_input)
        key_layout.addWidget(self.key_btn)

        auth_layout.addRow("Username:", self.user_input)
        auth_layout.addRow("Password:", self.pass_input)
        auth_layout.addRow("Private Key:", key_layout)
        
        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)

        # === Options ===
        options_group = QGroupBox("Options")
        opt_layout = QVBoxLayout()
        self.chk_store_pass = QCheckBox("Store encrypted password in profile")
        opt_layout.addWidget(self.chk_store_pass)
        options_group.setLayout(opt_layout)
        layout.addWidget(options_group)

        layout.addStretch() # Push everything up

    def browse_key(self):
        # Add filters for common SSH key formats
        filters = "SSH Keys (*.pem *.key *.ppk id_rsa*);;All Files (*)"
        fname, _ = QFileDialog.getOpenFileName(self, 'Open Private Key', '.', filters)
        if fname:
            self.key_path_input.setText(fname)

    def import_command_logic(self):
        text, ok = QInputDialog.getMultiLineText(self, "Import SSH Command", "Paste your full SSH command here:\n(e.g. ssh -i key.pem user@host -p 2222)")
        if not ok or not text:
            return
        
        cmd = text.strip()
        
        # 1. Extract Port (-p 1234 or -p1234)
        port_match = re.search(r'-p\s*(\d+)', cmd)
        if port_match:
            self.port_input.setText(port_match.group(1))
            
        # 2. Extract Key Path (-i path)
        # Handles quoted paths ("path with space") or simple paths
        key_match = re.search(r'-i\s+(?:"([^"]+)"|\'([^\']+)\'|(\S+))', cmd)
        if key_match:
            # find the non-None group and clean quotes just in case
            path = next(g for g in key_match.groups() if g is not None)
            self.key_path_input.setText(path.strip('"').strip("'"))

        # 3. Extract User@Host
        # Looks for pattern: something@something
        user_host_match = re.search(r'(?:^|\s)([a-zA-Z0-9_.-]+)@([a-zA-Z0-9_.-]+)', cmd)
        if user_host_match:
            self.user_input.setText(user_host_match.group(1))
            self.host_input.setText(user_host_match.group(2))
        else:
            # Fallback: maybe just a hostname was pasted without user@? 
            # This is risky to guess, so we only extract if strictly user@host format is found
            # or if we want to try to find the standalone host (complex without full parser)
            pass

    def get_config(self):
        return {
            'host': self.host_input.text().strip(),
            'port': int(self.port_input.text().strip() or 22),
            'user': self.user_input.text().strip(),
            'password': self.pass_input.text(),
            'key_path': self.key_path_input.text().strip()
        }

    def set_config(self, config):
        if 'host' in config: self.host_input.setText(config['host'])
        if 'port' in config: self.port_input.setText(str(config['port']))
        if 'user' in config: self.user_input.setText(config['user'])
        if 'password' in config: self.pass_input.setText(config['password'])
        if 'key_path' in config: self.key_path_input.setText(config['key_path'])

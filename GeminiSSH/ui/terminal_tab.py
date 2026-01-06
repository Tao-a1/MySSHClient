import re
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPlainTextEdit
from PyQt6.QtGui import QFont, QColor, QTextCursor
from PyQt6.QtCore import Qt

class TerminalWidget(QPlainTextEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ssh_manager = None
        
        # Style: Hacker Mode
        self.setStyleSheet("""
            QPlainTextEdit {
                background-color: #000000;
                color: #00FF00;
                border: none;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 11pt;
            }
        """)
        self.setReadOnly(True) # Prevent local typing, we only echo remote
        
        # ANSI Escape Code Cleaner (Simple version)
        self.ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|[\[0-?]*[ -/]*[@-~])')

    def set_manager(self, manager):
        self.ssh_manager = manager
        # Connect signal
        self.ssh_manager.shell_data_received.connect(self.append_data)

    def append_data(self, text):
        # 1. Strip ANSI codes (Color codes) for now to keep it clean
        # In a real app, we would parse these to set HTML colors
        clean_text = self.ansi_escape.sub('', text)
        
        # 2. Append to end
        self.moveCursor(QTextCursor.MoveOperation.End)
        self.insertPlainText(clean_text)
        
        # 3. Auto scroll
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())

    def keyPressEvent(self, event):
        if not self.ssh_manager:
            return

        key = event.text()
        
        # Handle Enter key specifically
        if event.key() == Qt.Key.Key_Return or event.key() == Qt.Key.Key_Enter:
            key = '\n'
        
        # Handle Backspace (Send \x08 or \x7f depending on server, usually \x7f works)
        if event.key() == Qt.Key.Key_Backspace:
            key = '\x7f' # ASCII DEL
            
        # Send raw key to SSH
        if key:
            self.ssh_manager.send_shell_input(key)

class TerminalTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.terminal = TerminalWidget()
        layout.addWidget(self.terminal)
        
        self.setLayout(layout)

    def bind_manager(self, manager):
        self.terminal.set_manager(manager)

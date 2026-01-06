import threading
import paramiko
import time
from PyQt6.QtCore import QObject, pyqtSignal

class SSHManager(QObject):
    # Signals
    connection_status = pyqtSignal(bool, str) # success, message
    log_message = pyqtSignal(str)
    shell_data_received = pyqtSignal(str)     # New: raw text from server

    def __init__(self):
        super().__init__()
        self.client = None
        self.shell_channel = None
        self.running = False

    def connect(self, config):
        """Starts connection in a separate thread."""
        threading.Thread(target=self._connect_thread, args=(config,), daemon=True).start()

    def _connect_thread(self, config):
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            self.log_message.emit(f"Resolving host {config['host']}...")
            
            connect_kwargs = {
                'hostname': config['host'],
                'port': config['port'],
                'username': config['user'],
                'timeout': 10
            }

            if config['key_path']:
                self.log_message.emit(f"Authenticating with key: {config['key_path']}")
                connect_kwargs['key_filename'] = config['key_path']
            elif config['password']:
                self.log_message.emit("Authenticating with password...")
                connect_kwargs['password'] = config['password']
            
            self.client.connect(**connect_kwargs)
            
            # Start Interactive Shell immediately upon connection
            self.open_shell()

            self.connection_status.emit(True, "Session established")
            self.log_message.emit("Authentication successful. Shell opened.")

        except Exception as e:
            self.log_message.emit(f"Error: {str(e)}")
            self.connection_status.emit(False, str(e))
            self.client = None

    def open_shell(self):
        """Opens an interactive shell and starts the reader thread."""
        if self.client:
            # invoke_shell requests a pseudo-terminal (pty) by default
            self.shell_channel = self.client.invoke_shell()
            self.running = True
            
            # Start background thread to listen for output
            threading.Thread(target=self._shell_read_loop, daemon=True).start()

    def _shell_read_loop(self):
        """Continuously reads bytes from the SSH channel."""
        while self.running and self.shell_channel:
            try:
                if self.shell_channel.recv_ready():
                    # Read up to 1024 bytes
                    data = self.shell_channel.recv(1024)
                    if len(data) == 0:
                        break
                    
                    # Decode bytes to string (replace errors to avoid crash)
                    text = data.decode('utf-8', errors='replace')
                    self.shell_data_received.emit(text)
                else:
                    time.sleep(0.01) # Prevent CPU spin
            except Exception as e:
                self.log_message.emit(f"Shell Read Error: {e}")
                break
        
        self.log_message.emit("Shell channel closed.")

    def send_shell_input(self, text):
        """Sends keystrokes to the server."""
        if self.shell_channel and self.shell_channel.active:
            self.shell_channel.send(text)

    def disconnect(self):
        self.running = False
        if self.client:
            self.client.close()
            self.client = None
            self.shell_channel = None
            self.connection_status.emit(False, "User disconnected")
            self.log_message.emit("Session closed.")

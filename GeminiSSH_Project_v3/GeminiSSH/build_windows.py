import os
import subprocess
import sys

def build():
    print("Building GeminiSSH for Windows...")
    
    # Check if pyinstaller is installed
    try:
        subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.DEVNULL)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Error: PyInstaller not found. Please run: pip install pyinstaller")
        return

    # Build command
    # --noconsole: Hide the black command window (GUI mode)
    # --onefile: Bundle everything into a single .exe
    # --name: Output filename
    # --hidden-import: Ensure dynamic imports (like PyQt plugins) are found
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        "--name=GeminiSSH",
        "--clean",
        "main.py"  # Entry point
    ]
    
    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd)
    
    print("\nBuild complete!")
    print(f"Executable is located in: {os.path.join(os.getcwd(), 'dist', 'GeminiSSH.exe')}")

if __name__ == "__main__":
    if sys.platform != "win32":
        print("Warning: You are running this build script on a non-Windows platform.")
        print("The resulting executable will be for THIS platform (Linux/Mac), not Windows.")
    
    build()

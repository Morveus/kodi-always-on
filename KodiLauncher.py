import os
import subprocess
import tkinter as tk
import tkinter.filedialog
import psutil
import time
import win32gui
import win32con
import win32api

class KodiLauncher:

    def __init__(self):
        self.kodi_path = ""
        self.root = tk.Tk()
        self.root.title("Kodi Launcher")
        self.root.geometry("300x100")
        self.load_settings()
        self.create_widgets()
        self.root.mainloop()

    def create_widgets(self):
        # Create a label and button to set Kodi path
        self.path_label = tk.Label(self.root, text="Kodi Path:")
        self.path_label.pack(pady=10)
        self.path_var = tk.StringVar()
        self.path_var.set(self.kodi_path)
        self.path_entry = tk.Entry(self.root, textvariable=self.path_var)
        self.path_entry.pack()
        self.browse_button = tk.Button(self.root, text="Browse...", command=self.set_kodi_path)
        self.browse_button.pack(pady=10)

        # Create a label to display Kodi status
        self.status_label = tk.Label(self.root, text="")
        self.status_label.pack(pady=10)

        # Check if Kodi is running every second
        self.check_kodi()
    
    def save_kodi_path(self):
        # Save Kodi's path to a text file
        with open("settings.ini", "w") as f:
            f.write(self.kodi_path)

    def load_settings(self):
        try:
            with open('settings.ini', 'r') as f:
                self.kodi_path = f.readline().strip()
        except FileNotFoundError:
            pass

    def set_kodi_path(self):
        # Open a file dialog to choose Kodi path
        try:
            import tkFileDialog
        except ImportError:
            tkFileDialog = tkinter.filedialog
        path = tkFileDialog.askopenfilename(filetypes=[("Executable Files", "*.exe")])
        if path:
            self.kodi_path = path
            self.path_var.set(self.kodi_path)

            # Check if Kodi is already running and maximize its window
            if self.is_kodi_running():
                self.maximize_kodi()
            else:
                self.status_label.config(text="Kodi path set. Please start Kodi manually or wait for the next check.")
                
            # Save Kodi's path to a text file
            self.save_kodi_path()


    def check_kodi(self):
        # Check if Kodi path is set
        if self.kodi_path:
            # Check if Kodi is running
            running = self.is_kodi_running()

            if not running:
                # If Kodi is not running, start it
                self.status_label.config(text="Starting Kodi...")
                subprocess.Popen('"' + self.kodi_path + '"', shell=True)
            else:
                # If Kodi is running, check if it's minimized
                minimized = self.is_kodi_minimized()

                if minimized:
                    # If Kodi is minimized, maximize it
                    self.status_label.config(text="Maximizing Kodi...")
                    self.maximize_kodi()
                else:
                    # If Kodi is not minimized, do nothing
                    self.status_label.config(text="Kodi is running.")

        # Check again in one second
        self.root.after(1000, self.check_kodi)

    def is_kodi_running(self):
        # Check if Kodi is running by searching for the process
        for proc in psutil.process_iter():
            if "kodi.exe" in proc.name().lower():
                return True
        return False

    def is_kodi_minimized(self):
        # Get the window dimensions
        handle = self.get_kodi_handle()
        if not handle:
            return False
        left, top, right, bottom = win32gui.GetWindowRect(handle)
        w = right - left
        h = bottom - top

        # Check if the window is minimized
        placement = win32gui.GetWindowPlacement(handle)
        return w == 0 and h == 0 or placement[1] == win32con.SW_SHOWMINIMIZED

    def get_kodi_handle(self):
        # Find Kodi's window handle by enumerating all windows
        def callback(handle, handles):
            if win32gui.GetWindowText(handle) == "Kodi":
                handles.append(handle)
            return True
        handles = []
        win32gui.EnumWindows(callback, handles)
        return handles[0] if handles else None

    def maximize_kodi(self):
        # Get the Kodi window handle
        handle = self.get_kodi_handle()
        if not handle:
            return

        # Set the Kodi window to foreground
        win32gui.SetForegroundWindow(handle)

        # Send Alt-Enter keystrokes to toggle fullscreen mode
        win32api.keybd_event(win32con.VK_MENU, 0, 0, 0)
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_MENU, 0, win32con.KEYEVENTF_KEYUP, 0)

        # Send Win-UpArrow keystrokes to maximize the window
        win32api.keybd_event(win32con.VK_LWIN, 0, 0, 0)
        win32api.keybd_event(win32con.VK_UP, 0, 0, 0)
        win32api.keybd_event(win32con.VK_UP, 0, win32con.KEYEVENTF_KEYUP, 0)
        win32api.keybd_event(win32con.VK_LWIN, 0, win32con.KEYEVENTF_KEYUP, 0)

if __name__ == "__main__":
    KodiLauncher()

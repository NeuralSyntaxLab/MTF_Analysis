# Main GUI application for capturing and scoring images from a Miniscope setup.
# It allows the user to:
# - Select LPS (Lines Per mm) values.
# - Capture and score images interactively.
# - Control an LED via serial port.
# - Save and visualize the results.

import cv2
import os
import pandas as pd
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import serial as ser
from serial.tools import list_ports
from score_photo import score_image, score_image_interactive  # Custom image scoring functions
import sys
import os

IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff')

class MiniscopeApp:
    """Main application class for the MTF GUI analysis tool."""
    
    def __init__(self, miniscope):
        """Initialize the application and open the home window."""
        self.video_capture = None
        self.current_image = None
        self.LPS = None
        self.current_lp_index = 0
        self.current_lps = None
        self.scores = []
        self.home_window(miniscope)

    def home_window(self, miniscope):
        """Creates the home window with a start and quit option."""
        self.home_window = miniscope
        self.home_window.title("MTF app")
        main_frame = tk.Frame(self.home_window, padx=20, pady=20)
        
        # Display an image/logo
        
        img = Image.open(get_resource_path("app_images/ponny_canary.jpg")).resize((200, 200))
        self.photo = ImageTk.PhotoImage(img)
        img_label = tk.Label(main_frame, image=self.photo)
        img_label.grid(row=1, column=0, columnspan=2, pady=10)

        # Title
        title_label = tk.Label(main_frame, text="MTF Analysis", font=("Helvetica", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))

        # Start Button
        self.start_button = tk.Button(
            main_frame, text="✅ Start", command=self.ask_for_lps,
            bg="green", fg="white", font=("Helvetica", 12, "bold"), width=15
        )
        self.start_button.grid(row=2, column=0, pady=10, padx=10, sticky='e')

        # Quit Button
        self.quit_button = tk.Button(
            main_frame, text="❌ Quit", command=self.home_window.destroy,
            bg="red", fg="white", font=("Helvetica", 12, "bold"), width=15
        )
        self.quit_button.grid(row=2, column=1, pady=10, padx=10, sticky='w')

        main_frame.pack()

    def ask_for_lps(self):
        """Displays a popup for the user to select LPS values for analysis."""
        lps_window = tk.Toplevel(self.home_window)
        lps_window.title("Select LPS values")

        tk.Label(lps_window, text="Choose LPS values to analyse:").grid(row=0, column=0, columnspan=9, pady=5)

        options = [23, 26, 29, 32, 40, 45, 51, 57, 64, 72, 80, 90, 101, 114, 128, 143, 161, 180]
        self.lp_vars = {}
        cols = (len(options) + 1) // 2

        # Create checkboxes
        for idx, lp in enumerate(options):
            var = tk.BooleanVar()
            self.lp_vars[lp] = var
            row = 1 if idx < cols else 2
            col = idx if idx < cols else idx - cols
            chk = tk.Checkbutton(lps_window, text=str(lp), variable=var)
            chk.grid(row=row, column=col, sticky='w', padx=5, pady=2)

        # Confirm button
        confirm_button = tk.Button(
            lps_window, text="Confirm", command=lambda: self.set_lps_and_start(lps_window)
        )
        confirm_button.grid(row=3, column=0, columnspan=cols, pady=10)

    def set_lps_and_start(self, lps_window):
        """Gets selected LPS and initializes the camera and controls."""
        self.LPS = [lps for lps, var in self.lp_vars.items() if var.get()]
        if not self.LPS:
            tk.messagebox.showwarning("No Selection", "You must select at least one LPS.")
            return

        lps_window.destroy()
        self.home_window.destroy()

        # New window
        self.camera_window = tk.Tk()
        self.camera_window.title("Miniscope's Camera")
        self.camera_window.geometry("800x800")

        # Canvas for video feed
        self.canvas = tk.Canvas(self.camera_window, width=640, height=480)
        self.canvas.place(relx=0.5, rely=0.05, anchor='n')

        # Instruction Label (animated text)
        self.instruction_label = tk.Label(self.camera_window, text="", fg="white", bg="red",
                                          font=("Helvetica", 20, "bold"), padx=10, pady=5,
                                          relief="solid", borderwidth=2)
        self.instruction_label.place(relx=0.5, rely=0.5, anchor='center')

        # Camera icon & Capture bu_tton
        icon_img = Image.open(get_resource_path("app_images/camera_icon.jpg")).resize((24, 24))
        self.camera_icon = ImageTk.PhotoImage(icon_img)

        self.capture_button = tk.Button(
            self.camera_window, text=" Capture Image", image=self.camera_icon,
            compound="left", command=self.capture_and_confirm, bg="green", fg="white",
            font=("Helvetica", 14, "bold"), padx=10, pady=6, relief="raised", borderwidth=3
        )
        self.capture_button.place(relx=0.5, rely=0.9, anchor='center')

        # COM Port Selection
        tk.Label(self.camera_window, text="COM Port:").place(relx=0.5, rely=0.67)
        ports = list_ports.comports()
        self.com_options = [p.device for p in ports]
        self.selected_com = tk.StringVar(value=self.com_options[0] if self.com_options else "No COM ports")
        com_menu = ttk.Combobox(self.camera_window, textvariable=self.selected_com,
                                values=self.com_options, state="readonly", width=15)
        com_menu.place(relx=0.5, rely=0.8, anchor='center')

        # Connect Button
        connect_button = tk.Button(self.camera_window, text="Connect LED",
                                   command=self.connect_serial_port, bg="blue", fg="white")
        connect_button.place(relx=0.7, rely=0.8, anchor='center')

        # LED Power Scale
        tk.Label(self.camera_window, text="LED Power").place(relx=0.1, rely=0.8, anchor='center')
        self.led_power_var = tk.DoubleVar()
        led_scale = tk.Scale(self.camera_window, from_=0, to=255, orient=tk.HORIZONTAL,
                             variable=self.led_power_var, command=self.set_LED, length=200)
        led_scale.place(relx=0.1, rely=0.7)

        # Start video feed
        self.video_capture = cv2.VideoCapture(0)
        self.current_lp_index = 0
        self.update_webcam()
        self.next_lps()

        self.camera_window.protocol("WM_DELETE_WINDOW", self.close_camera_window)
        self.camera_window.mainloop()

    def next_lps(self):
        """Display instructions for the next LPS value."""
        self.current_lps = self.LPS[self.current_lp_index]
        self.instruction_label.config(
            text=f"Please Take a Picture for {self.current_lps} LPS ({self.current_lp_index+1}/ {len(self.LPS)})"
        )

        def move_label_up():
            self.instruction_label.config(font=("Helvetica", 12, "normal"))
            self.instruction_label.place(relx=0.5, rely=0.01, anchor='n')

        self.instruction_label.after(2000, move_label_up)

    def update_webcam(self):
        """Grabs the latest webcam frame and updates the canvas display."""
        ret, frame = self.video_capture.read()
        if ret:
            self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.camera_window.after(15, self.update_webcam)

    def capture_and_confirm(self):
        """Capture current image and show confirmation popup."""
        if self.current_image is None:
            tk.messagebox.showerror("Error", "No image to capture.")
            return

        frozen_image = self.current_image.copy()
        lp = self.LPS[self.current_lp_index]
        popup = tk.Toplevel(self.camera_window)
        popup.title(f"Captured Image - LPS {lp}")

        img = ImageTk.PhotoImage(frozen_image)
        label = tk.Label(popup, image=img)
        label.image = img
        label.pack()

        def confirm():
            popup.destroy()
            self.save_and_score(lp, frozen_image)

        def retake():
            popup.destroy()
            tk.messagebox.showinfo("Retake", "Please retake the image.")

        button_frame = tk.Frame(popup)
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Continue", command=confirm).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Retake", command=retake).pack(side=tk.LEFT, padx=5)

    def save_and_score(self, lps, image):
        """Save captured image and run scoring."""
        save_dir = "captured_images"
        os.makedirs(save_dir, exist_ok=True)
        filepath = os.path.join(save_dir, f"{lps}_image.png")
        image.save(filepath)

        result = score_image_interactive(filepath)
        if result == "retake":
            return
        elif result == "skip":
            self.LPS.pop(self.current_lp_index)
            if self.current_lp_index < len(self.LPS):
                self.start_capture_sequence()
            else:
                tk.messagebox.showinfo("Done", "All LPS processed.")
                extract_results(self.LPS, self.scores)
                self.close_camera_window()
            return

        tk.messagebox.showinfo("Image Score", f"Score: {result:.2f}")
        self.scores.append(result)
        self.current_lp_index += 1

        if self.current_lp_index < len(self.LPS):
            self.next_lps()
        else:
            tk.messagebox.showinfo("Done", "All LPS processed.")
            extract_results(self.LPS, self.scores)
            self.close_camera_window()

    def start_capture_sequence(self):
        """Continue capture sequence after skipping."""
        self.next_lps()

    def close_camera_window(self):
        """Release camera and close GUI."""
        if self.video_capture and self.video_capture.isOpened():
            self.video_capture.release()
        if hasattr(self, 'camera_window'):
            self.camera_window.destroy()

    def connect_serial_port(self):
        """Open serial port to control LED."""
        port = self.selected_com.get()
        try:
            self.serial_port = ser.Serial(port, baudrate=115200)
            self.serial_port.close()
            self.serial_port.open()
            tk.messagebox.showinfo("Connected", f"Connected to {port}")
        except Exception as e:
            tk.messagebox.showerror("Error", f"Failed to connect to {port}\n{e}")

    def set_LED(self, level):
        """Send LED brightness level via serial."""
        if hasattr(self, 'serial_port') and self.serial_port:
            s = ('4n' + chr(int(float(level)))).encode('latin-1')
            self.serial_port.write(s)

def get_resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS  # PyInstaller runtime folder
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def extract_results(lps_list_sorted, score_list_sorted):
    """Save results to CSV and display a plot."""
    root = tk.Tk()
    root.withdraw()
    save_path = filedialog.asksaveasfilename(
        title="Save Results As",
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        initialfile="miniscope_results.csv"
    )
    root.destroy()
    if not save_path:
        tk.messagebox.showwarning("Cancelled", "No file selected. Results were not saved.")
        return

    result_table = pd.DataFrame({'LPS': lps_list_sorted, 'Score': score_list_sorted})
    result_table.to_csv(save_path, index=False)
    plot_score(lps_list_sorted, score_list_sorted)

def plot_score(lps_list_sorted, score_list_sorted):
    """Plot score vs LPS graph."""
    plt.figure(figsize=(8, 5))
    plt.plot(lps_list_sorted, score_list_sorted, color='blue', marker='o')
    plt.axhline(y=0, color='gray', linestyle='--', linewidth=1)
    plt.xticks(lps_list_sorted)
    plt.xlabel("Lines per mm (LPS)")
    plt.ylabel("Mean Contrast for Minima-Maxima Pair")
    plt.title("Image Score vs LPS")
    plt.grid(True)
    plt.show()

def interactive_main():
    """Entry point for interactive mode."""
    SAVE_DIR = "captured_images"
    os.makedirs(SAVE_DIR, exist_ok=True)
    root = tk.Tk()
    app = MiniscopeApp(root)
    root.mainloop()

if __name__ == '__main__':
    interactive_main()

import tkinter as tk
from tkinter import filedialog

# Function to open the file explorer for directory selection
def get_directory():
    # Create a Tkinter window to open the file dialog
    root = tk.Tk()
    root.withdraw()  # Hide the root window

    # Open the directory selection dialog
    folder_selected = filedialog.askdirectory(title="Select Directory to Save")
    
    # Print the directory path to stdout (Streamlit will capture this)
    print(folder_selected)

if __name__ == "__main__":
    get_directory()

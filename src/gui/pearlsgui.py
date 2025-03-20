import sys
import os
import tkinter as tk
from tkinter import ttk

from tkinter import filedialog


sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from src.classes.diamond_perls_converter import GenerateDiamondperls
from config.paper_size import FORMATE_MM

class DiamondPerlsApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Diamond Perls Generator")
        self.geometry("600x600")

        # Input file selection
        self.file_label = ttk.Label(self, text="Input File:")
        self.file_label.pack(pady=5)
        self.file_entry = ttk.Entry(self, width=80)
        self.file_entry.pack(pady=5)
        self.browse_button = ttk.Button(self, text="Browse", command=self.browse_file)
        self.browse_button.pack(pady=5)

        # Color depth slider
        self.color_depth_label = ttk.Label(self, text="Color Depth:")
        self.color_depth_label.pack(pady=5)
        self.color_depth_slider = ttk.Scale(self, from_=1, to=200, orient="horizontal")
        self.color_depth_slider.pack(pady=5)

        # Display current value of Color Depth slider
        self.color_depth_value = ttk.Label(
            self, text=f"{int(self.color_depth_slider.get())}"
        )
        self.color_depth_value.pack(pady=5)
        self.color_depth_slider.configure(
            command=lambda value: self.color_depth_value.config(
                text=f"{int(float(value))}"
            )
        )

        # DPI adjustment slider
        self.dpi_label = ttk.Label(self, text="DPI:")
        self.dpi_label.pack(pady=5)
        self.dpi_slider = ttk.Scale(self, from_=72, to=600, orient="horizontal")
        self.dpi_slider.pack(pady=5)

        # Display current value of DPI slider
        self.dpi_value = ttk.Label(self, text=f"{int(self.dpi_slider.get())}")
        self.dpi_value.pack(pady=5)
        self.dpi_slider.configure(
            command=lambda value: self.dpi_value.config(text=f"{int(float(value))}")
        )

        
        # Load paper sizes from configuration file
        self.paper_size_label = ttk.Label(self, text="Paper Size:")
        self.paper_size_label.pack(pady=5)
        self.paper_size_var = tk.StringVar(value=list(FORMATE_MM.keys())[0])
        self.paper_size_dropdown = ttk.OptionMenu(self, 
                                                  self.paper_size_var, *FORMATE_MM.keys()
        )
        self.paper_size_dropdown.pack(pady=5)
        
        # Set Pearlsize
        self.pearl_size_label = ttk.Label(self, text="Pearl Size (mm):")
        self.pearl_size_label.pack(pady=5)
        self.pearl_size_var = tk.DoubleVar(value=2.5)
        self.pearl_size_entry = ttk.Entry(self, textvariable=self.pearl_size_var, width=10)
        self.pearl_size_entry.pack(pady=5)
        
        # Set average Color
        self.average_color_label = ttk.Label(self, text="Calculate Average Color:")
        self.average_color_label.pack(pady=5)
        self.average_color_var = tk.BooleanVar(value=False)
        self.average_color_checkbox = ttk.Checkbutton(
            self, text="Enable", variable=self.average_color_var
        )
        self.average_color_checkbox.pack(pady=5)
        
        # Generate button
        self.generate_button = ttk.Button(
            self, text="Generate", command=self.generate_diamond_perls
        )
        self.generate_button.pack(pady=20)
        
        # Exit button
        self.exit_button = ttk.Button(
            self, text="Exit", command=sys.exit
        )
        self.exit_button.pack(pady=10)
        
    def browse_file(self):
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def generate_diamond_perls(self):
        input_file = self.file_entry.get()
        color_depth = int(self.color_depth_slider.get())
        dpi = int(self.dpi_slider.get())

        if not input_file:
            tk.messagebox.showerror("Error", "Please select an input file.")
            return

        generator = GenerateDiamondperls(input_file_name=input_file, 
                                         farben_anzahl=color_depth, 
                                         dpi=dpi, 
                                         format=self.paper_size_var.get(),
                                         perlen_groesse=self.pearl_size_var.get(),
                                         durchschnitt_farbe_berechnen=self.average_color_var.get())
        try:
            generator.generate()
            tk.messagebox.showinfo("Success", "Diamond Perls generated successfully!")
        except Exception as e:
            tk.messagebox.showerror("Error", f"An error occurred: {e}")

    
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
        self.columnconfigure(0, weight=1)  # Damit Widgets sich anpassen

        # --- Datei auswählen ---
        file_frame = ttk.Frame(self)
        file_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Input File:").grid(row=0, column=0, padx=5, sticky="w")
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)

        # --- Color Depth ---
        self.color_depth_var = tk.IntVar(value=100)
        self.create_slider("Color Depth:", 1, 200, self.color_depth_var, 1)

        # --- DPI ---
        self.dpi_var = tk.IntVar(value=300)
        self.create_slider("DPI:", 72, 600, self.dpi_var, 2)

        # --- Paper Size ---
        ttk.Label(self, text="Paper Size:").grid(row=3, column=0, pady=5)
        self.paper_size_var = tk.StringVar(value=list(FORMATE_MM.keys())[0])
        self.paper_size_dropdown = ttk.OptionMenu(self, self.paper_size_var, *FORMATE_MM.keys())
        self.paper_size_dropdown.grid(row=4, column=0, pady=5)

        # --- Pearl Size ---
        ttk.Label(self, text="Pearl Size (mm):").grid(row=5, column=0, pady=5)
        self.pearl_size_var = tk.DoubleVar(value=2.5)
        self.pearl_size_entry = ttk.Entry(self, textvariable=self.pearl_size_var, width=10)
        self.pearl_size_entry.grid(row=6, column=0, pady=5)

        # --- Durchschnittsfarbe berechnen ---
        self.average_color_var = tk.BooleanVar(value=False)
        self.average_color_checkbox = ttk.Checkbutton(
            self, text="Calculate Average Color", variable=self.average_color_var
        )
        self.average_color_checkbox.grid(row=7, column=0, pady=5)

        # --- Buttons ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=8, column=0, pady=20, padx=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(button_frame, text="Generate", command=self.generate_diamond_perls).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(button_frame, text="Exit", command=sys.exit).grid(row=0, column=1, sticky="ew", padx=5)

    def create_slider(self, label, min_value, max_value, variable, row):
        """Hilfsfunktion zum Erstellen von Slidern mit Label"""
        frame = ttk.Frame(self)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        ttk.Label(frame, text=label).pack(anchor="w")
        slider = ttk.Scale(frame, from_=min_value, to=max_value, orient="horizontal", variable=variable)
        slider.pack(fill="x")

        value_label = ttk.Label(frame, text=f"{int(variable.get())}")
        value_label.pack()

        # Aktualisiert das Label, wenn sich der Wert ändert
        variable.trace_add("write", lambda *args: value_label.config(text=str(int(variable.get()))))

        return slider  # Falls du den Slider später direkt brauchst
    
    def browse_file(self):
        """Öffnet einen Datei-Dialog zur Auswahl einer Datei"""
        file_path = filedialog.askopenfilename()
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)
        
    def generate_diamond_perls(self):
        input_file = self.file_entry.get()
        color_depth = int(self.color_depth_var.get())
        dpi = int(self.dpi_var.get())

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

    
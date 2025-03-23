import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

# Ensure the module can be found
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

try:
    from src.classes.diamond_pearls_converter import GenerateDiamondperls
    from config.paper_size import FORMATE_MM
    from config.const import GUI, DPI, PERLEN_GROESSE, FORMAT, FARBBEREICH
except ModuleNotFoundError as e:
    messagebox.showerror("Module Import Error", f"Required modules could not be found: {e}")
    sys.exit(1)

class DiamondPerlsApp(tk.Tk):
    """
    A GUI application for generating diamond pearls using user-defined settings.
    """

    def __init__(self) -> None:
        """Initialize the GUI application."""
        super().__init__()
        self.setup_gui()

    def setup_gui(self) -> None:
        """Setup the main GUI layout and widgets."""
        self.title(GUI.TITLE)
        self.geometry(GUI.GEOMETRY)
        self.columnconfigure(0, weight=1)

        self.create_file_selection()
        self.create_sliders()
        self.create_dropdowns()
        self.create_checkboxes()
        self.create_buttons()

    def create_file_selection(self) -> None:
        """Create file selection widgets."""
        frame = ttk.Frame(self)
        frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        frame.columnconfigure(1, weight=1)

        ttk.Label(frame, text="Input File:").grid(row=0, column=0, padx=5, sticky="w")
        self.file_entry = ttk.Entry(frame)
        self.file_entry.grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(frame, text="Browse", command=self.browse_file).grid(row=0, column=2, padx=5)

    def create_sliders(self) -> None:
        """Create sliders for adjustable settings."""
        self.color_depth_var: tk.IntVar = tk.IntVar(value=FARBBEREICH)
        self.dpi_var: tk.IntVar = tk.IntVar(value=DPI)
        
        self.create_slider("Color Depth:", 1, 200, self.color_depth_var, 1)
        self.create_slider("DPI:", 72, 600, self.dpi_var, 2)

    def create_dropdowns(self) -> None:
        """Create dropdowns for selecting options."""
        ttk.Label(self, text="Paper Size:").grid(row=3, column=0, pady=5)
        self.paper_size_var: tk.StringVar = tk.StringVar(value=list(FORMATE_MM.keys())[0])
        self.paper_size_dropdown = ttk.Combobox(self, textvariable=self.paper_size_var, values=list(FORMATE_MM.keys()), state="readonly")
        self.paper_size_dropdown.grid(row=4, column=0, pady=5)

        ttk.Label(self, text="Pearl Size (mm):").grid(row=5, column=0, pady=5)
        self.pearl_size_var: tk.DoubleVar = tk.DoubleVar(value=PERLEN_GROESSE)
        self.pearl_size_entry = ttk.Entry(self, textvariable=self.pearl_size_var, width=10)
        self.pearl_size_entry.grid(row=6, column=0, pady=5)

    def create_checkboxes(self) -> None:
        """Create checkboxes for additional options."""
        self.average_color_var: tk.BooleanVar = tk.BooleanVar(value=False)
        self.average_color_checkbox = ttk.Checkbutton(self, text="Calculate Average Color", variable=self.average_color_var)
        self.average_color_checkbox.grid(row=7, column=0, pady=5)

    def create_buttons(self) -> None:
        """Create buttons for user actions."""
        frame = ttk.Frame(self)
        frame.grid(row=8, column=0, pady=20, padx=10, sticky="ew")
        frame.columnconfigure(0, weight=1)

        ttk.Button(frame, text="Generate", command=self.generate_diamond_perls).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(frame, text="Exit", command=self.destroy).grid(row=0, column=1, sticky="ew", padx=5)

    def create_slider(self, label: str, min_value: int, max_value: int, variable: tk.IntVar, row: int) -> None:
        """
        Helper function to create a labeled slider.

        Args:
            label (str): Label text for the slider.
            min_value (int): Minimum slider value.
            max_value (int): Maximum slider value.
            variable (tk.IntVar): Variable to bind to the slider.
            row (int): Grid row placement.
        """
        frame = ttk.Frame(self)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")
        
        ttk.Label(frame, text=label).pack(anchor="w")
        slider = ttk.Scale(frame, from_=min_value, to=max_value, orient="horizontal", variable=variable)
        slider.pack(fill="x")
        
        value_label = ttk.Label(frame, text=f"{int(variable.get())}")
        value_label.pack()
        variable.trace_add("write", lambda *args: value_label.config(text=str(int(variable.get()))))

    def browse_file(self) -> None:
        """Open a file dialog to select an input file."""
        file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"), ("All Files", "*.*")])
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def generate_diamond_perls(self) -> None:
        """Generate diamond pearls based on user-defined settings."""
        input_file: str = self.file_entry.get()
        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        try:
            generator = GenerateDiamondperls(
                input_file_name=input_file,
                color_variation_count=self.color_depth_var.get(),
                output_dpi=self.dpi_var.get(),
                output_format=self.paper_size_var.get(),
                pearl_dimension=self.pearl_size_var.get(),
                is_average_color_enabled=self.average_color_var.get(),
            )
            generator.generate()
            messagebox.showinfo("Success", "Diamond Perls generated successfully!")
        except (FileNotFoundError, PermissionError) as e:
            messagebox.showerror("Error", str(e))
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

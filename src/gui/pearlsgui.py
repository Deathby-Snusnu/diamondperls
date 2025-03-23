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
    print(f"Module Import Error: {e}")
    messagebox.showerror("Error", "Required modules could not be found.")
    sys.exit(1)


class DiamondPerlsApp(tk.Tk):
    """
    A GUI application for generating diamond pearls using user-defined settings.
    """

    def __init__(self) -> None:
        """
        Initialize the DiamondPerlsApp GUI.
        """
        super().__init__()
        self.title(GUI.TITLE)
        self.geometry(GUI.GEOMETRY)
        self.columnconfigure(0, weight=1)  # Ensure widgets resize properly

        # --- File Selection ---
        file_frame = ttk.Frame(self)
        file_frame.grid(row=0, column=0, pady=10, padx=10, sticky="ew")
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="Input File:").grid(
            row=0, column=0, padx=5, sticky="w"
        )
        self.file_entry = ttk.Entry(file_frame)
        self.file_entry.grid(row=0, column=1, padx=5, sticky="ew")
        ttk.Button(file_frame, text="Browse", command=self.browse_file).grid(
            row=0, column=2, padx=5
        )

        # --- Color Depth ---
        self.color_depth_var = tk.IntVar(value=FARBBEREICH)
        self.create_slider("Color Depth:", 1, 200, self.color_depth_var, 1)

        # --- DPI ---
        self.dpi_var = tk.IntVar(value=DPI)
        self.create_slider("DPI:", 72, 600, self.dpi_var, 2)

        # --- Paper Size ---
        ttk.Label(self, text="Paper Size:").grid(row=3, column=0, pady=5)
        self.paper_size_var = tk.StringVar(value=list(FORMATE_MM.keys())[0])
        self.paper_size_dropdown = ttk.Combobox(
            self,
            textvariable=self.paper_size_var,
            values=list(FORMATE_MM.keys()),
            state="readonly",
        )
        self.paper_size_dropdown.grid(row=4, column=0, pady=5)

        # --- Pearl Size ---
        ttk.Label(self, text="Pearl Size (mm):").grid(row=5, column=0, pady=5)
        self.pearl_size_var = tk.DoubleVar(value=PERLEN_GROESSE)
        self.pearl_size_entry = ttk.Entry(
            self, textvariable=self.pearl_size_var, width=10
        )
        self.pearl_size_entry.grid(row=6, column=0, pady=5)

        # --- Average Color Calculation ---
        self.average_color_var = tk.BooleanVar(value=False)
        self.average_color_checkbox = ttk.Checkbutton(
            self, text="Calculate Average Color", variable=self.average_color_var
        )
        self.average_color_checkbox.grid(row=7, column=0, pady=5)

        # --- Buttons ---
        button_frame = ttk.Frame(self)
        button_frame.grid(row=8, column=0, pady=20, padx=10, sticky="ew")
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(
            button_frame, text="Generate", command=self.generate_diamond_perls
        ).grid(row=0, column=0, sticky="ew", padx=5)
        ttk.Button(button_frame, text="Exit", command=self.destroy).grid(
            row=0, column=1, sticky="ew", padx=5
        )

    def create_slider(
        self, label: str, min_value: int, max_value: int, variable: tk.IntVar, row: int
    ) -> ttk.Scale:
        """
        Helper function to create a labeled slider.

        Args:
            label (str): The label text for the slider.
            min_value (int): The minimum value of the slider.
            max_value (int): The maximum value of the slider.
            variable (tk.IntVar): The variable to bind to the slider.
            row (int): The row in the grid where the slider will be placed.

        Returns:
            ttk.Scale: The created slider widget.
        """
        frame = ttk.Frame(self)
        frame.grid(row=row, column=0, pady=5, padx=10, sticky="ew")

        ttk.Label(frame, text=label).pack(anchor="w")
        slider = ttk.Scale(
            frame, from_=min_value, to=max_value, orient="horizontal", variable=variable
        )
        slider.pack(fill="x")

        value_label = ttk.Label(frame, text=f"{int(variable.get())}")
        value_label.pack()

        # Update the label when the slider value changes
        variable.trace_add(
            "write", lambda *args: value_label.config(text=str(int(variable.get())))
        )

        return slider

    def browse_file(self) -> None:
        """
        Open a file dialog to select an input file.
        """
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif"),
                ("All Files", "*.*"),
            ]
        )
        if file_path:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, file_path)

    def generate_diamond_perls(self) -> None:
        """
        Generate diamond pearls based on the user-defined settings.
        """
        input_file: str = self.file_entry.get()
        color_depth: int = int(self.color_depth_var.get())
        dpi: int = int(self.dpi_var.get())
        druck_format: str = self.paper_size_var.get()
        perlen_groesse: float = self.pearl_size_var.get()
        durchschnitt_farbe_berechnen: bool = self.average_color_var.get()

        if not input_file:
            messagebox.showerror("Error", "Please select an input file.")
            return

        generator = GenerateDiamondperls(
            input_file_name=input_file,
            farben_anzahl=color_depth,
            dpi=dpi,
            format=druck_format,
            perlen_groesse=perlen_groesse,
            durchschnitt_farbe_berechnen=durchschnitt_farbe_berechnen,
        )
        
        try:
            generator.generate()
            messagebox.showinfo("Success", "Diamond Perls generated successfully!")

        except FileNotFoundError:
            messagebox.showerror("Error", "The selected file was not found.")
        except PermissionError:
            messagebox.showerror(
                "Error", "Permission denied. Check file access rights."
            )
        except Exception as e:
            messagebox.showerror("Error", f"An unexpected error occurred: {e}")

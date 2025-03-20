import csv
import sys
import os

from PIL import Image, ImageDraw, ImageStat

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.paper_size import FORMATE_MM
from config.pathnames import RAL_FILE_NAME #DATA_PATH
from config.const import DPI, PERLEN_GROESSE, FARBBEREICH, FORMAT


class GenerateDiamondperls:
    """
    GenerateDiamondperls is a class designed to create a diamond pearl pattern from an input image.
    It processes the image, reduces its color palette, and maps the colors to the closest RAL colors.
    The result is a stylized image with a pearl-like appearance.
    Attributes:
        _durchschnitt_farbe_berechnen (bool): Determines whether to calculate the average color for each block.
        _input_file_name (str): Path to the input image file.
        _perlen_groesse (float): Size of the pearls in millimeters.
        _farben_anzahl (int): Number of colors to reduce the image to.
        _format (str): Format of the output image (e.g., A4, A3).
        _dpi (int): Dots per inch for the output image.
        _formate_mm (dict): Dictionary containing dimensions of formats in millimeters.
        _breite_px (int): Width of the image in pixels after scaling.
        _höhe_px (int): Height of the image in pixels after scaling.
        _RAL_farben (dict): Dictionary of RAL colors loaded from a CSV file.
        _bild (PIL.Image.Image): The processed image.
        _breite (int): Width of the processed image.
        _länge (int): Height of the processed image.
        verwendete_farben (set): Set of RAL colors used in the final image.
    Methods:
        __init__(input_file_name, perlen_groesse, farben_anzahl, format, dpi, durchschnitt_farbe_berechnen):
            Initializes the class with the given parameters and loads necessary resources.
        _berechne_durchschnittsfarbe(teilbild):
            Calculates the average color of a given image block.
        _lade_RAL_farben():
            Loads RAL colors from a CSV file.
        _finde_nächste_ral_farbe(rgb):
            Finds the closest RAL color to a given RGB value using Euclidean distance.
        _lade_bild():
            Loads the input image, scales it proportionally, and reduces its color palette.
        _zeichne_perlen():
            Draws pearl-like ellipses on the image based on the processed color data.
        _save_image():
            Saves the final image with the pearl pattern applied.
        _show_image():
            Displays the current state of the image.
        generate():
            Generates the diamond pearl pattern, displays the result, and saves the image.
    """

    def __init__(
        self,
        input_file_name,
        perlen_groesse=PERLEN_GROESSE,
        farben_anzahl=FARBBEREICH,
        format=FORMAT,
        dpi=DPI,
        durchschnitt_farbe_berechnen=True,
    ):
        self._durchschnitt_farbe_berechnen: bool = durchschnitt_farbe_berechnen
        self._input_file_name: str = f'{input_file_name}'
        self._perlen_groesse: int = perlen_groesse
        self._farben_anzahl: int = farben_anzahl
        self._format: str = format
        self._dpi: int = dpi
        self._formate_mm: dict = FORMATE_MM
        self._breite_px: int = self._formate_mm[self._format][0] * self._dpi // 25.4
        self._höhe_px: int = self._formate_mm[self._format][1] * self._dpi // 25.4
        self._lade_RAL_farben()
        self._lade_bild()

    def _berechne_durchschnittsfarbe(self, teilbild):
        """
        Calculates the average color of a given image section (block).

        Args:
            teilbild (PIL.Image.Image): The image section for which the average color is to be calculated.

        Returns:
            tuple: A tuple of three integers representing the average RGB color values of the image section.
        """
        """Berechnet die Durchschnittsfarbe eines Bildbereichs (Block)."""
        stat = ImageStat.Stat(teilbild)
        return tuple(int(c) for c in stat.mean[:3])

    def _lade_RAL_farben(self):
        """
        Loads RAL colors from a CSV file and stores them in a dictionary.

        The method reads a CSV file specified by the `RAL_FILE_NAME` constant. Each row in the file
        is expected to contain the following data:
        - Column 0: RAL number (used as the key in the dictionary).
        - Column 1: RGB values in the format "R-G-B" (e.g., "255-255-255").
        - Column 6: Color name.

        The loaded data is stored in the `_RAL_farben` attribute as a dictionary where:
        - The key is the RAL number (string).
        - The value is a tuple containing:
            - A tuple of RGB values (integers).
            - The color name (string).

        Assumes the CSV file has a header row, which is skipped during processing.

        Raises:
            ValueError: If the RGB values in the CSV file cannot be converted to integers.
            FileNotFoundError: If the specified CSV file does not exist.
            IOError: If there is an error reading the file.
        """
        """Lädt RAL-Farben aus einer CSV-Datei."""
        self._RAL_farben = {}
        with open(RAL_FILE_NAME, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Header überspringen
            for row in reader:
                ral_nummer = row[0]
                farb_name = row[6]
                r, g, b = map(int, row[1].split("-"))
                self._RAL_farben[ral_nummer] = ((r, g, b), farb_name)

    def _finde_nächste_ral_farbe(self, rgb):
        """
        Finds the RAL color with the smallest Euclidean distance to the given RGB value.

        Args:
            rgb (tuple): A tuple containing the RGB values as integers (r, g, b).

        Returns:
            tuple: A tuple containing the RAL color code and its corresponding RGB value.
        """
        """Findet die RAL-Farbe mit der kleinsten euklidischen Distanz zum gegebenen RGB-Wert."""
        r, g, b = rgb
        nächster_ral = min(
            self._RAL_farben.items(),
            key=lambda item: (item[1][0][0] - r) ** 2
            + (item[1][0][1] - g) ** 2
            + (item[1][0][2] - b) ** 2,
        )
        return nächster_ral

    def _lade_bild(self):
        """
        Loads the image, scales it proportionally, and converts it to a reduced color palette.

        This method performs the following steps:
        1. Opens the image file specified by `_input_file_name` and converts it to RGB mode.
        2. Scales the image proportionally to fit within the dimensions specified by `_breite_px` and `_höhe_px`.
        3. Converts the image to a palette-based mode (P) with a maximum of `_farben_anzahl` colors,
           using an adaptive palette, and then converts it back to RGB mode.
        4. Updates the image dimensions (`_breite` and `_länge`) based on the processed image.

        Attributes:
            _input_file_name (str): The file path of the input image.
            _breite_px (int): The maximum width of the scaled image in pixels.
            _höhe_px (int): The maximum height of the scaled image in pixels.
            _farben_anzahl (int): The number of colors to use in the adaptive palette.
            _bild (Image): The processed image object.
            _breite (int): The width of the processed image in pixels.
            _länge (int): The height of the processed image in pixels.
        """
        """Lädt das Bild und passt es an."""
        self._bild = Image.open(self._input_file_name).convert("RGB")
        # Bild proportional skalieren
        self._bild.thumbnail((self._breite_px, self._höhe_px))
        # Bild in P-Modus mit 16 Farben umwandeln
        self._bild = self._bild.convert(
            "P", palette=Image.Palette.ADAPTIVE, colors=self._farben_anzahl
        ).convert("RGB")
        self._breite, self._länge = self._bild.size

    def _zeichne_perlen(self):
        """
        Draws beads (perlen) onto the image based on the specified bead size and color mapping.
        This method processes the image in a grid-like manner, dividing it into sections
        corresponding to the size of the beads. For each section, it calculates the color
        (either the average color or the color of the center pixel) and maps it to the nearest
        RAL color. The bead is then drawn as an ellipse on the image with the mapped RAL color.
        Attributes:
            self._bild (Image): The image on which the beads are drawn.
            self._dpi (int): The resolution of the image in dots per inch.
            self._perlen_groesse (float): The size of the beads in millimeters.
            self._breite (int): The width of the image in pixels.
            self._länge (int): The height of the image in pixels.
            self._durchschnitt_farbe_berechnen (bool): Whether to calculate the average color
                of each bead section or use the center pixel's color.
            self.verwendete_farben (set): A set to store the RAL colors used in the image.
        Steps:
            1. Calculate the bead size in pixels based on the DPI and bead size in millimeters.
            2. Iterate over the image in a grid pattern based on the bead size.
            3. For each grid section:
                a. Crop the section from the image.
                b. Calculate the color (average or center pixel).
                c. Map the color to the nearest RAL color.
                d. Add the RAL color to the set of used colors.
                e. Draw an ellipse (bead) on the image with the mapped RAL color.
        """
        """Zeichnet die Perlen ins Bild."""
        draw = ImageDraw.Draw(self._bild)
        perlengröße_pixel = int(self._dpi * (self._perlen_groesse / 25.4))
        self.verwendete_farben = set()

        for x in range(0, self._breite, perlengröße_pixel):
            for y in range(0, self._länge, perlengröße_pixel):
                # Bereich für die Perle definieren (Sicherstellen, dass wir nicht über das Bild hinausgehen)
                teilbild = self._bild.crop(
                    (x, y, x + perlengröße_pixel, y + perlengröße_pixel)
                )

                # Durchschnittsfarbe berechnen oder den Mittelpunktpixelwert verwenden
                if self._durchschnitt_farbe_berechnen:
                    rgb_farbe = self._berechne_durchschnittsfarbe(teilbild)
                else:
                    rgb_farbe = teilbild.getpixel(
                        (perlengröße_pixel // 2, perlengröße_pixel // 2)
                    )

                # Nächste RAL-Farbe finden
                ral_farbe = self._finde_nächste_ral_farbe(rgb_farbe)
                self.verwendete_farben.add(
                    (ral_farbe[0], ral_farbe[1][1])
                )  # Füge die RAL-Nummer zur Liste hinzu

                # Ellipse (Perle) zeichnen
                draw.ellipse(
                    (x, y, x + perlengröße_pixel, y + perlengröße_pixel),
                    fill=ral_farbe[1][0],
                    outline="black",  # Optional: schwarze Umrandung für Perlen
                )

    def _save_image(self):
        """
        Saves the generated image with diamond pearls.

        This method saves the modified image with a new filename by replacing
        the ".jpg" extension in the input file name with "_diamond_perls.jpg".

        Returns:
            None
        """
        """Speichert das Bild mit Perlen."""
        self._bild.save(self._input_file_name.replace(".jpg", "_diamond_perls.jpg"))

    def _show_image(self):
        """
        Displays the image stored in the `_bild` attribute.

        This method uses the `show` method of the image object to open and
        display the image in the default image viewer of the system.
        """
        """Zeigt das Bild an."""
        self._bild.show()

    def _save_colors_to_textfile(self):
        """
        Writes the list of used RAL colors to a text file.

        This method writes the RAL color codes and names to a text file named
        "verwendete_farben.txt" in the same directory as the input image.

        Returns:
            None
        """
        """Schreibt die Liste der verwendeten RAL-Farben in eine Textdatei."""
        with open(
            self._input_file_name.replace(".jpg", "_verwendete_farben.txt"), "w"
        ) as file:
            for farbe, bezeichnung in self.verwendete_farben:
                file.write(f"{farbe} {bezeichnung}\n")
    
    def generate(self):
        """
        Generates the diamond image, displays it, draws pearls on it, displays it again, 
        saves the image, and returns the final image.
        Returns:
            PIL.Image.Image: The generated and processed diamond image.
        """
        """Generiert das Diamantbild und speichert es."""
        self._show_image()
        self._zeichne_perlen()
        self._show_image()
        self._save_image()
        self._save_colors_to_textfile()
        return self._bild

import csv
import sys
import os

from PIL import Image, ImageDraw, ImageStat

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.paper_size import FORMATE_MM
from config.pathnames import RAL_FILE_NAME #DATA_PATH
from config.const import DPI, PERLEN_GROESSE, FARBBEREICH, FORMAT, MM_PRO_INCH

# FIXME: !!!! Wenn eine Datei, die KEIN .jpg ist verwendet wird muss die entsprechende Erweiterung KORREKT verwendet werden !!!!
# FIXME: datei erweiterung extrahieren, unabhängig machen von gross und klein schreibung
# FIXME: datei erweiterung an alle beteiligten Methoden übergeben 
# FIXME: ODER als Instanz Variable speichern und in den Methoden berücksichtigen.

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
        _verwendete_farben (set): Set of RAL colors used in the final image.
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
        self._image_file_type: str = self._input_file_name.rsplit('.', 1)[-1].lower()
        self._perlen_groesse: float = perlen_groesse
        self._farben_anzahl: int = farben_anzahl
        self._format: str = format
        self._dpi: int = dpi
        self._formate_mm: dict = FORMATE_MM
        self._breite_px: int = round(self._formate_mm[self._format][0] * self._dpi / MM_PRO_INCH)
        self._höhe_px: int = round(self._formate_mm[self._format][1] * self._dpi / MM_PRO_INCH)
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
        self._RAL_farben: dict = {}
        with open(RAL_FILE_NAME, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Header überspringen
            for row in reader:
                ral_nummer: str = row[0]
                farb_name: str = row[6]
                try:
                    r, g, b = map(int, row[1].split("-"))
                except ValueError:
                    print(f"Fehlerhafte RGB-Werte in Zeile: {row}")
                    continue

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
        nächster_ral: tuple[str, tuple[tuple[int, int, int], str]] = min(
            self._RAL_farben.items(),
            key=lambda item: (item[1][0][0] - r) ** 2
            + (item[1][0][1] - g) ** 2
            + (item[1][0][2] - b) ** 2,
        )
        return nächster_ral

    def _lade_bild(self):
        """
        Lädt ein Bild, skaliert es proportional, dreht es bei Bedarf und reduziert die Farbpalette.
        Diese Methode führt folgende Schritte aus:
        1. Öffnet die Bilddatei, die durch `_input_file_name` angegeben ist, und konvertiert sie in den RGB-Modus.
        2. Dreht das Bild automatisch um 90 Grad, falls die Dimensionen des Bildes und die Zielmaße nicht übereinstimmen.
        3. Skaliert das Bild proportional, um innerhalb der durch `_breite_px` und `_höhe_px` angegebenen Zielmaße zu bleiben.
        4. Füllt das Bild mit weißem Hintergrund auf, falls es kleiner als die Zielmaße ist.
        5. Reduziert die Farbpalette des Bildes auf `_farben_anzahl` Farben mit einer adaptiven Palette.
        6. Aktualisiert die Bildmaße (`_breite` und `_länge`) basierend auf dem verarbeiteten Bild.
        Attribute:
            _input_file_name (str): Der Dateipfad des Eingabebildes.
            _breite_px (int): Die maximale Breite des skalierten Bildes in Pixeln.
            _höhe_px (int): Die maximale Höhe des skalierten Bildes in Pixeln.
            _farben_anzahl (int): Die Anzahl der Farben, die in der adaptiven Palette verwendet werden.
            _bild (Image): Das verarbeitete Bildobjekt.
            _breite (int): Die Breite des verarbeiteten Bildes in Pixeln.
            _länge (int): Die Höhe des verarbeiteten Bildes in Pixeln.
        """

        self._bild = Image.open(self._input_file_name).convert("RGB")

        # Originalgröße des Bildes
        orig_breite, orig_höhe = self._bild.size
        ziel_breite, ziel_höhe = self._breite_px, self._höhe_px

        # **Automatische Drehung für maximale Abdeckung**
        if (orig_breite < orig_höhe and ziel_breite > ziel_höhe) or (orig_breite > orig_höhe and ziel_breite < ziel_höhe):
            self._bild = self._bild.rotate(90, expand=True)
            orig_breite, orig_höhe = self._bild.size  # Neue Größe nach Rotation aktualisieren

        # **Skalierung mit Erhaltung des Seitenverhältnisses**
        skalierungsfaktor = min(ziel_breite / orig_breite, ziel_höhe / orig_höhe)
        neue_breite = int(orig_breite * skalierungsfaktor)
        neue_höhe = int(orig_höhe * skalierungsfaktor)

        # Bild proportional skalieren
        self._bild = self._bild.resize((neue_breite, neue_höhe), Image.Resampling.LANCZOS)

        # **Falls das Bild kleiner ist, weiß auffüllen**
        neues_bild = Image.new("RGB", (ziel_breite, ziel_höhe), (255, 255, 255))
        position = ((ziel_breite - neue_breite) // 2, (ziel_höhe - neue_höhe) // 2)
        neues_bild.paste(self._bild, position)

        self._bild = neues_bild

        # **Farben reduzieren**
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
        
        perlengröße_pixel = int(self._dpi * (self._perlen_groesse / MM_PRO_INCH))
        self._verwendete_farben = set()

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
                self._verwendete_farben.add(
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
        the <extension> in the input file name with "_diamond_perls.<extention>".

        Returns:
            None
        """
        """Speichert das Bild mit Perlen."""
        self._bild.save(self._input_file_name.replace(f'.{self._image_file_type}', f'_diamond_perls.{self._image_file_type}'))

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
            self._input_file_name.replace(f".{self._image_file_type}", "_verwendete_farben.txt"), "w", encoding='utf-8'
        ) as file:
            for farbe, bezeichnung in self._verwendete_farben:
                file.write(f"{farbe} {bezeichnung}\n")
    
    def _create_colors_pdf_file(self):
        pass
        # TODO: Implementieren
        # TODO: 1. Lade Text Datei
        # TODO: 2. erzeuge PDF mit einer Tabelle mit dem Farbnamen, evt. den RAL Wert und der Farbe
        # TODO: 3. PDF Speichern als > self._input_file_name.replace(".jpg", _farben.pdf)
        # FIXME: Hier ebenfalls berücksichtigen das evtl. ein anderes Bildformat als .jpg geladen wurde
        
    def generate(self):
        """
        Generates a diamond image, processes it by drawing pearls, and saves the results.

        This method performs the following steps:
        1. Displays the initial diamond image.
        2. Draws pearls on the diamond image.
        3. Displays the updated image with pearls.
        4. Saves the final image to a file.
        5. Saves the color information to a text file.
        6. Creates a PDF file containing the color information.

            PIL.Image.Image: The final processed diamond image with pearls.
        """
        self._zeichne_perlen()
        self._show_image()
        self._save_image()
        self._save_colors_to_textfile()
        self._create_colors_pdf_file()
        return self._bild

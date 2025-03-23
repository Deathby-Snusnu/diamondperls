import csv
import sys
import os
import re

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from PIL import Image, ImageDraw, ImageStat, ImageFont

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config.paper_size import FORMATE_MM
from config.pathnames import DMC_FILE_NAME  # DATA_PATH
from config.const import DPI, PERLEN_GROESSE, FARBBEREICH, FORMAT, MM_PRO_INCH


class GenerateDiamondperls:
    """
    GenerateDiamondperls is a class designed to create a diamond pearl pattern from an input image.
    It processes the image, reduces its color palette, and maps the colors to the closest DMC colors.
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
        _DMC_farben (dict): Dictionary of DMC colors loaded from a CSV file.
        _bild (PIL.Image.Image): The processed image.
        _breite (int): Width of the processed image.
        _länge (int): Height of the processed image.
        _verwendete_farben (set): Set of DMC colors used in the final image.
    Methods:
        __init__(input_file_name, perlen_groesse, farben_anzahl, format, dpi, durchschnitt_farbe_berechnen):
            Initializes the class with the given parameters and loads necessary resources.
        _berechne_durchschnittsfarbe(teilbild):
            Calculates the average color of a given image block.
        _lade_DMC_farben():
            Loads DMC colors from a CSV file.
        _finde_nächste_DMC_farbe(rgb):
            Finds the closest DMC color to a given RGB value using Euclidean distance.
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
        durchschnitt_farbe_berechnen=False,
    ):
        self._durchschnitt_farbe_berechnen: bool = durchschnitt_farbe_berechnen
        self._input_file_name: str = f"{input_file_name}"
        self._image_file_type: str = self._input_file_name.rsplit(".", 1)[-1].lower()
        self._perlen_groesse: float = perlen_groesse
        self._farben_anzahl: int = farben_anzahl
        self._format: str = format
        self._dpi: int = dpi
        self._formate_mm: dict = FORMATE_MM
        self._breite_px: int = round(
            self._formate_mm[self._format][0] * self._dpi / MM_PRO_INCH
        )    
        self._höhe_px: int = round(
            self._formate_mm[self._format][1] * self._dpi / MM_PRO_INCH
        )
        self._verwendete_farben: dict = {}
        try:
            self._lade_DMC_farben()
            self._lade_bild()
        except Exception as e:
            raise RuntimeError(f"Fehler beim Laden der DMC-Farben oder des Bildes: {e}")

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

    def _lade_DMC_farben(self):
        """
        Loads DMC colors from a CSV file and stores them in a dictionary.

        This method reads a CSV file specified by the `DMC_FILE_NAME` constant. Each row in the file
        is expected to contain the following data:
        - Column 0: DMC number (used as the key in the dictionary).
        - Column 1: Color name.
        - Columns 2-4: RGB values in the format "R-G-B" (e.g., "255-255-255").

        The loaded data is stored in the `_DMC_farben` attribute as a dictionary where:
        - The key is the DMC number (string).
        - The value is a tuple containing:
            - A tuple of RGB values (integers).
            - The color name (string).
        """
        self._DMC_farben = {}
        try:
            with open(DMC_FILE_NAME, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    dmc_nummer = row[0]
                    farb_name = row[1]
                    try:
                        r, g, b = map(
                            int, row[2:5]
                        )  # Convert RGB values from string to integers
                    except ValueError as e:
                        raise ValueError(f"Fehlerhafte RGB-Werte in Zeile: {row} {e}")
                        

                    self._DMC_farben[dmc_nummer] = ((r, g, b), farb_name)
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Die Datei {DMC_FILE_NAME} wurde nicht gefunden. {e}")
        except IOError as e:
            raise IOError (f"Fehler beim Lesen der Datei {DMC_FILE_NAME}: {e}")

    def _find_closest_dmc_color(self, rgb):
        """
        Finds the DMC color with the smallest Euclidean distance to the given RGB value.

        Args:
            rgb (tuple): A tuple with the RGB values as integers (r, g, b).

        Returns:
            tuple: A tuple with the DMC color number, RGB values, and the color name.
        """
        r, g, b = rgb
        # Check if the RGB value is already cached
        if not hasattr(self, '_dmc_cache'):
            self._dmc_cache = {}

        if rgb in self._dmc_cache:
            nächster_dmc = self._dmc_cache[rgb]
        else:
            nächster_dmc = min(
                self._DMC_farben.items(),
                key=lambda item: (item[1][0][0] - r) ** 2  # R
                + (item[1][0][1] - g) ** 2  # G
                + (item[1][0][2] - b) ** 2,  # B
            )
            self._dmc_cache[rgb] = nächster_dmc  # Cache the result
        dmc_nummer = nächster_dmc[0]
        rgb_farbe = nächster_dmc[1][0]  # RGB values of the closest DMC color
        farb_name = nächster_dmc[1][1]  # Color name
        return dmc_nummer, rgb_farbe, farb_name

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
        try:
            self._bild = Image.open(self._input_file_name).convert("RGB")
        except FileNotFoundError as e:
            raise FileNotFoundError(f'Datei nicht gefunden: {e}')
        except Exception as e:
            raise Exception(f'Ein Problem ist aufgetreten: {e}')
        # Originalgröße des Bildes
        orig_breite, orig_höhe = self._bild.size
        ziel_breite, ziel_höhe = self._breite_px, self._höhe_px

        # **Automatische Drehung für maximale Abdeckung**
        if (orig_breite < orig_höhe and ziel_breite > ziel_höhe) or (
            orig_breite > orig_höhe and ziel_breite < ziel_höhe
        ):
            self._bild = self._bild.rotate(90, expand=True)
            orig_breite, orig_höhe = (
                self._bild.size
            )  # Neue Größe nach Rotation aktualisieren

        # **Skalierung mit Erhaltung des Seitenverhältnisses**
        skalierungsfaktor = min(ziel_breite / orig_breite, ziel_höhe / orig_höhe)
        neue_breite = int(orig_breite * skalierungsfaktor)
        neue_höhe = int(orig_höhe * skalierungsfaktor)

        # Bild proportional skalieren
        self._bild = self._bild.resize(
            (neue_breite, neue_höhe), Image.Resampling.LANCZOS
        )

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

    def _zeichne_perlen(self) -> None:
        """
        Draws pearls on the image based on the processed color data.

        This method iterates over the image in blocks of size determined by the pearl size in pixels.
        For each block, it calculates the average color or picks the center pixel color, maps it to the
        closest DMC color, and draws a pearl (ellipse) with the corresponding color. It also numbers
        the pearls and writes the number on top of each pearl.

        Attributes:
            perlengröße_pixel (int): The size of the pearls in pixels.
            zähler (int): Counter for numbering the pearls.
            farb_mapping (dict): A mapping of DMC color numbers to their assigned numbers, names, and RGB values.
        """
        draw = ImageDraw.Draw(self._bild)

        # Calculate pearl size in pixels
        perlengröße_pixel: int = round(self._dpi * (self._perlen_groesse / MM_PRO_INCH))
        zähler: int = 1  # Start value for numbering
        farb_mapping: dict = {}  # Stores the color and its corresponding number

        for x in range(0, self._breite, perlengröße_pixel):
            for y in range(0, self._länge, perlengröße_pixel):
                # Define the crop box for the current block
                crop_box: tuple = (
                    x,
                    y,
                    min(x + perlengröße_pixel, self._breite),
                    min(y + perlengröße_pixel, self._länge),
                )
                teilbild: Image.Image = self._bild.crop(crop_box)

                # Calculate the average color or use the center pixel color
                if self._durchschnitt_farbe_berechnen:
                    rgb_farbe = self._berechne_durchschnittsfarbe(teilbild)
                else:
                    rgb_farbe = teilbild.getpixel(
                        (
                            min(perlengröße_pixel // 2, teilbild.width - 1),
                            min(perlengröße_pixel // 2, teilbild.height - 1),
                        )
                    )

                # Find the closest DMC color
                dmc_farbe: tuple = self._find_closest_dmc_color(rgb_farbe)
                dmc_nummer: str = dmc_farbe[0]
                rgb: tuple = dmc_farbe[1]
                r, g, b = rgb

                # Calculate luminance to determine text color
                luminance: float = 0.299 * r + 0.587 * g + 0.114 * b
                textfarbe: tuple = (0, 0, 0) if luminance > 128 else (255, 255, 255)

                # Assign a new number if the color is not already mapped
                if dmc_nummer not in farb_mapping:
                    farb_mapping[dmc_nummer] = (zähler, dmc_farbe[2], rgb)
                    zähler += 1

                farb_nummer: int = farb_mapping[dmc_nummer][0]

                # Draw the pearl (ellipse)
                draw.ellipse(
                    (x, y, x + perlengröße_pixel, y + perlengröße_pixel),
                    fill=rgb,  # Use the RGB tuple directly
                    outline="black",
                )

                # Determine font size dynamically, with a minimum size of 10px
                font_size: int = max(10, perlengröße_pixel // 2)
                try:
                    font = ImageFont.truetype(
                        "arial.ttf", font_size
                    )
                except IOError:
                    font = ImageFont.load_default()  # Fallback to default font if Arial is unavailable

                # Draw the number on the pearl
                draw.text(
                    (x + perlengröße_pixel // 2, y + perlengröße_pixel // 2),
                    str(farb_nummer),
                    fill=textfarbe,
                    font=font,
                    anchor="mm",  # Center the number on the pearl
                )

        # Store the used colors in the class attribute
        self._verwendete_farben: dict = farb_mapping

    def _save_image(self):
        """
        Saves the generated image with diamond pearls.

        This method saves the modified image with a new filename by replacing
        the <extension> in the input file name with "_diamond_perls.<extention>".

        Returns:
            None
        """
        """Speichert das Bild mit Perlen."""
        filename = self._input_file_name.replace(
            f".{self._image_file_type}", f"_diamond_perls.{self._image_file_type}"
        )
        self._bild.save(filename)

    def _show_image(self):
        """
        Displays the image stored in the `_bild` attribute.

        This method uses the `show` method of the image object to open and
        display the image in the default image viewer of the system.
        """
        """Zeigt das Bild an."""
        self._bild.show()

    def _create_colors_textfile(self):
        """
        Writes the list of used DMC colors to a text file.

        This method writes the DMC color codes and names to a text file named
        "verwendete_farben.txt" in the same directory as the input image.

        Returns:
            None
        """
        """Schreibt die Liste der verwendeten DMC-Farben in eine Textdatei."""
        filename = self._input_file_name.replace(
            f".{self._image_file_type}", "_verwendete_farben.txt"
        )
        with open(filename, "w", encoding="utf-8") as file:
            for nummer, (index, name, rgb) in self._verwendete_farben.items():
                file.write(
                    f"{index}. {nummer} - {name} (RGB: {rgb[0]}, {rgb[1]}, {rgb[2]})\n"
                )

    def _create_colors_pdf_file(self):
        """
        Erstellt eine PDF-Datei aus einer Textdatei und zeigt Farben als Hintergrund
        für die Textzeilen an.

        Args:
            None

        Returns:
            None
        """

        pdf_datei = self._input_file_name.replace(
            f".{self._image_file_type}", "_verwendete_farben.pdf"
        )
        txt_datei = self._input_file_name.replace(
            f".{self._image_file_type}", "_verwendete_farben.txt"
        )

        # Neue PDF-Datei erstellen
        c = canvas.Canvas(pdf_datei, pagesize=A4)
        (width, height) = A4

        # Text aus Datei lesen
        with open(txt_datei, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Startposition für Text
        y_position = height - 50  # Abstand von oben
        x_position = 50  # Startposition für die X-Achse

        # Definiere Spaltenbreiten
        column_widths = [100, 100, 300]  # Beispiel: Farbe, Nummer, Beschreibung

        # RegEx für RGB-Werte in der Form "RGB: 255, 251, 239"
        rgb_pattern = re.compile(r"RGB: (\d+), (\d+), (\d+)")

        for line in lines:
            if y_position < 50:  # Falls die Seite voll ist, neue Seite
                c.showPage()
                y_position = height - 50

            # Zerlege die Zeile in die Teile (z.B. Nummer, Name, RGB)
            parts = line.strip().split(" - ")

            if len(parts) >= 2:
                nummer_beschreibung = parts[0].strip()
                farbe_beschreibung = parts[1].strip()

                # Extrahiere die RGB-Werte mit RegEx
                match = rgb_pattern.search(farbe_beschreibung)
                if match:
                    r, g, b = map(int, match.groups())  # Extrahiere RGB-Werte

                    # Berechne die Helligkeit der Farbe
                    luminance = 0.299 * r + 0.587 * g + 0.114 * b

                    # Wähle Textfarbe basierend auf der Helligkeit der Hintergrundfarbe
                    if luminance > 128:  # Helle Farbe, dunkler Text
                        text_color = (0, 0, 0)  # Schwarz
                    else:  # Dunkle Farbe, heller Text
                        text_color = (255, 255, 255)  # Weiß

                    # Hintergrundfarbe für die Zelle (Farbe)
                    c.setFillColorRGB(r / 255, g / 255, b / 255)  # Farbe aus RGB setzen
                    c.rect(
                        x_position, y_position - 10, column_widths[0], 20, fill=1
                    )  # Rechteck als Hintergrund

                    # Text mit der passenden Farbe schreiben
                    c.setFillColorRGB(
                        text_color[0] / 255, text_color[1] / 255, text_color[2] / 255
                    )
                    c.drawString(
                        x_position + 5, y_position, nummer_beschreibung
                    )  # Nummer

                    # Beschreibenden Text (Name der Farbe)
                    c.setFillColorRGB(0, 0, 0)  # Schwarz für den Farbnamen
                    c.drawString(
                        x_position + column_widths[0] + 5,
                        y_position,
                        farbe_beschreibung,
                    )  # Farbbeschreibung

                    # Position für die nächste Zeile
                    y_position -= 30  # Zeilenabstand

        # PDF speichern
        c.save()

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
        self._create_colors_textfile()
        self._create_colors_pdf_file()
        return self._bild

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
        _is_average_color_calculation_enabled (bool): Determines whether to calculate the average color for each block.
        _input_file_name (str): Path to the input image file.
        _image_file_type (str): File type of the input image (e.g., jpg, png).
        _pearl_dimension (float): Size of the pearls in millimeters.
        _color_variation_count (int): Number of colors to reduce the image to.
        _output_file_format (str): Format of the output image (e.g., A4, A3).
        _print_dpi (int): Dots per inch for the output image.
        _format_sizes_mm (dict): Dictionary containing dimensions of formats in millimeters.
        _width_in_pixels (int): Width of the image in pixels after scaling.
        _height_in_pixels (int): Height of the image in pixels after scaling.
        _dmc_color_palette (dict): Dictionary of DMC colors loaded from a CSV file.
        _final_image (PIL.Image.Image): The processed image.
        _image_width (int): Width of the processed image in pixels.
        _image_height (int): Height of the processed image in pixels.
        _used_colors (dict): Dictionary of DMC colors used in the final image.

    Methods:
        __init__(input_file_name, pearl_dimension, color_variation_count, output_format, output_dpi, is_average_color_enabled):
            Initializes the class with the given parameters and loads necessary resources.
        _get_average_color_value(teilbild):
            Calculates the average color of a given image block.
        _load_dmc_colors():
            Loads DMC colors from a CSV file.
        _find_closest_dmc_color(rgb):
            Finds the closest DMC color to a given RGB value using Euclidean distance.
        _load_and_process_image():
            Loads the input image, scales it proportionally, and reduces its color palette.
        _create_pearl_image():
            Draws pearl-like ellipses on the image based on the processed color data.
        _save_image():
            Saves the final image with the pearl pattern applied.
        _show_image():
            Displays the current state of the image.
        _create_colors_textfile():
            Writes the list of used DMC colors to a text file.
        _create_colors_pdf_file():
            Creates a PDF file with the list of used DMC colors and their visual representation.
        generate():
            Generates the diamond pearl pattern, displays the result, and saves the image along with color information.
    """

    def __init__(
        self,
        input_file_name,
        pearl_dimension=PERLEN_GROESSE,
        color_variation_count=FARBBEREICH,
        output_format=FORMAT,
        output_dpi=DPI,
        is_average_color_enabled=False,
    ):
        self._is_average_color_calculation_enabled: bool = is_average_color_enabled
        self._input_file_name: str = f"{input_file_name}"
        self._image_file_type: str = self._input_file_name.rsplit(".", 1)[-1].lower()
        self._pearl_dimension: float = pearl_dimension
        self._color_variation_count: int = color_variation_count
        self._output_file_format: str = output_format
        self._print_dpi: int = output_dpi
        self._format_sizes_mm: dict = FORMATE_MM
        self._width_in_pixels: int = round(
            self._format_sizes_mm[self._output_file_format][0] * self._print_dpi / MM_PRO_INCH
        )    
        self._height_in_pixels: int = round(
            self._format_sizes_mm[self._output_file_format][1] * self._print_dpi / MM_PRO_INCH
        )
        self._used_colors: dict = {}
        try:
            self._load_dmc_colors()
            self._load_and_process_image()
        except Exception as e:
            raise RuntimeError(f"Fehler beim Laden der DMC-Farben oder des Bildes: {e}")

    def _get_average_color_value(self, teilbild):
        """
        Calculates the average color of a given image section (block).

        This method computes the mean RGB values of all pixels within the specified image section.

        Args:
            teilbild (PIL.Image.Image): The image section (block) for which the average color is to be calculated.

        Returns:
            tuple: A tuple of three integers representing the average RGB color values (R, G, B) of the image section.
        """
        stat = ImageStat.Stat(teilbild)
        return tuple(int(c) for c in stat.mean[:3])

    def _load_dmc_colors(self):
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
        self._dmc_color_palette = {}
        try:
            with open(DMC_FILE_NAME, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                next(reader)  # Skip header
                for row in reader:
                    dmc_number = row[0]
                    color_name = row[1]
                    try:
                        r, g, b = map(
                            int, row[2:5]
                        )  # Convert RGB values from string to integers
                    except ValueError as e:
                        raise ValueError(f"Fehlerhafte RGB-Werte in Zeile: {row} {e}")
                        

                    self._dmc_color_palette[dmc_number] = ((r, g, b), color_name)
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
            closest_dmc = self._dmc_cache[rgb]
        else:
            closest_dmc = min(
                self._dmc_color_palette.items(),
                key=lambda item: (item[1][0][0] - r) ** 2  # R
                + (item[1][0][1] - g) ** 2  # G
                + (item[1][0][2] - b) ** 2,  # B
            )
            self._dmc_cache[rgb] = closest_dmc  # Cache the result
        dmc_color_id = closest_dmc[0]
        matching_rgb_values = closest_dmc[1][0]  # RGB values of the closest DMC color
        color_name = closest_dmc[1][1]  # Color name
        return dmc_color_id, matching_rgb_values, color_name

    def _load_and_process_image(self):
        """
        Loads an image, scales it proportionally, rotates it if necessary, and reduces its color palette.

        This method performs the following steps:
        1. Opens the image file specified by `_input_file_name` and converts it to RGB mode.
        2. Automatically rotates the image by 90 degrees if its dimensions do not match the target dimensions.
        3. Scales the image proportionally to fit within the target dimensions specified by `_width_in_pixels` and `_height_in_pixels`.
        4. Fills the image with a white background if it is smaller than the target dimensions.
        5. Reduces the image's color palette to `_color_variation_count` colors using an adaptive palette.
        6. Updates the image dimensions (`_image_width` and `_image_height`) based on the processed image.

        Attributes:
            _input_file_name (str): The file path of the input image.
            _width_in_pixels (int): The maximum width of the scaled image in pixels.
            _height_in_pixels (int): The maximum height of the scaled image in pixels.
            _color_variation_count (int): The number of colors to use in the adaptive palette.
            _final_image (Image): The processed image object.
            _image_width (int): The width of the processed image in pixels.
            _image_height (int): The height of the processed image in pixels.
        """
        try:
            try:
                self._final_image = Image.open(self._input_file_name).convert("RGB")
            except Image.UnidentifiedImageError as e:
                raise RuntimeError(f"Das Bild konnte nicht identifiziert werden: {e}")
        except FileNotFoundError as e:
            raise FileNotFoundError(f'Datei nicht gefunden: {e}')
        except Exception as e:
            raise Exception(f'Ein Problem ist aufgetreten: {e}')
        # Originalgröße des Bildes
        original_width, original_height = self._final_image.size
        target_width, target_height = self._width_in_pixels, self._height_in_pixels

        # **Automatische Drehung für maximale Abdeckung**
        if (original_width < original_height and target_width > target_height) or (
            original_width > original_height and target_width < target_height
        ):
            self._final_image = self._final_image.rotate(90, expand=True)
            original_width, original_height = (
                self._final_image.size
            )  # Neue Größe nach Rotation aktualisieren

        # **Skalierung mit Erhaltung des Seitenverhältnisses**
        scaling_factor = min(target_width / original_width, target_height / original_height)
        scaled_width = int(original_width * scaling_factor)
        scaled_height = int(original_height * scaling_factor)

        # Bild proportional skalieren
        self._final_image = self._final_image.resize(
            (scaled_width, scaled_height), Image.Resampling.LANCZOS
        )

        # **Falls das Bild kleiner ist, weiß auffüllen**
        filled_background_image = Image.new("RGB", (target_width, target_height), (255, 255, 255))
        image_position = ((target_width - scaled_width) // 2, (target_height - scaled_height) // 2)
        filled_background_image.paste(self._final_image, image_position)

        self._final_image = filled_background_image

        # **Farben reduzieren**
        self._final_image = self._final_image.convert(
            "P", palette=Image.Palette.ADAPTIVE, colors=self._color_variation_count
        ).convert("RGB")

        self._image_width, self._image_height = self._final_image.size

    def _create_pearl_image(self) -> None:
        """Generates an image with pearls drawn based on processed color data.
        This method processes the image in blocks of a size determined by the pearl dimensions in millimeters 
        and the print DPI. For each block, it calculates the representative color, maps it to the closest DMC 
        color, and draws a pearl (ellipse) with the corresponding color. Each pearl is also numbered, and the 
        number is drawn on top of the pearl.
        The numbering is based on unique DMC colors, and the text color for the number is dynamically adjusted 
        based on the luminance of the pearl's color to ensure readability.
            perlengröße_pixel (int): The size of the pearls in pixels, calculated from the print DPI and pearl dimensions.
            zähler (int): Counter for numbering the pearls, incremented for each unique DMC color.
            farb_mapping (dict): A mapping of DMC color codes to their assigned numbers, names, and RGB values.
        Steps:
            1. Iterate over the image in blocks of size `perlengröße_pixel`.
            2. For each block, calculate the representative color (average or center pixel).
            3. Map the color to the closest DMC color using a predefined mapping.
            4. Draw a pearl (ellipse) with the mapped DMC color.
            5. Assign a unique number to the DMC color if it hasn't been assigned yet.
            6. Draw the number on the pearl, adjusting the text color for readability.
            7. Store the used DMC colors and their mappings in the class attribute `_used_colors`.
        Notes:
            - The font size for the numbers is dynamically calculated based on the pearl size, with a minimum size of 10px.
            - If the Arial font is unavailable, a default font is used as a fallback.
            - The method ensures that the numbering and color mapping are consistent across the entire image.
        """
        
        draw = ImageDraw.Draw(self._final_image)

        # Calculate pearl size in pixels
        pearl_size_in_pixels: int = round(self._print_dpi * (self._pearl_dimension / MM_PRO_INCH))
        pearl_index: int = 1  # Start value for numbering
        dmc_color_mapping: dict = {}  # Stores the color and its corresponding number

        for x in range(0, self._image_width, pearl_size_in_pixels):
            for y in range(0, self._image_height, pearl_size_in_pixels):
                # Define the crop box for the current block
                crop_box: tuple = (
                    x,
                    y,
                    min(x + pearl_size_in_pixels, self._image_width),
                    min(y + pearl_size_in_pixels, self._image_height),
                )
                cropped_image: Image.Image = self._final_image.crop(crop_box)

                # Calculate the average color or use the center pixel color
                if self._is_average_color_calculation_enabled:
                    rgb_color_value = self._get_average_color_value(cropped_image)
                else:
                    rgb_color_value = cropped_image.getpixel(
                        (
                            min(pearl_size_in_pixels // 2, cropped_image.width - 1),
                            min(pearl_size_in_pixels // 2, cropped_image.height - 1),
                        )
                    )

                # Find the closest DMC color
                mapped_dmc_color: tuple = self._find_closest_dmc_color(rgb_color_value)
                dmc_color_code: str = mapped_dmc_color[0]
                rgb: tuple = mapped_dmc_color[1]
                r, g, b = rgb

                # Calculate luminance to determine text color
                luminance_value: float = 0.299 * r + 0.587 * g + 0.114 * b
                text_color: tuple = (0, 0, 0) if luminance_value > 128 else (255, 255, 255)

                # Assign a new number if the color is not already mapped
                if dmc_color_code not in dmc_color_mapping:
                    dmc_color_mapping[dmc_color_code] = (pearl_index, mapped_dmc_color[2], rgb)
                    pearl_index += 1

                dmc_color_index: int = dmc_color_mapping[dmc_color_code][0]

                # Draw the pearl (ellipse)
                draw.ellipse(
                    (x, y, x + pearl_size_in_pixels, y + pearl_size_in_pixels),
                    fill=rgb,  # Use the RGB tuple directly
                    outline="black",
                )

                # Determine font size dynamically, with a minimum size of 10px
                font_size: int = max(10, pearl_size_in_pixels // 2)
                try:
                    font = ImageFont.truetype(
                        "arial.ttf", font_size
                    )
                except IOError:
                    font = ImageFont.load_default()  # Fallback to default font if Arial is unavailable

                # Draw the number on the pearl
                draw.text(
                    (x + pearl_size_in_pixels // 2, y + pearl_size_in_pixels // 2),
                    str(dmc_color_index),
                    fill=text_color,
                    font=font,
                    anchor="mm",  # Center the number on the pearl
                )

        # Store the used colors in the class attribute
        self._used_colors: dict = dmc_color_mapping

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
        self._final_image.save(filename)

    def _show_image(self):
        """
        Displays the image stored in the `_bild` attribute.

        This method uses the `show` method of the image object to open and
        display the image in the default image viewer of the system.
        """
        """Zeigt das Bild an."""
        self._final_image.show()

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
            for dmc_color_number, (color_index, color_name, color_rgb_values) in self._used_colors.items():
                file.write(
                    f"{color_index}. {dmc_color_number} - {color_name} (RGB: {color_rgb_values[0]}, {color_rgb_values[1]}, {color_rgb_values[2]})\n"
                )

    def _create_colors_pdf_file(self):
        """
        Creates a PDF file from a text file and displays colors as the background
        for the text lines.

        This method reads a text file containing color information, including DMC color codes,
        names, and RGB values. It then generates a PDF file where each line of text is displayed
        with a background color corresponding to the RGB values of the color.

        The method dynamically adjusts the text color (black or white) based on the luminance
        of the background color to ensure readability.

        Args:
            None

        Returns:
            None
        """

        output_pdf_file = self._input_file_name.replace(
            f".{self._image_file_type}", "_verwendete_farben.pdf"
        )
        color_used_text_file = self._input_file_name.replace(
            f".{self._image_file_type}", "_verwendete_farben.txt"
        )

        # Neue PDF-Datei erstellen
        pdf_canvas = canvas.Canvas(output_pdf_file, pagesize=A4)
        (width, height) = A4

        # Text aus Datei lesen
        with open(color_used_text_file, "r", encoding="utf-8") as file:
            lines = file.readlines()

        # Startposition für Text
        text_y_coordinate = height - 50  # Abstand von oben
        start_x_coordinate = 50  # Startposition für die X-Achse

        # Definiere Spaltenbreiten
        column_widths = [100, 100, 300]  # Beispiel: Farbe, Nummer, Beschreibung

        # RegEx für RGB-Werte in der Form "RGB: 255, 251, 239"
        rgb_pattern = re.compile(r"RGB: (\d+), (\d+), (\d+)")

        for line in lines:
            if text_y_coordinate < 50:  # Falls die Seite voll ist, neue Seite
                pdf_canvas.showPage()
                text_y_coordinate = height - 50

            # Zerlege die Zeile in die Teile (z.B. Nummer, Name, RGB)
            line_segments = line.strip().split(" - ")

            if len(line_segments) >= 2:
                color_number = line_segments[0].strip()
                color_description = line_segments[1].strip()

                # Extrahiere die RGB-Werte mit RegEx
                match = rgb_pattern.search(color_description)
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
                    pdf_canvas.setFillColorRGB(r / 255, g / 255, b / 255)  # Farbe aus RGB setzen
                    pdf_canvas.rect(
                        start_x_coordinate, text_y_coordinate - 10, column_widths[0], 20, fill=1
                    )  # Rechteck als Hintergrund

                    # Text mit der passenden Farbe schreiben
                    pdf_canvas.setFillColorRGB(
                        text_color[0] / 255, text_color[1] / 255, text_color[2] / 255
                    )
                    pdf_canvas.drawString(
                        start_x_coordinate + 5, text_y_coordinate, color_number
                    )  # Nummer

                    # Beschreibenden Text (Name der Farbe)
                    pdf_canvas.setFillColorRGB(0, 0, 0)  # Schwarz für den Farbnamen
                    pdf_canvas.drawString(
                        start_x_coordinate + column_widths[0] + 5,
                        text_y_coordinate,
                        color_description,
                    )  # Farbbeschreibung

                    # Position für die nächste Zeile
                    text_y_coordinate -= 30  # Zeilenabstand

        # PDF speichern
        pdf_canvas.save()

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
        self._create_pearl_image()
        self._show_image()
        self._save_image()
        self._create_colors_textfile()
        self._create_colors_pdf_file()
        return self._final_image

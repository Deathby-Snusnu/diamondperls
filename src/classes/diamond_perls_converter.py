from PIL import Image, ImageDraw, ImageStat
import csv


from src.const.paper_size import FORMATE_MM
from src.const.pathnames import RAL_FILE_NAME

class GenerateDiamondperls:
    
    def __init__(self,
                 input_file_name,
                 perlen_groesse=2.5, 
                 farben_anzahl=64, 
                 format="A4", 
                 dpi=300,
                 durchschnitt_farbe_berechnen=True):
        self._durchschnitt_farbe_berechnen = durchschnitt_farbe_berechnen
        self._input_file_name = input_file_name
        self._perlen_groesse = perlen_groesse
        self._farben_anzahl = farben_anzahl
        self._format = format
        self._dpi = dpi
        self._formate_mm = FORMATE_MM
        self._breite_px = self._formate_mm[self._format][0] * self._dpi // 25.4
        self._höhe_px = self._formate_mm[self._format][1] * self._dpi // 25.4
        self._lade_RAL_farben()
        self._lade_bild()

    def _berechne_durchschnittsfarbe(self, teilbild):
        """Berechnet die Durchschnittsfarbe eines Bildbereichs (Block)."""
        stat = ImageStat.Stat(teilbild)
        return tuple(int(c) for c in stat.mean[:3])

    def _lade_RAL_farben(self):
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
        """Findet die RAL-Farbe mit der kleinsten euklidischen Distanz zum gegebenen RGB-Wert."""
        r, g, b = rgb
        nächster_ral = min(
            self._RAL_farben.items(),
            key=lambda item: (item[1][0][0] - r) ** 2 + (item[1][0][1] - g) ** 2 + (item[1][0][2] - b) ** 2
        )
        return nächster_ral
    
    def _lade_bild(self):
        """Lädt das Bild und passt es an."""
        self._bild = Image.open(self._input_file_name).convert("RGB")
        # Bild proportional skalieren
        self._bild.thumbnail((self._breite_px, self._höhe_px))
        # Bild in P-Modus mit 16 Farben umwandeln
        self._bild = self._bild.convert("P", palette=Image.Palette.ADAPTIVE, colors=self._farben_anzahl).convert("RGB")
        self._breite, self._länge = self._bild.size

    def _zeichne_perlen(self):
        """Zeichnet die Perlen ins Bild."""
        draw = ImageDraw.Draw(self._bild)
        perlengröße_pixel = int(self._dpi * (self._perlen_groesse / 25.4))
        self._verwendete_farben = set()

        for x in range(0, self._breite, perlengröße_pixel):
            for y in range(0, self._länge, perlengröße_pixel):
                # Bereich für die Perle definieren (Sicherstellen, dass wir nicht über das Bild hinausgehen)
                teilbild = self._bild.crop((x, y, x + perlengröße_pixel, y + perlengröße_pixel))

                # Durchschnittsfarbe berechnen oder den Mittelpunktpixelwert verwenden
                if self._durchschnitt_farbe_berechnen:
                    rgb_farbe = self._berechne_durchschnittsfarbe(teilbild)
                else:
                    rgb_farbe = teilbild.getpixel((perlengröße_pixel // 2, perlengröße_pixel // 2))
                
                # Nächste RAL-Farbe finden
                ral_farbe = self._finde_nächste_ral_farbe(rgb_farbe)
                self._verwendete_farben.add(ral_farbe[0])  # Füge die RAL-Nummer zur Liste hinzu
                
                # Ellipse (Perle) zeichnen
                draw.ellipse(
                    (x, y, x + perlengröße_pixel, y + perlengröße_pixel),
                    fill=rgb_farbe,
                    outline="black"  # Optional: schwarze Umrandung für Perlen
                )

    def _save_image(self):
        """Speichert das Bild mit Perlen."""
        self._bild.save(self._input_file_name.replace(".jpg", "_diamond_perls.jpg"))

    def _show_image(self):
        """Zeigt das Bild an."""
        self._bild.show()

    def generate(self):
        """Generiert das Diamantbild und speichert es."""
        self._show_image()
        self._zeichne_perlen()
        self._save_image()
        self._show_image()
        print(f"Verwendete RAL-Farben: {self._verwendete_farben}")
        return self._bild

if __name__ == "__main__":
    dp = GenerateDiamondperls(".\\data\\test_bild.jpg")
    dp.generate()
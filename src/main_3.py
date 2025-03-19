from PIL import Image, ImageDraw, ImageStat
import csv

def lade_RAL_farben(dateipfad):
    """Lädt die RAL-Farben aus einer CSV-Datei und gibt ein Dictionary zurück."""
    farben = {}
    with open(dateipfad, "r", encoding="utf-8") as file:
        reader = csv.reader(file)
        next(reader)  # Erste Zeile (Header) überspringen
        for row in reader:
            ral_nummer = row[0]  # RAL-Code als String behalten (z. B. "RAL 1000")
            farb_name = row[6]  # Farbname (z. B. "Grünbeige")
            r, g, b = map(int, row[1].split("-"))  # RGB-Werte aus "205-186-136" extrahieren
            farben[ral_nummer] = ((r, g, b), farb_name)
    return farben

def finde_nächste_ral_farbe(rgb, ral_farben):
    """Findet die RAL-Farbe mit der kleinsten euklidischen Distanz zum gegebenen RGB-Wert und gibt den Farbnamen zurück."""
    r, g, b = rgb
    nächster_ral = min(
        ral_farben.items(),
        key=lambda item: (item[1][0][0] - r) ** 2 + (item[1][0][1] - g) ** 2 + (item[1][0][2] - b) ** 2
    )
    return nächster_ral  # Gibt (RAL-Nummer, ((R, G, B), Farbname)) zurück

def berechne_durchschnittsfarbe(teilbild):
    """Berechnet die Durchschnittsfarbe eines Bildbereichs (Block)."""
    stat = ImageStat.Stat(teilbild)
    return tuple(int(c) for c in stat.mean[:3])  # Durchschnittsfarbe (RGB)

# Bild laden
perlen_bild = Image.open(".\\data\\test_bild.jpg").convert("RGB")


# A4-Abmessungen in Pixel
A4_breite_pixel = int(300 * (210 / 25.4))
A4_länge_pixel = int(300 * (297 / 25.4))

# Bild proportional skalieren
perlen_bild.thumbnail((A4_breite_pixel, A4_länge_pixel))
# Bild in P-Modus mit 16 Farben umwandeln
perlen_bild = perlen_bild.convert("P", palette=Image.Palette.ADAPTIVE, colors=16).convert("RGB")

breite, länge = perlen_bild.size

# Zeichnen vorbereiten
draw = ImageDraw.Draw(perlen_bild)
perlengröße_in_mm = 2.5
perlengröße_pixel = int(300 * (perlengröße_in_mm / 25.4))

ral_farben = lade_RAL_farben(".\\data\\RAL_farben.csv")
verwendete_farben = dict()

# Option, ob Durchschnittsfarbe berechnet werden soll
durchschnitt_farbe_berechnen = True  # Setze auf True, um Durchschnittsfarbe zu verwenden

# Iteriere über das Bild und zeichne Perlen (Ellipsen)
for x in range(0, breite, perlengröße_pixel):
    for y in range(0, länge, perlengröße_pixel):
        # Bereich für die Perle definieren (Sicherstellen, dass wir nicht über das Bild hinausgehen)
        box = (x, y, min(x + perlengröße_pixel, breite), min(y + perlengröße_pixel, länge))

        if durchschnitt_farbe_berechnen:
            # Durchschnittsfarbe berechnen
            teilbild = perlen_bild.crop(box)
            pixel_farbe = berechne_durchschnittsfarbe(teilbild)
        else:
            # Direkte Pixel-Farbe verwenden
            pixel_farbe = perlen_bild.getpixel((x, y))

        # Ellipse zeichnen
        draw.ellipse((x, y, x + perlengröße_pixel, y + perlengröße_pixel), fill=pixel_farbe, outline="black")

        # RAL-Farbe finden und anzeigen
        ral_farbe = finde_nächste_ral_farbe(pixel_farbe, ral_farben)
        verwendete_farben[ral_farbe[0]] = ral_farbe[1]

# Bild anzeigen
perlen_bild.show()
perlen_bild.save(".\\data\\diamond_perls_a4.jpg")

# farben als RAL Farben anzeigen
for k, v in verwendete_farben.items():
    print(f'{k}: {v}')
# Anzahl der verwendeten Farben
print(len(verwendete_farben))

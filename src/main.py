from PIL import Image, ImageDraw

# DIN A4 in Pixel bei 300 DPI
a4_breite_px = 2480
a4_hoehe_px = 3508

# Größe der Diamond Painting Perlen in Pixel (2,8 mm = ca. 33 px)
perlen_groesse = 33  

# Berechnung des Rasters (Anzahl Perlen)
spalten = a4_breite_px // perlen_groesse  # Anzahl der Spalten (max. Breite)
zeilen = a4_hoehe_px // perlen_groesse  # Anzahl der Zeilen (max. Höhe)

# Bild öffnen
bild = Image.open(".\\data\\test_bild.jpg").convert("RGB")

# Seitenverhältnis berechnen
bild_breite, bild_hoehe = bild.size
ratio = min(spalten / bild_breite, zeilen / bild_hoehe)

# Neue Größe berechnen (möglichst groß ohne Verzerrung)
neue_breite = int(bild_breite * ratio)
neue_hoehe = int(bild_hoehe * ratio)

# Bild proportional skalieren
bild = bild.resize((neue_breite, neue_hoehe))

# Farben reduzieren
farben_anzahl = 64  
bild = bild.convert("P", palette=Image.Palette.ADAPTIVE, colors=farben_anzahl).convert("RGB")

# Neues A4-Bild mit weißem Hintergrund erstellen
perlen_bild = Image.new("RGB", (a4_breite_px, a4_hoehe_px), "white")
draw = ImageDraw.Draw(perlen_bild)

# Berechnung der Zentrierung
x_offset = (spalten - neue_breite) // 2
y_offset = (zeilen - neue_hoehe) // 2

# Durch jedes Pixel iterieren und eine "Perle" zeichnen
for y in range(neue_hoehe):
    for x in range(neue_breite):
        rgb_farbe = bild.getpixel((x, y))

        # Position berechnen (inkl. Zentrierung)
        x_pos = (x + x_offset) * perlen_groesse + perlen_groesse // 2
        y_pos = (y + y_offset) * perlen_groesse + perlen_groesse // 2

        # Perle zeichnen
        draw.ellipse(
            (x_pos - perlen_groesse // 2, y_pos - perlen_groesse // 2,
             x_pos + perlen_groesse // 2, y_pos + perlen_groesse // 2),
            fill=rgb_farbe
        )

# Bild speichern und anzeigen
perlen_bild.save(".\\data\\diamond_perls_a4_optimal.jpg")
perlen_bild.show()

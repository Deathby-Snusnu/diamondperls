import numpy as np
from PIL import Image
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor

# Funktion zur Berechnung der Durchschnittsfarbe eines Blocks
def berechne_durchschnittsfarbe(bild, x, y, block_size=3):
    # Bild in ein NumPy-Array umwandeln (so wird es schneller)
    bild_array = np.array(bild)
    
    # Block extrahieren (Sicherstellen, dass wir nicht über das Bild hinausgehen)
    block = bild_array[y:y+block_size, x:x+block_size]
    
    # Wenn der Block kleiner als die gewünschte Blockgröße ist, Randpixel füllen
    if block.shape[0] < block_size or block.shape[1] < block_size:
        block = np.pad(
            block,
            ((0, block_size - block.shape[0]), (0, block_size - block.shape[1]), (0, 0)),
            mode='edge'
        )

    r, g, b = block[:, :, 0].mean(), block[:, :, 1].mean(), block[:, :, 2].mean()
    return (int(r), int(g), int(b))
    
    return (int(r), int(g), int(b), x, y)

# Funktion zur Verteilung der Arbeit an mehrere Threads
def berechne_perlenfarben(bild, block_size=3):
    # Bildgröße
    bild_breite, bild_hoehe = bild.size
    perlen_farbe = {}

    # ThreadPoolExecutor für Multithreading
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Alle Positionen (x, y) für Blöcke berechnen
        future_to_pixel = {}
        
        for y in range(0, bild_hoehe, block_size):
            for x in range(0, bild_breite, block_size):
                future = executor.submit(berechne_durchschnittsfarbe, bild, x, y, block_size)
                future_to_pixel[future] = (x, y)
        for future in concurrent.futures.as_completed(future_to_pixel):
            r, g, b, x, y = future.result()
            perlen_farbe[(x, y)] = (r, g, b)

    return perlen_farbe

# Bild laden
bild = Image.open(".\\data\\test_bild.jpg").convert("RGB")

# Durchschnittsfarben berechnen
block_size = 3
perlen_farben = berechne_perlenfarben(bild, block_size)

# Beispiel: Zeige das Ergebnis für alle berechneten Blockfarben
print(perlen_farben)

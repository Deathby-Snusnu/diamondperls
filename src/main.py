from src.classes.diamond_pearls_converter import GenerateDiamondperls


from config.pathnames import DATA_PATH

def main():
    generator = GenerateDiamondperls(
        input_file_name=f"test_bild.jpg",
        perlen_groesse=2.5,
        farben_anzahl=32,
        format="A6",
        dpi=300,
        durchschnitt_farbe_berechnen=True,
    )
    generator.generate()
    
    
    text_farben: list = list(generator._verwendete_farben)
    
    print(text_farben)
    print(type(text_farben))
    print(len(text_farben))
    for farbe, bezeichnung in text_farben:
        print(farbe, bezeichnung)
if __name__ == "__main__":
    main()

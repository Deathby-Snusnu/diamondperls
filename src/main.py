from classes.diamond_perls_converter import GenerateDiamondperls


def main():
    generator = GenerateDiamondperls(
        input_file_name="\\data\test_bild.jpg", 
        perlen_groesse=2.8, 
        farben_anzahl=64, 
        format="A4", 
        dpi=300,
        durchschnitt_farbe_berechnen=True
    )
    generator.generate()
    
if __name__ == "__main__":
    main()
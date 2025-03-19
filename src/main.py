from classes.diamond_perls_converter import GenerateDiamondperls


def main():
    generator = GenerateDiamondperls(
        input_file_name=".\\data\\test_bild.jpg",
        perlen_groesse=2.5,
        farben_anzahl=128,
        format="A3",
        dpi=300,
        durchschnitt_farbe_berechnen=True,
    )
    generator.generate()
    print(generator.verwendete_farben)
    print(len(generator.verwendete_farben))
if __name__ == "__main__":
    main()


import argparse


def parse_arguments():
    """Récupère et vérifie les arguments de la ligne de commande."""
    parser = argparse.ArgumentParser(
        description="Entraînement et simulation de Learn2Slither."
    )

    parser.add_argument(
        "-episodes",
        type=int,
        default=1,
        help="Nombre de parties d'entraînement."
    )

    parser.add_argument(
        "-dontlearn",
        action="store_true",
        help="Charge un modèle et joue sans apprentissage."
    )

    parser.add_argument(
        "-model",
        type=str,
        default=None,
        help="Chemin du modèle à charger ou sauvegarder."
    )

    parser.add_argument(
        "-width",
        type=int,
        default=10,
        help="Largeur du plateau."
    )

    parser.add_argument(
        "-height",
        type=int,
        default=10,
        help="Hauteur du plateau."
    )

    parser.add_argument(
        "-quiet",
        action="store_true",
        help="Désactive l'affichage des résultats d'entraînement."
    )

    parser.add_argument(
        "-evaluate",
        type=int,
        default=0,
        help="Nombre de parties utilisées pour évaluer un modèle."
    )

    parser.add_argument(
        "-gui",
        action="store_true",
        help="Lance l'interface graphique."
    )

    parser.add_argument(
        "-speed",
        type=int,
        default=8,
        help="Vitesse initiale de la GUI, en déplacements par seconde."
    )

    args = parser.parse_args()

    if args.evaluate < 0:
        parser.error("-evaluate ne peut pas être négatif.")

    if args.evaluate > 0 and not args.model:
        parser.error("-evaluate nécessite -model.")

    if args.evaluate > 0 and args.dontlearn:
        parser.error("-evaluate et -dontlearn sont incompatibles.")

    if args.episodes < 1:
        parser.error("-episodes doit être supérieur ou égal à 1.")

    if args.width < 3 or args.height < 3:
        parser.error("Les dimensions du plateau doivent être au moins 3.")

    if args.dontlearn and not args.model:
        parser.error("-dontlearn nécessite -model.")

    if args.gui and not args.dontlearn:
        parser.error("-gui nécessite -dontlearn et -model.")

    if args.speed < 1 or args.speed > 30:
        parser.error("-speed doit être compris entre 1 et 30.")

    return args

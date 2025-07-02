import os

def afficher_arborescence(racine: str, prefixe: str = "", niveau: int = 0, max_level: int = 3):
    """
    Affiche l’arborescence du dossier jusqu’à une profondeur donnée.

    Paramètres :
    -----------
    racine : str
        Chemin du dossier à explorer
    prefixe : str
        Préfixe d’indentation (utile pour la récursivité)
    niveau : int
        Niveau actuel de profondeur
    max_level : int
        Profondeur maximale d’affichage
    """
    if niveau > max_level:
        return

    try:
        elements = sorted(os.listdir(racine))
    except PermissionError:
        print(f"{prefixe}[Permission Denied] {racine}")
        return

    for element in elements:
        chemin = os.path.join(racine, element)
        if os.path.isdir(chemin):
            print(f"{prefixe}📁 {element}/")
            afficher_arborescence(chemin, prefixe + "    ", niveau + 1, max_level)
        else:
            print(f"{prefixe}📄 {element}")

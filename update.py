import os
import platform
import subprocess
import sys


def run_command(command, description):
    """Exécute une commande système et affiche un message propre."""
    print(f"\n{description}...")
    try:
        subprocess.run(command, check=True, shell=True)
        print(f"{description} : Terminé !")
    except subprocess.CalledProcessError as e:
        print(f"Erreur lors de : {description}")
        print(f"Détails : {e}")
        sys.exit(1)


def main():
    print("==========================================")
    print(" Script de mise à jour du projet Django  ")
    print("==========================================")

    securite = input("Avez vous des fichiers non commit sur votre branche de travail ? o/n ")
    if securite in ["o", "oui", "y", "yes"]:
        run_command(["git", "stash"],"Mise en réserve des fichiers non commit")

    run_command(["git", "checkout", "main"], "Basculement sur la branche main")
    run_command(["git", "pull", "origin", "main"], "Récupération du dernier code")

    is_windows = platform.system() == "Windows"
    venv_python = (
        os.path.join(".venv", "Scripts", "python.exe")
        if is_windows
        else os.path.join(".venv", "bin", "python")
    )

    if not os.path.exists(venv_python):
        print(
            "\nErreur : L'environnement virtuel (.venv) n'a pas été trouvé !"
        )
        print("Veuillez d'abord créer l'environnement avec : python -m venv .venv")
        sys.exit(1)

    run_command(
        [venv_python, "-m", "pip", "install", "-r", "requirements.txt"],
        "Mise à jour des packages pip",
    )

    creation_db = input("Souhaitez vous relancer une création de base de donnée et la génération de données fictive ? o/n ")

    if creation_db in ["o", "oui", "y", "yes"]:
        run_command(
        [venv_python, "manage.py", "migrate"],
        "Application des migrations Django",
        )

        run_command(
        [venv_python, "manage.py", "seed_db"],
        "Génération des données de tests"
        )

    creation = input("Voulez-vous créer une nouvelle branche de travail ? o/n ")
    name = input("Quel est le nom de la branche sur laquelle vous voulez travailler ? ")
    if creation in ["o", "oui", "y", "yes"]:
        run_command(
        ["git", "checkout", "-b", name], "Création de la brache"
        )
    else :
        run_command(["git", "checkout", name], "Retour sur la branche de travail")
        try :
            run_command(["git", "merge", "main"], "Intègration des mise à jour à la branche de travail")
            print("La fusion des branches c'est déroulé sans soucis !")
            if securite in ["o", "oui", "y", "yes"]:
                run_command(["git", "stash", "pop"], "Restauration des modifications local")
        except subprocess.CalledProcessError :
            print("ATTENTION DES CONFLITS SONT DETECTES !")
            print("1. Réglez les conflits dans les fichiers marqués en rouge.")
            print("2. Une fois réglé, si vous aviez des modifications non commit vous pouvez les récupérer avec la commande : git stash pop")

    print("\nTout est à jour et prêt pour continuer!")


if __name__ == "__main__":
    main()
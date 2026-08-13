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
    print(" Script de mise à jour du projet Django")
    print("==========================================")

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

    run_command(
        [venv_python, "manage.py", "migrate"],
        "Application des migrations Django",
    )

    run_command(
        [venv_python, "manage.py", "seed_db"],
        "Génération des données de tests"
    )

    name = input("Quel est le nom de la barnche sur laquelle vous voulez travailez ? ")
    run_command(
        f"git checkout -b {name}", "Création de la brache"
    )

    print("\nTout est à jour et prêt pour continuer!")


if __name__ == "__main__":
    main()
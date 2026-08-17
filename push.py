import subprocess
import sys
import webbrowser

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

def get_current_branch():
    """Récupère automatiquement le nom de la branche courante."""
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return None


def open_github_pr_url(branch_name):
    """Ouvre la page de création de PR sur GitHub dans le navigateur par défaut."""
    repo_url = "https://github.com/ClementGiz/Projet-groupe-back"

    pr_url = f"{repo_url}/compare/main...{branch_name}?expand=1"

    print(f"\nOuverture de GitHub pour créer la Pull Request sur 'main'...")
    webbrowser.open(pr_url)

def main():
    print("==========================================")
    print(" Script de push de code sur git ")
    print("==========================================")

    run_command(["git", "add", "."], "Ajout des fichier dans la branche.")
    message = input("Entrer votre message de commit : ").strip()
    run_command(["git", "commit", "-m", message], "Envoie du commit !")

    current_branch = get_current_branch()
    if current_branch:
        branch = input(
            f"Branche détectée [{current_branch}]. Appuyez sur Entrée pour valider ou tapez un autre nom : "
        ).strip()
        if not branch:
            branch = current_branch
    else:
        branch = input("Entrer le nom de votre branche : ").strip()

    run_command(
        ["git", "push", "--set-upstream", "origin", branch],
        f"Push sur la branche '{branch}'",
    )

    create_pr = input("\nVoulez-vous ouvrir GitHub pour demander un merge sur 'main' ? (o/n) : ").strip().lower()

    if create_pr in ["o", "oui", "y", "yes"]:
        open_github_pr_url(branch)

if __name__ == "__main__":
    main()
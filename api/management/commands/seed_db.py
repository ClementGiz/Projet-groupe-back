import random
from datetime import timedelta
from django.core.management.base import BaseCommand
from faker import Faker
from api.models import (
    Filiere, Cours, Cursus, CursusCours, Promotion,
    User, EleveProfile, FormateurProfile, CoursDonne
)

class Command(BaseCommand):
    help = "Remplit la base de données avec des données de test réalistes"

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Nettoyage de la base de données..."))
        User.objects.filter(is_superuser=False).delete()
        Filiere.objects.all().delete()
        Cours.objects.all().delete()

        fake = Faker('fr_FR')

        self.stdout.write(self.style.SUCCESS("Génération des données en cours..."))

        filieres_data = [
            ("DEV", "Développement"),
            ("SYS", "Système & Réseaux"),
        ]
        filieres = []
        for code, nom in filieres_data:
            filiere = Filiere.objects.create(code=code, nom=nom)
            filieres.append(filiere)

        cours_data = [
            ("HTML", "Web Client / HTML & CSS", 35),
            ("JS", "JavaScript initiation", 35),
            ("POO", "Programmation Orientée Objet / Java", 35),
            ("SQL", "Langage SQL / SQL Server", 70),
            ("NODE", "Développement Web côté Serveur avec JavaScript / Node.js et NoSQL", 35),
            ("PHP", "Développement Web côté Serveur (Back-End) / PHP", 70),
            ("PROJ", "Projet Fullstack - Web / Java Spring Boot + Angular", 105),
        ]
        cours_list = []
        for code, libelle, duree in cours_data:
            c = Cours.objects.create(code=code, libelle=libelle, duree=duree)
            cours_list.append(c)

        cursus_dev = Cursus.objects.create(
            code="CDA",
            libelle="Concepteur Développeur d'Applications",
            filiere=filieres[0]
        )
        for index, c in enumerate(cours_list[:5], start=1):
            CursusCours.objects.create(cursus=cursus_dev, cours=c, ordre=index)

        promotions = []
        for filiere in filieres:
            for year in [2025, 2026]:
                start_date = fake.date_between(start_date=f'-{2026-year+1}y', end_date=f'-{2026-year}y')
                end_date = start_date + timedelta(days=300)
                p = Promotion.objects.create(
                    filiere=filiere,
                    nom=f"{filiere.code} - Promo {year}",
                    date_debut=start_date,
                    date_fin=end_date
                )
                promotions.append(p)

        formateurs = []
        for _ in range(4):
            first_name = fake.first_name()
            last_name = fake.last_name()
            user = User.objects.create_user(
                username=f"formateur_{first_name.lower()}",
                email=f"{first_name.lower()}.{last_name.lower()}@ecole.fr",
                first_name=first_name,
                last_name=last_name,
                password="password123",
                role=User.Role.FORMATEUR
            )
            formateur_profile = FormateurProfile.objects.create(user=user)
            formateurs.append(formateur_profile)

        for promo in promotions:
            for _ in range(8):  # 8 élèves par promo
                first_name = fake.first_name()
                last_name = fake.last_name()
                user = User.objects.create_user(
                    username=fake.unique.user_name(),
                    email=fake.unique.email(),
                    first_name=first_name,
                    last_name=last_name,
                    password="password123",
                    role=User.Role.ELEVE
                )
                EleveProfile.objects.create(user=user, promotion=promo)

        User.objects.create_user(
            username="admin_test",
            email="admin@ecole.fr",
            first_name="Admin",
            last_name="System",
            password="adminpassword",
            role=User.Role.ADMIN,
            is_staff=True
        )

        cursus_cours_list = list(CursusCours.objects.all())
        for promo in promotions:
            for cc in random.sample(cursus_cours_list, min(3, len(cursus_cours_list))):
                CoursDonne.objects.create(
                    formateur=random.choice(formateurs),
                    promotion=promo,
                    cours=cc,
                    date_debut=promo.date_debut + timedelta(days=random.randint(1, 30)),
                    date_fin=promo.date_debut + timedelta(days=random.randint(31, 60))
                )

        self.stdout.write(self.style.SUCCESS("Base de données remplie avec succès !"))
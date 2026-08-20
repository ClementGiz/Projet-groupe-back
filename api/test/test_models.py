from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta
from api.models import (
    Filiere, Cours, Cursus, CursusCours, Promotion,
    User, EleveProfile, FormateurProfile, CoursDonne
)


class FiliereModelTest(TestCase):
    def test_str_representation(self):
        filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.assertEqual(str(filiere), "Développement")


class CoursModelTest(TestCase):
    def test_default_duree(self):
        cours = Cours.objects.create(code="ALG", libelle="Algorithmique")
        self.assertEqual(cours.duree, 35)

    def test_str_representation(self):
        cours = Cours.objects.create(code="WEB", libelle="Web Client / HTML & CSS")
        self.assertEqual(str(cours), "Web Client / HTML & CSS")


class CursusModelTest(TestCase):
    def setUp(self):
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")

    def test_str_representation(self):
        cursus = Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=self.filiere)
        self.assertEqual(str(cursus), "Développement : D2WL - Développeur Web")

    def test_cascade_delete_filiere_deletes_cursus(self):
        Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=self.filiere)
        self.filiere.delete()
        self.assertEqual(Cursus.objects.count(), 0)

    def test_many_to_many_via_cursuscours(self):
        cursus = Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=self.filiere)
        cours = Cours.objects.create(code="ALG", libelle="Algorithmique")
        CursusCours.objects.create(cursus=cursus, cours=cours, ordre=1)
        self.assertIn(cours, cursus.cours.all())


class CursusCoursModelTest(TestCase):
    def setUp(self):
        filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.cursus = Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=filiere)
        self.cours = Cours.objects.create(code="ALG", libelle="Algorithmique")

    def test_str_representation(self):
        cc = CursusCours.objects.create(cursus=self.cursus, cours=self.cours, ordre=1)
        self.assertEqual(str(cc), "D2WL - Algorithmique (Ordre: 1)")

    def test_unique_constraint_cursus_cours(self):
        CursusCours.objects.create(cursus=self.cursus, cours=self.cours, ordre=1)
        with self.assertRaises(IntegrityError):
            CursusCours.objects.create(cursus=self.cursus, cours=self.cours, ordre=2)


class PromotionModelTest(TestCase):
    def setUp(self):
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")

    def test_str_representation(self):
        promo = Promotion.objects.create(
            filiere=self.filiere, nom="Promo 2025",
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=365)
        )
        self.assertEqual(str(promo), "Promo 2025")

    def test_cascade_delete_filiere_deletes_promotion(self):
        Promotion.objects.create(
            filiere=self.filiere, nom="Promo 2025",
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=365)
        )
        self.filiere.delete()
        self.assertEqual(Promotion.objects.count(), 0)


class UserModelTest(TestCase):
    def test_default_role_is_eleve(self):
        user = User.objects.create_user(username="jdupont", password="pass123")
        self.assertEqual(user.role, User.Role.ELEVE)
        self.assertTrue(user.is_eleve)

    def test_is_admin_property(self):
        user = User.objects.create_user(username="admin1", password="pass123", role=User.Role.ADMIN)
        self.assertTrue(user.is_admin)
        self.assertFalse(user.is_eleve)

    def test_is_ref_property(self):
        user = User.objects.create_user(username="ref1", password="pass123", role=User.Role.REF)
        self.assertTrue(user.is_ref)

    def test_is_formateur_property(self):
        user = User.objects.create_user(username="form1", password="pass123", role=User.Role.FORMATEUR)
        self.assertTrue(user.is_formateur)


class EleveProfileModelTest(TestCase):
    def setUp(self):
        filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.promotion = Promotion.objects.create(
            filiere=filiere, nom="Promo 2025",
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=365)
        )

    def test_str_with_full_name(self):
        user = User.objects.create_user(
            username="jdupont", password="pass123",
            first_name="Jean", last_name="Dupont", role=User.Role.ELEVE
        )
        profile = EleveProfile.objects.create(user=user, promotion=self.promotion)
        self.assertEqual(str(profile), "Élève: Jean Dupont")

    def test_str_fallback_to_username(self):
        user = User.objects.create_user(username="jdupont", password="pass123")
        profile = EleveProfile.objects.create(user=user, promotion=self.promotion)
        self.assertEqual(str(profile), "Élève: jdupont")

    def test_one_to_one_constraint(self):
        user = User.objects.create_user(username="jdupont", password="pass123")
        EleveProfile.objects.create(user=user, promotion=self.promotion)
        with self.assertRaises(IntegrityError):
            EleveProfile.objects.create(user=user, promotion=self.promotion)

    def test_cascade_delete_promotion_deletes_eleve_profile(self):
        user = User.objects.create_user(username="jdupont", password="pass123")
        EleveProfile.objects.create(user=user, promotion=self.promotion)
        self.promotion.delete()
        self.assertEqual(EleveProfile.objects.count(), 0)


class FormateurProfileModelTest(TestCase):
    def test_str_representation(self):
        user = User.objects.create_user(
            username="pmartin", password="pass123",
            first_name="Paul", last_name="Martin", role=User.Role.FORMATEUR
        )
        profile = FormateurProfile.objects.create(user=user)
        self.assertEqual(str(profile), "Formateur: Paul Martin")


class CoursDonneModelTest(TestCase):
    def setUp(self):
        filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.cursus = Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=filiere)
        self.cours = Cours.objects.create(code="ALG", libelle="Algorithmique")
        self.cursus_cours = CursusCours.objects.create(cursus=self.cursus, cours=self.cours, ordre=1)
        self.promotion = Promotion.objects.create(
            filiere=filiere, nom="Promo 2025",
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=365)
        )
        user = User.objects.create_user(username="pmartin", password="pass123", role=User.Role.FORMATEUR)
        self.formateur = FormateurProfile.objects.create(user=user)

    def test_str_representation(self):
        cd = CoursDonne.objects.create(
            formateur=self.formateur, promotion=self.promotion,
            cours=self.cursus_cours, date_debut=timezone.now().date()
        )
        self.assertIn("Algorithmique", str(cd))

    def test_date_fin_optional(self):
        cd = CoursDonne.objects.create(
            formateur=self.formateur, promotion=self.promotion,
            cours=self.cursus_cours, date_debut=timezone.now().date()
        )
        self.assertIsNone(cd.date_fin)

    def test_cascade_delete_formateur_deletes_coursdonne(self):
        CoursDonne.objects.create(
            formateur=self.formateur, promotion=self.promotion,
            cours=self.cursus_cours, date_debut=timezone.now().date()
        )
        self.formateur.delete()
        self.assertEqual(CoursDonne.objects.count(), 0)
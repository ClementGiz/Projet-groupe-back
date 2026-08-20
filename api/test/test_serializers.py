from django.test import TestCase
from django.db.utils import IntegrityError
from django.utils import timezone
from datetime import timedelta

from api.models import Filiere, Cours, Cursus, Promotion
from api.serializers import FiliereSerializer, CoursSerializer, CursusSerializer, PromotionSerializer


class FiliereSerializerTest(TestCase):
    def test_valid_data(self):
        serializer = FiliereSerializer(data={"code": "DEV", "nom": "Développement"})
        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_missing_nom(self):
        serializer = FiliereSerializer(data={"code": "DEV"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("nom", serializer.errors)

    def test_serialized_output(self):
        filiere = Filiere.objects.create(code="DEV", nom="Développement")
        data = FiliereSerializer(filiere).data
        self.assertEqual(data["code"], "DEV")
        self.assertEqual(data["nom"], "Développement")


class CoursSerializerTest(TestCase):
    def test_valid_data_without_duree_uses_model_default(self):
        serializer = CoursSerializer(data={"code": "ALGO", "libelle": "Algorithmique"})
        self.assertTrue(serializer.is_valid(), serializer.errors)
        cours = serializer.save()
        self.assertEqual(cours.duree, 35)

    def test_missing_libelle(self):
        serializer = CoursSerializer(data={"code": "ALGO"})
        self.assertFalse(serializer.is_valid())
        self.assertIn("libelle", serializer.errors)

    def test_custom_duree_is_respected(self):
        serializer = CoursSerializer(data={"code": "WEB", "libelle": "HTML/CSS", "duree": 70})
        self.assertTrue(serializer.is_valid())
        cours = serializer.save()
        self.assertEqual(cours.duree, 70)


class CursusSerializerTest(TestCase):
    def setUp(self):
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")

    def test_filiere_field_is_ignored_on_input(self):
        serializer = CursusSerializer(data={
            "code": "D2WL", "libelle": "Développeur Web", "filiere": self.filiere.id
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("filiere", serializer.validated_data)

    def test_missing_code_and_libelle(self):
        serializer = CursusSerializer(data={"filiere": self.filiere.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn("code", serializer.errors)
        self.assertIn("libelle", serializer.errors)

    def test_serialized_output_contains_nested_filiere(self):
        cursus = Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=self.filiere)
        data = CursusSerializer(cursus).data
        self.assertEqual(data["filiere"]["code"], "DEV")
        self.assertEqual(data["libelle"], "Développeur Web")

    def test_KNOWN_BUG_save_fails_without_filiere(self):
        """
        Documente le bug : filiere est read_only alors qu'il est NOT NULL en base.
        Ce test doit rester rouge tant que le serializer n'expose pas un champ
        writable (ex: filiere_id) comme le fait CoursDonneSerializer.
        """
        serializer = CursusSerializer(data={"code": "D2WL", "libelle": "Développeur Web"})
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(IntegrityError):
            serializer.save()


class PromotionSerializerTest(TestCase):
    def setUp(self):
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.date_debut = timezone.now().date()
        self.date_fin = self.date_debut + timedelta(days=365)

    def test_filiere_field_is_ignored_on_input(self):
        serializer = PromotionSerializer(data={
            "nom": "Promo 2025", "date_debut": self.date_debut, "date_fin": self.date_fin,
            "filiere": self.filiere.id,
        })
        self.assertTrue(serializer.is_valid(), serializer.errors)
        self.assertNotIn("filiere", serializer.validated_data)

    def test_missing_dates(self):
        serializer = PromotionSerializer(data={"nom": "Promo 2025", "filiere": self.filiere.id})
        self.assertFalse(serializer.is_valid())
        self.assertIn("date_debut", serializer.errors)
        self.assertIn("date_fin", serializer.errors)

    def test_KNOWN_BUG_save_fails_without_filiere(self):
        serializer = PromotionSerializer(data={
            "nom": "Promo 2025", "date_debut": self.date_debut, "date_fin": self.date_fin,
        })
        self.assertTrue(serializer.is_valid())
        with self.assertRaises(IntegrityError):
            serializer.save()
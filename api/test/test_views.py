from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework import status
from rest_framework.authtoken.models import Token

from api.models import Filiere, Cours, Cursus, CursusCours, Promotion, User, FormateurProfile, CoursDonne


def make_user(username, role, **kwargs):
    return User.objects.create_user(username=username, password="pass123", role=role, **kwargs)


class LoginViewTest(APITestCase):
    def setUp(self):
        self.user = make_user("jdupont", User.Role.ELEVE)

    def test_login_success_returns_token(self):
        response = self.client.post(reverse("login"), {"username": "jdupont", "password": "pass123"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("token", response.data)
        self.assertEqual(response.data["user"]["username"], "jdupont")

    def test_login_wrong_password(self):
        response = self.client.post(reverse("login"), {"username": "jdupont", "password": "wrong"})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_missing_fields(self):
        response = self.client.post(reverse("login"), {"username": "jdupont"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class MeViewTest(APITestCase):
    def setUp(self):
        self.user = make_user("jdupont", User.Role.ELEVE)

    def test_requires_auth(self):
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_returns_current_user(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(reverse("me"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "jdupont")


class FilieresViewTest(APITestCase):
    def setUp(self):
        self.user = make_user("jdupont", User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")

    def test_list_filieres(self):
        response = self.client.get("/api/filieres/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_create_filiere(self):
        response = self.client.post("/api/filieres/", {"code": "RES", "nom": "Réseaux"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Filiere.objects.count(), 2)

    def test_create_filiere_missing_nom(self):
        response = self.client.post("/api/filieres/", {"code": "RES"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_list_requires_auth(self):
        self.client.force_authenticate(user=None)
        response = self.client.get("/api/filieres/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class FiliereDetailViewTest(APITestCase):

    def setUp(self):
        self.user = make_user("jdupont", User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")

    def test_patch_updates_filiere(self):
        response = self.client.patch(f"/api/filieres/{self.filiere.id}/", {"nom": "Dev Modifié"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.filiere.refresh_from_db()
        self.assertEqual(self.filiere.nom, "Dev Modifié")

    def test_patch_unknown_filiere_returns_404(self):
        response = self.client.patch("/api/filieres/9999/", {"nom": "X"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_get_not_allowed(self):
        response = self.client.get(f"/api/filieres/{self.filiere.id}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_delete_not_allowed(self):
        response = self.client.delete(f"/api/filieres/{self.filiere.id}/")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


class CursusViewTest(APITestCase):
    def setUp(self):
        self.user = make_user("jdupont", User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")

    def test_list_cursus(self):
        Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=self.filiere)
        response = self.client.get("/api/cursus/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_KNOWN_BUG_create_cursus_crashes_because_filiere_is_readonly(self):
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            self.client.post("/api/cursus/", {"code": "D2WL", "libelle": "Développeur Web"})


class PromotionsViewTest(APITestCase):
    def setUp(self):
        self.user = make_user("jdupont", User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.date_debut = timezone.now().date()
        self.date_fin = self.date_debut + timedelta(days=365)

    def test_list_promotions(self):
        Promotion.objects.create(
            filiere=self.filiere, nom="Promo 2025",
            date_debut=self.date_debut, date_fin=self.date_fin
        )
        response = self.client.get("/api/promotions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_KNOWN_BUG_create_promotion_crashes_because_filiere_is_readonly(self):
        from django.db.utils import IntegrityError
        with self.assertRaises(IntegrityError):
            self.client.post("/api/promotions/", {
                "nom": "Promo 2025", "date_debut": self.date_debut, "date_fin": self.date_fin,
            })


class PromotionElevesViewTest(APITestCase):
    def setUp(self):
        self.admin = make_user("admin1", User.Role.ADMIN)
        self.client.force_authenticate(user=self.admin)
        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.promotion = Promotion.objects.create(
            filiere=self.filiere, nom="Promo 2025",
            date_debut=timezone.now().date(),
            date_fin=timezone.now().date() + timedelta(days=365),
        )

    def test_unknown_promotion_returns_404(self):
        response = self.client.get(reverse("promotion-eleves", args=[9999]))
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_empty_promotion_returns_empty_list(self):
        response = self.client.get(reverse("promotion-eleves", args=[self.promotion.id]))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, [])


class CoursDonneViewTest(APITestCase):
    def setUp(self):
        self.user = make_user("jdupont", User.Role.ADMIN)
        self.client.force_authenticate(user=self.user)

        self.filiere = Filiere.objects.create(code="DEV", nom="Développement")
        self.cursus = Cursus.objects.create(code="D2WL", libelle="Développeur Web", filiere=self.filiere)
        self.cours = Cours.objects.create(code="ALGO", libelle="Algorithmique")
        self.cursus_cours = CursusCours.objects.create(cursus=self.cursus, cours=self.cours, ordre=1)
        self.promotion = Promotion.objects.create(
            filiere=self.filiere, nom="Promo 2025",
            date_debut=timezone.now().date(), date_fin=timezone.now().date() + timedelta(days=365),
        )
        formateur_user = make_user("formateur1", User.Role.FORMATEUR)
        self.formateur = FormateurProfile.objects.create(user=formateur_user)

    def test_create_cours_donne(self):
        data = {
            "formateur_id": self.formateur.id,
            "promotion_id": self.promotion.id,
            "cours_id": self.cursus_cours.id,
            "date_debut": timezone.now().date(),
        }
        response = self.client.post("/api/cours-donnes/", data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CoursDonne.objects.count(), 1)

    def test_filter_by_promotion(self):
        CoursDonne.objects.create(
            formateur=self.formateur, promotion=self.promotion,
            cours=self.cursus_cours, date_debut=timezone.now().date(),
        )
        response = self.client.get(f"/api/cours-donnes/?promotion={self.promotion.id}")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_delete_cours_donne(self):
        cd = CoursDonne.objects.create(
            formateur=self.formateur, promotion=self.promotion,
            cours=self.cursus_cours, date_debut=timezone.now().date(),
        )
        response = self.client.delete(f"/api/cours-donnes/{cd.id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


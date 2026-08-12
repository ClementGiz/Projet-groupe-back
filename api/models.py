from django.contrib.auth.models import AbstractUser
from django.db import models

class Filiere(models.Model):
    code = models.CharField(max_length = 5)
    nom = models.CharField(max_length = 50, help_text = 'Ex : Développement, Système et réseaux ...')

    def __str__(self):
        return self.nom

class Cours(models.Model):
    code = models.CharField(max_length = 5)
    libelle = models.CharField(max_length = 50, help_text= 'Ex : Algorithmique / Pseudo-Code, Web Client / HTML & CSS ...')
    duree = models.IntegerField(default = 35)

    def __str__(self):
        return self.libelle

class Cursus(models.Model):
    code = models.CharField(max_length = 5, help_text='Ex : D2WL, CDA, EADL ...')
    libelle = models.CharField(max_length = 50, help_text= 'Ex: Concepteur Développeur d\'Applications')
    filiere = models.ForeignKey(Filiere, on_delete = models.CASCADE)
    cours = models.ManyToManyField(Cours, through = 'CursusCours')

    def __str__(self):
        return f"Le cursus {self.libelle} fait parti de la filière {str(self.filiere)}"

class CursusCours(models.Model):
    cursus = models.ForeignKey(Cursus, on_delete = models.CASCADE)
    cours = models.ForeignKey(Cours, on_delete = models.CASCADE)
    ordre = models.IntegerField(help_text = 'Position du cours dans le cursus')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields = ['cursus', 'cours'], name = 'unique_cursus_cours'),
        ]

class Promotion(models.Model):
    filiere = models.ForeignKey(Filiere, on_delete = models.CASCADE)
    nom = models.CharField(max_length = 50)
    date_debut = models.DateField()
    date_fin = models.DateField()

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrateur'
        REF = 'REF', 'Référente administrative'
        FORMATEUR = 'FORMATEUR', 'Formateur'
        ELEVE = 'ELEVE', 'Elève'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.ELEVE)

    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    @property
    def is_ref(self):
        return self.role == self.Role.REF
    @property
    def is_formateur(self):
        return self.role == self.Role.FORMATEUR
    @property
    def is_eleve(self):
        return self.role == self.Role.ELEVE

class EleveProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)
    promotion = models.ForeignKey(Promotion, on_delete = models.CASCADE)

class FormateurProfile(models.Model):
    user = models.OneToOneField(User, on_delete = models.CASCADE)

class CoursDonne(models.Model):
    formateur = models.ForeignKey(FormateurProfile, on_delete = models.CASCADE)
    cours = models.ForeignKey(CursusCours, on_delete = models.CASCADE)
    date_debut = models.DateField()
    date_fin = models.DateField(null=True)
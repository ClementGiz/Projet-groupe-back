from rest_framework import serializers
from .models import (
    Filiere, Cours, Cursus, CursusCours, Promotion,
    User, EleveProfile, FormateurProfile, CoursDonne
)

# 1. Serializers de base
class FiliereSerializer(serializers.ModelSerializer):
    class Meta:
        model = Filiere
        fields = '__all__'

class CoursSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cours
        fields = '__all__'

class CursusCoursSerializer(serializers.ModelSerializer):
    cours = CoursSerializer(read_only=True)
    class Meta:
        model = CursusCours
        fields = '__all__'

class CursusSerializer(serializers.ModelSerializer):
    filiere = FiliereSerializer(read_only=True)
    cursus_cours = CursusCoursSerializer(many=True, read_only=True)
    class Meta:
        model = Cursus
        fields = '__all__'

class PromotionSerializer(serializers.ModelSerializer):
    filiere = FiliereSerializer(read_only=True)
    class Meta:
        model = Promotion
        fields = '__all__'

# 2. Utilisateurs et Profils
class EleveProfileSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)
    class Meta:
        model = EleveProfile
        fields = '__all__'

class FormateurProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormateurProfile
        fields = '__all__'

class UserSerializer(serializers.ModelSerializer):
    eleve_profile = EleveProfileSerializer(read_only=True)
    formateur_profile = FormateurProfileSerializer(read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'eleve_profile', 'formateur_profile']

    # Cette méthode permet d'enregistrer proprement les modification de l'utilsateur en BDD

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        # Met ) jour les champs dynamiquement

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Méthode set_password hache le mot de passe. Si le champ est laissé vide par utilsateur,password vaut None

        if password:
            instance.set_password(password)

        instance.save()
        return instance

class CoursDonneSerializer(serializers.ModelSerializer):
    formateur = FormateurProfileSerializer(read_only=True)
    promotion = PromotionSerializer(read_only=True)
    cours = CursusCoursSerializer(read_only=True)
    class Meta:
        model = CoursDonne
        fields = '__all__'
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

class EleveSerializer(serializers.ModelSerializer):
    eleve_profile = EleveProfileSerializer(read_only=True)

    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(),
        source='eleve_profile.promotion',
        write_only=True
    )

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'eleve_profile',
            'promotion_id',
        ]

        read_only_fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'eleve_profile',
        ]

class LoginUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
        ]


class AdminUserManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'role',
            'password',
            'is_active',
        ]

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create_user(**validated_data)

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save()

        if user.role == User.Role.ELEVE:
            try:
                promo_attente = Promotion.objects.get(pk=21)
            except Promotion.DoesNotExist:
                promo_attente = Promotion.objects.first()

            if promo_attente:
                EleveProfile.objects.create(user=user, promotion=promo_attente)

        if user.role == User.Role.FORMATEUR:
            FormateurProfile.objects.get_or_create(user=user)

        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)

        instance.save()
        return instance
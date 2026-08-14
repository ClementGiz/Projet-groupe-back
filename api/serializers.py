from rest_framework import serializers
from .models import (
    Filiere, Cours, Cursus, CursusCours, Promotion,
    User, EleveProfile, FormateurProfile, CoursDonne
)


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
    filiere_id = serializers.PrimaryKeyRelatedField(
        queryset=Filiere.objects.all(), source='filiere', write_only=True
    )
    cursus_cours = CursusCoursSerializer(many=True, read_only=True)

    class Meta:
        model = Cursus
        fields = '__all__'


class PromotionSerializer(serializers.ModelSerializer):
    filiere = FiliereSerializer(read_only=True)
    filiere_id = serializers.PrimaryKeyRelatedField(
        queryset=Filiere.objects.all(), source='filiere', write_only=True
    )

    class Meta:
        model = Promotion
        fields = '__all__'


class EleveProfileSerializer(serializers.ModelSerializer):
    promotion = PromotionSerializer(read_only=True)

    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(),
        source='promotion',
        write_only=True
    )

    class Meta:
        model = EleveProfile

        fields = [
            'id',
            'user',
            'promotion',
            'promotion_id',
        ]

        read_only_fields = [
            'id',
            'user',
            'promotion',
        ]


class FormateurProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FormateurProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    eleve_profile = EleveProfileSerializer(read_only=True)
    formateur_profile = FormateurProfileSerializer(read_only=True)

    class Meta:
        model = User

        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'eleve_profile',
            'formateur_profile',
        ]

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
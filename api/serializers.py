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

    # Cette méthode permet d'enregistrer proprement les modifications de l'utilisateur en BDD
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        # Met à jour les champs dynamiquement
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        # set_password hache le mot de passe. Si le champ est laissé vide, password vaut None
        if password:
            instance.set_password(password)
        instance.save()
        return instance


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


# 3. Élèves (lecture imbriquée + écriture par id)

class EleveSerializer(serializers.ModelSerializer):
    eleve_profile = EleveProfileSerializer(read_only=True)
    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(),
        source='eleve_profile.promotion',
        write_only=True,
        required=False,
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

    def update(self, instance, validated_data):
        # DRF empile ici {'eleve_profile': {'promotion': <Promotion>}} à cause du
        # source='eleve_profile.promotion' -> il faut le dépiler manuellement.
        eleve_profile_data = validated_data.pop('eleve_profile', None)
        if eleve_profile_data and 'promotion' in eleve_profile_data:
            profile = instance.eleve_profile
            profile.promotion = eleve_profile_data['promotion']
            profile.save()
        return instance


# 4. Administration des utilisateurs

class AdminUserManagementSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'first_name',
            'last_name',
            'email',
            'role',
            'is_active',
            'date_joined',
            'password',
        ]
        read_only_fields = ['id', 'date_joined']

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User(**validated_data)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


# 5. Planning (CoursDonne) — lecture imbriquée + écriture par id

class CoursDonneSerializer(serializers.ModelSerializer):
    formateur = FormateurProfileSerializer(read_only=True)
    promotion = PromotionSerializer(read_only=True)
    cours = CursusCoursSerializer(read_only=True)

    formateur_id = serializers.PrimaryKeyRelatedField(
        queryset=FormateurProfile.objects.all(),
        source='formateur',
        write_only=True,
    )
    promotion_id = serializers.PrimaryKeyRelatedField(
        queryset=Promotion.objects.all(),
        source='promotion',
        write_only=True,
    )
    cours_id = serializers.PrimaryKeyRelatedField(
        queryset=CursusCours.objects.all(),
        source='cours',
        write_only=True,
    )

    class Meta:
        model = CoursDonne
        fields = '__all__'
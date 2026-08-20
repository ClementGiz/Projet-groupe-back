from datetime import date
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
    class Meta:
        model = EleveProfile
        fields = '__all__'

class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name','email']

class FormateurProfileSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(serializers.ModelSerializer)
    class Meta:
        model = FormateurProfile
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    eleve_profile = EleveProfileSerializer(read_only=True)
    formateur_profile = FormateurProfileSerializer(read_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'role', 'eleve_profile', 'formateur_profile', 'password']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password and password.strip():
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

class SimpleEleveSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'email']


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
        eleve_profile_data = validated_data.pop('eleve_profile', None)
        if eleve_profile_data and 'promotion' in eleve_profile_data:
            profile = instance.eleve_profile
            profile.promotion = eleve_profile_data['promotion']
            profile.save()
        return instance


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

class FormateurCourseSerializer(serializers.ModelSerializer):
    promotion_id = serializers.IntegerField(source='promotion.id', read_only=True)
    code_cours = serializers.CharField(source='cours.cours.code', read_only=True)
    libelle = serializers.CharField(source='cours.cours.libelle', read_only=True)
    duree = serializers.IntegerField(source='cours.cours.duree', read_only=True)
    promotion_nom = serializers.CharField(source='promotion.nom', read_only=True)
    filiere_code = serializers.CharField(source='promotion.filiere.code', read_only=True)
    statut = serializers.SerializerMethodField()

    class Meta:
        model = CoursDonne
        fields = [
            'id',
            'promotion_id',
            'code_cours',
            'libelle',
            'duree',
            'promotion_nom',
            'filiere_code',
            'date_debut',
            'date_fin',
            'statut',
        ]

    def get_statut(self, obj):
        today = date.today()
        if obj.date_fin and obj.date_fin < today:
            return 'termine'
        elif obj.date_debut <= today and (not obj.date_fin or obj.date_fin >= today):
            return 'en_cours'
        elif obj.date_debut > today:
            return 'a_venir'
        return 'a_venir'
import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from . import serializers
from .models import Filiere, Cours, Cursus, Promotion, User, CoursDonne
from .serializers import (
    FiliereSerializer, CoursSerializer, CursusSerializer,
    PromotionSerializer, UserSerializer, CoursDonneSerializer
)

class DumpAllDataView(APIView):
    """
    Route de TEST : Renvoie TOUTES les données de la base de données.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        data = {
            "filieres": FiliereSerializer(Filiere.objects.all(), many=True).data,
            "cours": CoursSerializer(Cours.objects.all(), many=True).data,
            "cursus": CursusSerializer(Cursus.objects.all(), many=True).data,
            "promotions": PromotionSerializer(Promotion.objects.all(), many=True).data,
            "users": UserSerializer(User.objects.all(), many=True).data,
            "cours_donnes": CoursDonneSerializer(CoursDonne.objects.all(), many=True).data,
        }
        return Response(data)

class UserProfileView(APIView):
    """
    Gestion du profil de l'utlisateur actuellement conncecté
    """
    permission_classes = [IsAuthenticated]

    # GET /api/profile/me/ -> Récupère les données de l'utilsateur connecté
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # PATCH /api/profile/me/ -> Mettre à jour partiellement le profil

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
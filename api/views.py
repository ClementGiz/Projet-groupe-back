from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

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
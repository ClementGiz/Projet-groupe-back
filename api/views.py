from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated

from .models import Filiere, Cours, Cursus, Promotion, User, CoursDonne
from .serializers import (
    FiliereSerializer, CoursSerializer, CursusSerializer,
    PromotionSerializer, UserSerializer, CoursDonneSerializer, EleveSerializer, LoginUserSerializer
)

class DumpAllDataView(APIView):
    """
    Route de TEST : Renvoie TOUTES les données de la base de données.
    """
    permission_classes = [IsAuthenticated]

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


class LoginView(APIView):

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {
                    "message": "Username et password sont obligatoires."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:
            return Response(
                {
                    "message": "Identifiants incorrects."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, created = Token.objects.get_or_create(user=user)

        user_serializer = LoginUserSerializer(user)

        return Response(
            {
                "message": "Connexion réussie.",
                "token": token.key,
                "user": user_serializer.data
            },
            status=status.HTTP_200_OK
        )

class MeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        serializer = UserSerializer(request.user)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

class ElevesView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        eleves = User.objects.filter(
            role=User.Role.ELEVE
        ).select_related(
            'eleve_profile',
            'eleve_profile__promotion',
            'eleve_profile__promotion__filiere'
        )

        serializer = EleveSerializer(
            eleves,
            many=True
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )


class EleveDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get_object(self, pk):

        try:
            return User.objects.select_related(
                'eleve_profile',
                'eleve_profile__promotion',
                'eleve_profile__promotion__filiere'
            ).get(
                pk=pk,
                role=User.Role.ELEVE
            )

        except User.DoesNotExist:
            return None

    def get(self, request, pk):

        eleve = self.get_object(pk)

        if eleve is None:
            return Response(
                {
                    "message": "Élève introuvable."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EleveSerializer(eleve)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def patch(self, request, pk):

        eleve = self.get_object(pk)

        if eleve is None:
            return Response(
                {
                    "message": "Élève introuvable."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = EleveSerializer(
            eleve,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save()

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )
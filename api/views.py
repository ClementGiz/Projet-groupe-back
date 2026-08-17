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

            promotion_id = request.query_params.get('promotion')
            if promotion_id:
                eleves = eleves.filter(eleve_profile__promotion_id=promotion_id)

            serializer = EleveSerializer(
                eleves,
                many=True
            )

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

class FilieresView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        filieres = Filiere.objects.all()
        return Response(FiliereSerializer(filieres, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = FiliereSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FiliereDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Filiere.objects.get(pk=pk)
        except Filiere.DoesNotExist:
            return None

    def patch(self, request, pk):
        filiere = self.get_object(pk)
        if filiere is None:
            return Response({"message": "Filière introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = FiliereSerializer(filiere, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CursusView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cursus = Cursus.objects.select_related('filiere')
        return Response(CursusSerializer(cursus, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = CursusSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CursusDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Cursus.objects.get(pk=pk)
        except Cursus.DoesNotExist:
            return None

    def patch(self, request, pk):
        cursus = self.get_object(pk)
        if cursus is None:
            return Response({"message": "Cursus introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = CursusSerializer(cursus, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PromotionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        promotions = Promotion.objects.select_related('filiere')
        return Response(PromotionSerializer(promotions, many=True).data, status=status.HTTP_200_OK)

    def post(self, request):
        serializer = PromotionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PromotionDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk):
        try:
            return Promotion.objects.get(pk=pk)
        except Promotion.DoesNotExist:
            return None

    def patch(self, request, pk):
        promotion = self.get_object(pk)
        if promotion is None:
            return Response({"message": "Promotion introuvable."}, status=status.HTTP_404_NOT_FOUND)
        serializer = PromotionSerializer(promotion, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
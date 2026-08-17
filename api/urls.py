from django.urls import path

from api.models import Cursus
from api.views import LoginView, MeView, DumpAllDataView, ElevesView, EleveDetailView, FilieresView, FiliereDetailView, \
    CursusView, CursusDetailView, PromotionsView, PromotionDetailView, UserProfileView, PlanningView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me", MeView.as_view(), name="me"),
    path('test-dump/', DumpAllDataView.as_view(), name='test-dump'),
    path('eleves/', ElevesView.as_view(), name='eleves'),
    path('eleves/<int:pk>/', EleveDetailView.as_view(), name='eleve-detail'),
    path('filieres/', FilieresView.as_view()),
    path('filieres/<int:pk>/', FiliereDetailView.as_view()),
    path('cursus/', CursusView.as_view()),
    path('cursus/<int:pk>/', CursusDetailView.as_view()),
    path('promotions/', PromotionsView.as_view()),
    path('profile/me/', UserProfileView.as_view(), name='profile'),
    path('promotions/<int:pk>/', PromotionDetailView.as_view()),
    path('planning/me/', PlanningView.as_view(), name='my_planning')
]
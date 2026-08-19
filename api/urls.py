from django.urls import path

from api.views import (LoginView, MeView, DumpAllDataView, ElevesView, EleveDetailView,
                       FilieresView, FiliereDetailView, CursusView, CursusDetailView, PromotionsView,
                       PromotionDetailView, UserProfileView, AdminUsersView, AdminUserDetailView,
                       FormateurCoursesMeView, CoursDonneView, CoursDonneDetailView, FormateursView,
                       PromotionElevesView, PlanningView )

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
    path('profile/me/', UserProfileView.as_view(), name='profile-me'),
    path('promotions/<int:pk>/', PromotionDetailView.as_view()),
    path('promotions/<int:pk>/eleves/', PromotionElevesView.as_view(), name='promotion-eleves'),
    path('admin/users/', AdminUsersView.as_view(), name='admin-users'),
    path('admin/users/<int:pk>/', AdminUserDetailView.as_view(), name='admin-user-detail'),
    path('cours-donnes/', CoursDonneView.as_view(), name='cours-donnes'),
    path('cours-donnes/<int:pk>/', CoursDonneDetailView.as_view(), name='cours-donne-detail'),
    path('formateurs/', FormateursView.as_view(), name='formateurs'),
    path('formateur/courses/me/', FormateurCoursesMeView.as_view(), name='formateur-courses-me'),
    path('planning/me/', PlanningView.as_view(), name='planing-me'),
]
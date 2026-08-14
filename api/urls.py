from django.urls import path
from api.views import LoginView, MeView, DumpAllDataView, ElevesView, EleveDetailView

urlpatterns = [
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/me", MeView.as_view(), name="me"),

    path('test-dump/', DumpAllDataView.as_view(), name='test-dump'),

    path('eleves/', ElevesView.as_view(), name='eleves'),
    path('eleves/<int:pk>/', EleveDetailView.as_view(), name='eleve-detail'),
]
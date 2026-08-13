from os import name

from django.urls import path

from projet_full_stack_back.urls import urlpatterns
from .views import DumpAllDataView, UserProfileView

urlpatterns = [
    path('dump-data', DumpAllDataView.as_view(), name='dump-data'),
    path('profile/me/', UserProfileView.as_view(), name='profile-me'), # Route profil
]
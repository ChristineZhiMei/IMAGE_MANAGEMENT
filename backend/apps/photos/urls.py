from django.urls import path

from apps.photos.views import PhotoMainView

urlpatterns = [
    path('photos/', PhotoMainView.as_view()),
]
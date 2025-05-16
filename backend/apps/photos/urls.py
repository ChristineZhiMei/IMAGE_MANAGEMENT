from django.urls import path

from apps.photos.views import PhotoMainView,ClassifyView

urlpatterns = [
    path('photos/', PhotoMainView.as_view()),
    path('addLabels/',ClassifyView.as_view())
]
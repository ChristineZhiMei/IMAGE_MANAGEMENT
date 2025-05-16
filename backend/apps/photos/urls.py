from django.urls import path

# noinspection PyUnresolvedReferences
from apps.photos.views import PhotoMainView,ClassifyView,DeleteView

urlpatterns = [
    path('photos/', PhotoMainView.as_view()),
    path('addLabels/',ClassifyView.as_view()),
    path('delete/', DeleteView.as_view())
]
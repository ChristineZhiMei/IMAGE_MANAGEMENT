from django.urls import path

# noinspection PyUnresolvedReferences
from apps.photos.views import PhotoMainView,ClassifyView,DeleteView,CopyMovingView,FormatConvertView,RenameView

urlpatterns = [
    path('photos/', PhotoMainView.as_view()),
    path('addLabels/',ClassifyView.as_view()),
    path('delete/', DeleteView.as_view()),
    path('move/',CopyMovingView.as_view()),
    path('copy/',CopyMovingView.as_view()),
    path('format/',FormatConvertView.as_view()),
    path('rename/',RenameView.as_view())
]
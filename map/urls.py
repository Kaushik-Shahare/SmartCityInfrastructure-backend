from django.urls import path
from .views import *

urlpatterns = [
    path('matrix/', MatrixMapView.as_view()),
    path('matrix/<int:pk>/', MatrixMapDetailedView.as_view()),
    path('points/<int:map_id>/', PointView.as_view()),
    path('points/<int:map_id>/<int:pk>/', PointDetailedView.as_view()),
    
    path('points/<map_id>/<int:x>/<int:y>/', PointByCoordinatesView.as_view()),
    path('points/<map_id>/represents/<represents>/', PointByTypeView.as_view()),
    path('pathfinding/', ShortestRoadPathView.as_view()),
]
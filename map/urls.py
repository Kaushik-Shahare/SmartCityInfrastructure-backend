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
    path('canvas/', CanvasDataView.as_view()),
]

urlpatterns += [
    path('render-map/', render_map, name='render_map'),
    path('matrix/<int:map_id>/view/', map_html_view, name='map_html_view'),
    path('smart-city/', smart_city_view, name='smart_city'),
    path('smart-city/<int:map_id>/', smart_city_view, name='smart_city_with_map'),
]
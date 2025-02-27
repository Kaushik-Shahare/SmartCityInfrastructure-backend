from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
from .utils.pathfinding import dijkstra, find_next_closest_road

def validate_coordinates(matrix, x, y):
    # Assumes matrix has attributes 'max_x' and 'max_y'
    return 0 <= x <= matrix.X and 0 <= y <= matrix.Y

# Create your views here.

class MatrixMapView(APIView):

    def get(self, request):
        matrix = MatrixMap.objects.all()
        serializer = MatrixMapSerializer(matrix, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = MatrixMapSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MatrixMapDetailedView(APIView):
    
    def get(self, request, pk):
        matrix = MatrixMap.objects.get(pk=pk)
        serializer = MatrixMapSerializer(matrix)
        return Response(serializer.data)

    def put(self, request, pk):
        matrix = MatrixMap.objects.get(pk=pk)
        serializer = MatrixMapSerializer(matrix, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        matrix = MatrixMap.objects.get(pk=pk)
        matrix.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PointView(APIView):
    
    def get(self, request, map_id):
        points = Point.objects.filter(matrix=map_id)
        serializer = PointSerializer(points, many=True)
        return Response(serializer.data)

    def post(self, request, map_id):
        matrix = MatrixMap.objects.get(pk=map_id)
        x = int(request.data.get('x', -1))
        y = int(request.data.get('y', -1))
        if not validate_coordinates(matrix, x, y):
            return Response({'error': 'Coordinates out of range'}, status=status.HTTP_400_BAD_REQUEST)
        request.data['matrix'] = map_id
        serializer = PointSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class PointDetailedView(APIView):
    
    def get(self, request, map_id, pk):
        point = Point.objects.get(pk=pk)
        serializer = PointSerializer(point)
        return Response(serializer.data)

    def put(self, request, map_id, pk):
        matrix = MatrixMap.objects.get(pk=map_id)
        point = Point.objects.get(pk=pk)
        represents = request.data.get('represents', point.represents)
        data = {
            'matrix': map_id,
            'x': point.x,
            'y': point.y,   
            'represents': represents
        }
        serializer = PointSerializer(point, data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, map_id, pk):
        point = Point.objects.get(pk=pk)
        point.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    

class PointByCoordinatesView(APIView):
    
    def get(self, request, map_id, x, y):
        point = Point.objects.get(matrix=map_id, x=x, y=y)
        serializer = PointSerializer(point)
        return Response(serializer.data)
    
    def put(self, request, map_id, x, y):
        matrix = MatrixMap.objects.get(pk=map_id)
        new_x = int(request.data.get('x', x))
        new_y = int(request.data.get('y', y))
        if not validate_coordinates(matrix, new_x, new_y):
            return Response({'error': 'Coordinates out of range'}, status=status.HTTP_400_BAD_REQUEST)
        point = Point.objects.get(matrix=map_id, x=x, y=y)
        serializer = PointSerializer(point, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, map_id, x, y):
        point = Point.objects.get(matrix=map_id, x=x, y=y)
        point.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    
class PointByTypeView(APIView):
    
    def get(self, request, map_id, represents):
        points = Point.objects.filter(matrix=map_id, represents=represents)
        serializer = PointSerializer(points, many=True)
        return Response(serializer.data)

class ShortestRoadPathView(APIView):
    def post(self, request):
        try:
            map_id = request.data.get('map_id')
            start_x = int(request.data.get('start_x'))
            start_y = int(request.data.get('start_y'))
            end_x = int(request.data.get('end_x'))
            end_y = int(request.data.get('end_y'))
        except (TypeError, ValueError):
            return Response({'error': 'Invalid input'}, status=400)
            
        matrix = MatrixMap.objects.get(pk=map_id)
        start = (start_x, start_y)
        end = (end_x, end_y)
        path = dijkstra(matrix, start, end)
        if path is None:
            path = find_next_closest_road(matrix, start, end, algorithm='dijkstra')
        if path is None:
            return Response({'error': 'No path found'}, status=400)
        return Response({'path': path})

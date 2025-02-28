from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializers import *
# Update this import to include a_star function
from .utils.pathfinding import dijkstra, a_star, find_next_closest_road

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
        try:
            # Get existing point
            point = Point.objects.get(matrix=map_id, x=x, y=y)
            
            # Update represents field
            represents = request.data.get('represents')
            if represents:
                point.represents = represents
                point.save()
                
                # Verify save was successful
                updated_point = Point.objects.get(pk=point.pk)
                
                return Response({
                    'success': True,
                    'id': point.id,
                    'x': x,
                    'y': y,
                    'represents': updated_point.represents,
                })
            else:
                return Response({'error': 'No represents value provided'}, status=status.HTTP_400_BAD_REQUEST)
        except Point.DoesNotExist:
            return Response({'error': f'Point at ({x},{y}) not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
            algorithm = request.data.get('algorithm', 'dijkstra')  # Default to Dijkstra
            
        except (TypeError, ValueError):
            return Response({'error': 'Invalid input'}, status=400)
            
        matrix = MatrixMap.objects.get(pk=map_id)
        start = (start_x, start_y)
        end = (end_x, end_y)
        
        # Check if start and end are roads
        road_set = set((p.x, p.y) for p in matrix.points.filter(represents='road'))
        if start not in road_set:
            return Response({'error': 'Start point is not a road'}, status=400)
        if end not in road_set:
            return Response({'error': 'End point is not a road'}, status=400)
        
        import time
        start_time = time.time()
        
        # Track visited nodes for visualization
        explored_nodes = []
        
        # Run the appropriate algorithm
        if algorithm == 'astar':
            path = a_star(matrix, start, end, explored_nodes=explored_nodes)
        else:
            path = dijkstra(matrix, start, end, explored_nodes=explored_nodes)
        
        execution_time = (time.time() - start_time) * 1000  # in milliseconds
        
        if path is None:
            if algorithm == 'astar':
                path = find_next_closest_road(matrix, start, end, algorithm='astar', explored_nodes=explored_nodes)
            else:
                path = find_next_closest_road(matrix, start, end, algorithm='dijkstra', explored_nodes=explored_nodes)
        
        if path is None:
            return Response({'error': 'No path found between the selected points'}, status=400)
        
        return Response({
            'path': path,
            'explored': explored_nodes,
            'execution_time': execution_time,
            'algorithm': algorithm
        })

class CanvasDataView(APIView):
    def get(self, request):
        matrix_id = request.query_params.get('matrix_id')
        if not matrix_id:
            return Response({'error': 'matrix_id required'}, status=400)
        try:
            matrix = MatrixMap.objects.get(pk=matrix_id)
        except MatrixMap.DoesNotExist:
            return Response({'error': 'Matrix not found'}, status=404)
        
        # Create a dictionary for quick point lookup
        points_dict = {}
        for point in matrix.points.all():
            points_dict[f"{point.x},{point.y}"] = point
        
        # Build grid with consistent coordinate system
        grid = []
        for y in range(matrix.Y):  # Note: Switched from x to y as outer loop
            row = []
            for x in range(matrix.X):  # Note: Switched from y to x as inner loop
                key = f"{x},{y}"
                if key in points_dict:
                    point = points_dict[key]
                    row.append({'x': point.x, 'y': point.y, 'represents': point.represents})
                else:
                    row.append({'x': x, 'y': y, 'represents': 'other'})
            grid.append(row)
        
        return Response({'grid': grid})

def render_map(request):
    return render(request, 'map.html')

def map_html_view(request, map_id):
    from django.template.defaulttags import register
    
    matrix = get_object_or_404(MatrixMap, pk=map_id)
    points = Point.objects.filter(matrix=map_id)
    
    # Create a dictionary of points by coordinates for easy lookup in the template
    points_dict = {}
    for point in points:
        key = f"{point.x}-{point.y}"
        points_dict[key] = point.represents
    
    # Debug: check how many non-default points we have
    non_default = len([p for p in points if p.represents != 'other'])
    
    # Generate ranges for the grid
    x_range = range(matrix.X)
    y_range = range(matrix.Y)
    
    context = {
        'matrix': matrix,
        'points_dict': points_dict,
        'x_range': x_range,
        'y_range': y_range,
    }
    
    return render(request, 'map/map.html', context)

def smart_city_view(request, map_id=None):
    # We'll pass map_id but actually use AJAX to load the data
    context = {}
    if map_id:
        context['map_id'] = map_id
    
    return render(request, 'map/smart_city_canvas.html', context)

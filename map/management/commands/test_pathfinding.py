from django.core.management.base import BaseCommand
from map.models import MatrixMap, Point
from map.utils.pathfinding import dijkstra, a_star

class Command(BaseCommand):
    help = 'Test pathfinding algorithms between two points'
    
    def add_arguments(self, parser):
        parser.add_argument('--map-id', type=int, required=True, help='Matrix Map ID')
        parser.add_argument('--start-x', type=int, required=True, help='Start X coordinate')
        parser.add_argument('--start-y', type=int, required=True, help='Start Y coordinate')
        parser.add_argument('--end-x', type=int, required=True, help='End X coordinate')
        parser.add_argument('--end-y', type=int, required=True, help='End Y coordinate')
    
    def handle(self, *args, **options):
        map_id = options['map_id']
        start_x = options['start_x']
        start_y = options['start_y']
        end_x = options['end_x']
        end_y = options['end_y']
        
        try:
            matrix = MatrixMap.objects.get(pk=map_id)
        except MatrixMap.DoesNotExist:
            self.stderr.write(self.style.ERROR(f"Matrix with ID {map_id} not found"))
            return
            
        start = (start_x, start_y)
        end = (end_x, end_y)
        
        # Check if start and end are roads
        road_set = set((p.x, p.y) for p in matrix.points.filter(represents='road'))
        self.stdout.write(f"Found {len(road_set)} road cells in matrix")
        
        if start not in road_set:
            self.stdout.write(self.style.ERROR(f"Start point {start} is not a road"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Start point {start} is a road"))
        
        if end not in road_set:
            self.stdout.write(self.style.ERROR(f"End point {end} is not a road"))
        else:
            self.stdout.write(self.style.SUCCESS(f"End point {end} is a road"))
        
        # Test Dijkstra
        self.stdout.write(self.style.NOTICE("Testing Dijkstra..."))
        explored_dijkstra = []
        path_dijkstra = dijkstra(matrix, start, end, explored_nodes=explored_dijkstra)
        
        if path_dijkstra is None:
            self.stdout.write(self.style.ERROR(f"No Dijkstra path found between {start} and {end}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"Dijkstra path found: {path_dijkstra}"))
            self.stdout.write(f"Path length: {len(path_dijkstra)}")
            self.stdout.write(f"Nodes explored: {len(explored_dijkstra)}")
        
        # Test A*
        self.stdout.write(self.style.NOTICE("\nTesting A*..."))
        explored_astar = []
        path_astar = a_star(matrix, start, end, explored_nodes=explored_astar)
        
        if path_astar is None:
            self.stdout.write(self.style.ERROR(f"No A* path found between {start} and {end}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"A* path found: {path_astar}"))
            self.stdout.write(f"Path length: {len(path_astar)}")
            self.stdout.write(f"Nodes explored: {len(explored_astar)}")

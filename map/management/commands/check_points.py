from django.core.management.base import BaseCommand
from map.models import MatrixMap, Point

class Command(BaseCommand):
    help = 'Check and update points in the database'
    
    def add_arguments(self, parser):
        parser.add_argument('--map-id', type=int, help='Matrix Map ID to check')
        parser.add_argument('--update', action='store_true', help='Update some points as a test')
    
    def handle(self, *args, **options):
        map_id = options.get('map_id')
        update = options.get('update', False)
        
        # Get all matrix maps if no specific ID
        if map_id:
            matrices = MatrixMap.objects.filter(pk=map_id)
        else:
            matrices = MatrixMap.objects.all()
        
        self.stdout.write(f"Found {matrices.count()} matrices")
        
        for matrix in matrices:
            self.stdout.write(f"Matrix {matrix.id}: {matrix.name} ({matrix.X}x{matrix.Y})")
            
            points = Point.objects.filter(matrix=matrix)
            road_count = points.filter(represents='road').count()
            building_count = points.filter(represents='building').count()
            park_count = points.filter(represents='park').count()
            water_count = points.filter(represents='water').count()
            other_count = points.filter(represents='other').count()
            
            self.stdout.write(f"  - Total points: {points.count()}")
            self.stdout.write(f"  - Road: {road_count}")
            self.stdout.write(f"  - Building: {building_count}")
            self.stdout.write(f"  - Park: {park_count}")
            self.stdout.write(f"  - Water: {water_count}")
            self.stdout.write(f"  - Other: {other_count}")
            
            if update:
                # Update a few points as a test
                point1 = points.filter(x=0, y=0).first()
                if point1:
                    old_val = point1.represents
                    point1.represents = 'road'
                    point1.save()
                    self.stdout.write(f"  - Updated point (0,0) from '{old_val}' to 'road'")
                
                point2 = points.filter(x=1, y=1).first()
                if point2:
                    old_val = point2.represents
                    point2.represents = 'building'
                    point2.save()
                    self.stdout.write(f"  - Updated point (1,1) from '{old_val}' to 'building'")
                
                # Verify the updates
                p1 = Point.objects.get(matrix=matrix, x=0, y=0)
                p2 = Point.objects.get(matrix=matrix, x=1, y=1)
                self.stdout.write(f"  - Verification: point (0,0) is now '{p1.represents}'")
                self.stdout.write(f"  - Verification: point (1,1) is now '{p2.represents}'")

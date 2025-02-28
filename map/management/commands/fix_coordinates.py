from django.core.management.base import BaseCommand
from map.models import MatrixMap, Point

class Command(BaseCommand):
    help = 'Diagnose and fix coordinate mapping issues in the database'
    
    def add_arguments(self, parser):
        parser.add_argument('--map-id', type=int, help='Matrix Map ID to check/fix')
        parser.add_argument('--fix', action='store_true', help='Apply fixes to the database')
        parser.add_argument('--flip', action='store_true', help='Flip x and y coordinates if needed')
    
    def handle(self, *args, **options):
        map_id = options.get('map_id')
        fix_mode = options.get('fix', False)
        flip_mode = options.get('flip', False)
        
        # Get all matrix maps if no specific ID
        if map_id:
            matrices = MatrixMap.objects.filter(pk=map_id)
        else:
            matrices = MatrixMap.objects.all()
        
        self.stdout.write(f"Found {matrices.count()} matrices")
        
        for matrix in matrices:
            self.stdout.write(f"\nMatrix {matrix.id}: {matrix.name} ({matrix.X}x{matrix.Y})")
            
            # Analyze the data
            points = Point.objects.filter(matrix=matrix)
            coords = [(p.x, p.y) for p in points]
            
            # Find max x and y in the data
            max_x = max([x for x, _ in coords]) if coords else 0
            max_y = max([y for _, y in coords]) if coords else 0
            
            # Check if there are points outside of the matrix dimensions
            out_of_bounds = [p for p in points if p.x >= matrix.X or p.y >= matrix.Y]
            
            self.stdout.write(f"  - Total points: {points.count()}")
            self.stdout.write(f"  - Matrix dimensions: {matrix.X}x{matrix.Y}")
            self.stdout.write(f"  - Max coords in data: ({max_x}, {max_y})")
            self.stdout.write(f"  - Points outside matrix bounds: {len(out_of_bounds)}")
            
            # Check if the matrix dimensions might need to be swapped
            if max_x > matrix.X - 1 or max_y > matrix.Y - 1:
                self.stdout.write(self.style.WARNING("  - Matrix dimensions may be incorrect"))
                if fix_mode:
                    matrix.X = max(matrix.X, max_x + 1)
                    matrix.Y = max(matrix.Y, max_y + 1)
                    matrix.save()
                    self.stdout.write(self.style.SUCCESS(f"  - Updated matrix dimensions to {matrix.X}x{matrix.Y}"))
            
            # Flip x and y coordinates if requested
            if flip_mode:
                count = 0
                for point in points:
                    old_x, old_y = point.x, point.y
                    point.x, point.y = old_y, old_x  # Flip coordinates
                    point.save()
                    count += 1
                    
                self.stdout.write(self.style.SUCCESS(f"  - Flipped coordinates for {count} points"))
            
            # Display a summary of point types
            road_count = points.filter(represents='road').count()
            building_count = points.filter(represents='building').count()
            park_count = points.filter(represents='park').count()
            water_count = points.filter(represents='water').count()
            other_count = points.filter(represents='other').count()
            
            self.stdout.write(f"  - Roads: {road_count}")
            self.stdout.write(f"  - Buildings: {building_count}")
            self.stdout.write(f"  - Parks: {park_count}")
            self.stdout.write(f"  - Water: {water_count}")
            self.stdout.write(f"  - Other: {other_count}")

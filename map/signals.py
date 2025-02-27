from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import MatrixMap, Point

@receiver(post_save, sender=MatrixMap)
def create_matrix_points(sender, instance, created, **kwargs):
    if created:
        print("DEBUG: MatrixMap created, initializing points...")  # Debug statement
        points_bulk = []
        for x in range(instance.X):
            for y in range(instance.Y):
                points_bulk.append(Point(matrix=instance, x=x, y=y))
        Point.objects.bulk_create(points_bulk)
        print("DEBUG: Points created:", len(points_bulk))

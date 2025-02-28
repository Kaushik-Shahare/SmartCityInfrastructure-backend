from django.db import models

# Create your models here.


class MatrixMap(models.Model):
    name = models.CharField(max_length=100)
    X = models.IntegerField() # X is the number of rows
    Y = models.IntegerField() # Y is the number of columns
    distancePerUnit = models.FloatField() # distancePerUnit is the distance between two points in the map
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

represents_choice = [
    ('road', 'Road'),
    ('building', 'Building'),
    ('park', 'Park'),
    ('water', 'Water'),
    ('other', 'Other')
]

class Point(models.Model):
    matrix = models.ForeignKey(MatrixMap, on_delete=models.CASCADE, related_name="points")
    x = models.IntegerField()
    y = models.IntegerField()
    represents = models.CharField(max_length=10, choices=represents_choice, default='other')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"Point ({self.x}, {self.y})"
    
    def save(self, *args, **kwargs):
        if self.represents not in [choice[0] for choice in represents_choice]:
            print(f"WARNING: Invalid represents value: '{self.represents}', defaulting to 'other'")
            self.represents = 'other'
        super().save(*args, **kwargs)
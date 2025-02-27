from rest_framework import serializers
from .models import MatrixMap, Point

class PointSerializer(serializers.ModelSerializer):
    class Meta:
        model = Point
        fields = '__all__'
    
    def validate(self, data):
        matrix = data.get('matrix')
        x = data.get('x')
        y = data.get('y')

        # Skip uniqueness check on update if coordinates remain unchanged.
        if self.instance:
            if (self.instance.matrix == matrix and 
                self.instance.x == x and 
                self.instance.y == y):
                return data
            # Exclude the current instance from the uniqueness check.
            if Point.objects.filter(matrix=matrix, x=x, y=y).exclude(pk=self.instance.pk).exists():
                raise serializers.ValidationError("Point with these coordinates already exists in this matrix.")
        else:
            if Point.objects.filter(matrix=matrix, x=x, y=y).exists():
                raise serializers.ValidationError("Point with these coordinates already exists in this matrix.")
        return data

class MatrixMapSerializer(serializers.ModelSerializer):
    points = PointSerializer(many=True, required=False)

    class Meta:
        model = MatrixMap
        fields = '__all__'

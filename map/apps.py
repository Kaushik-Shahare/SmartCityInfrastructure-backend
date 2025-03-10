from django.apps import AppConfig

class MapConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "map"
    
    def ready(self):
        import map.signals
        print("Map app loaded successfully!")  # Debug statement

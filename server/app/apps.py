from django.apps import AppConfig




class AppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'app'
    
    def ready(self):
        from .dependencies import di_setup
        di_setup()

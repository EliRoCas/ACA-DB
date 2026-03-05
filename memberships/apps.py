from django.apps import AppConfig


class MembershipsConfig(AppConfig):
    name = 'memberships'
    
    def ready(self):
        """Importa las señales cuando la aplicación esté lista"""
        import memberships.signals

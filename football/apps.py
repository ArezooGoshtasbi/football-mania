from django.apps import AppConfig


class FootballConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'football'

    def ready(self):
        from football.sync_services.update_service import UpdateService
        update_service = UpdateService()
        update_service.sync_to_latest()

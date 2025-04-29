from django.apps import AppConfig
import sys


class FootballConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'football'

    def ready(self):
        # check if the app is running and doesn't come from migration
        if 'runserver' in sys.argv:
            from football.sync_services.sync_service import SyncService
            sync_service = SyncService()
            sync_service.create_scheduled_tasks()


from django.apps import AppConfig

class TeamUSLConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'team_USL'   # ← app_label は routers.py の想定と一致させる

from django.conf import settings  # import the settings file

from fleet_mng.models import User


def process_settings(request):
    return {'DOCK': settings.DOCK,
            'LAST_ACTIVE_ALL': User.last_active_all(),
            }

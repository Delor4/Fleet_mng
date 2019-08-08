from django.conf import settings # import the settings file

def process_settings(request):
    return {'DOCK': settings.DOCK}
from django.utils import timezone


class ActiveUsersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.

        if request.user.is_authenticated:
            request.user.last_active = timezone.now()
            request.user.save()

        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

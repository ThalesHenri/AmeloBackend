"""Normalize Authorization headers passed through Apache/Passenger."""


class PassengerAuthorizationMiddleware:
    """Restore Authorization when Apache exposes it under REDIRECT_*."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if not request.META.get('HTTP_AUTHORIZATION'):
            redirected_authorization = request.META.get(
                'REDIRECT_HTTP_AUTHORIZATION'
            )
            if redirected_authorization:
                request.META['HTTP_AUTHORIZATION'] = redirected_authorization

        return self.get_response(request)
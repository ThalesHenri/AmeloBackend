from django.test import RequestFactory, SimpleTestCase

from main.middleware import PassengerAuthorizationMiddleware


class PassengerAuthorizationMiddlewareTests(SimpleTestCase):
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = PassengerAuthorizationMiddleware(lambda request: request)

    def test_restores_redirected_authorization_header(self):
        request = self.factory.get(
            '/api/v1/auth/me/',
            REDIRECT_HTTP_AUTHORIZATION='Bearer test-token',
        )

        self.middleware(request)

        self.assertEqual(request.META['HTTP_AUTHORIZATION'], 'Bearer test-token')

    def test_preserves_standard_authorization_header(self):
        request = self.factory.get(
            '/api/v1/auth/me/',
            HTTP_AUTHORIZATION='Bearer test-token',
            REDIRECT_HTTP_AUTHORIZATION='Bearer redirected-token',
        )

        self.middleware(request)

        self.assertEqual(request.META['HTTP_AUTHORIZATION'], 'Bearer test-token')
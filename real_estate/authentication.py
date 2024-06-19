from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from .models import ExpirableToken  # Adjust the import path as necessary


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        try:
            token = ExpirableToken.objects.get(key=key)
        except ExpirableToken.DoesNotExist:
            raise AuthenticationFailed("Invalid Token")

        if token.is_expired():
            raise AuthenticationFailed("Token has expired")

        return (token.user, token)

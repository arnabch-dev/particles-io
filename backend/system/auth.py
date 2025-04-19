from fastapi import HTTPException, status
from typing import Optional
import jwt
from jwt import PyJWKClient
import os
from dotenv import load_dotenv

load_dotenv(".env")


class UnauthorizedException(HTTPException):
    def __init__(self, detail: str, **kwargs):
        super().__init__(status.HTTP_403_FORBIDDEN, detail=detail)


class UnauthenticatedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Requires authentication"
        )


auth0_domain = os.environ.get("AUTH0_DOMAIN")
auth0_algorithms = os.environ.get("AUTH0_ALGORITHMS", "RS256").split(",")
auth0_api_audience = os.environ.get("AUTH0_API_AUDIENCE")
auth0_issuer = os.environ.get("AUTH0_ISSUER") or f"https://{auth0_domain}/"


class VerifyToken:
    def __init__(self):
        jwks_url = f"https://{auth0_domain}/.well-known/jwks.json"
        self.jwks_client = PyJWKClient(jwks_url)

    async def verify(self, token: Optional[str]):
        if not token:
            raise UnauthenticatedException()

        try:
            signing_key = self.jwks_client.get_signing_key_from_jwt(token).key
        except (jwt.exceptions.PyJWKClientError, jwt.exceptions.DecodeError) as error:
            raise UnauthorizedException(f"Token error: {str(error)}")

        try:
            payload = jwt.decode(
                token,
                signing_key,
                algorithms=auth0_algorithms,
                audience=auth0_api_audience,
                issuer=auth0_issuer,
            )
        except jwt.ExpiredSignatureError:
            raise UnauthorizedException("Token expired")
        except jwt.InvalidTokenError as error:
            raise UnauthorizedException(f"Invalid token: {str(error)}")

        return payload

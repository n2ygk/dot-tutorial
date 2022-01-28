from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    # Return standard OIDC claims per /openid.net/specs/openid-connect-core-1_0.html#StandardClaims

    # The Claims requested by the profile, email, address, and phone scope
    # values are returned from the UserInfo Endpoint, as described in
    # Section 5.3.2, when a response_type value is used that results in an
    # Access Token being issued. However, when no Access Token is issued
    # (which is the case for the response_type value id_token),
    # the resulting Claims are returned in the ID Token.


    def get_additional_claims(self):
        return {
            "sub": lambda request: request.user.id,
            "given_name": lambda request: request.user.first_name,
            "family_name": lambda request: request.user.last_name,
            "name": lambda request: ' '.join([request.user.first_name, request.user.last_name]),
            "preferred_username": lambda request: request.user.username,
            "email": lambda request: request.user.email,
        }

    def get_oidc_claims(self, token, token_handler, request):
        """
        override DOT version to use scopes to determine which claims to return.
        per https://openid.net/specs/openid-connect-core-1_0.html#ScopeClaims
        """
        claim_scope = {
            "sub": "openid",
            "name": "profile",
            "family_name": "profile",
            "given_name": "profile",
            "middle_name": "profile",
            "nickname": "profile",
            "preferred_username": "profile",
            "profile": "profile",
            "picture": "profile",
            "website": "profile",
            "gender": "profile",
            "birthdate": "profile",
            "zoneinfo": "profile",
            "locale": "profile",
            "updated_at": "profile",
            "email": "email",
            "email_versified": "email",
            "address": "address",
            "phone_number": "phone",
            "phone_number_verified": "phone",
        }

        data = self.get_claim_dict(request)
        claims = {}

        for k, v in data.items():
            if k in claim_scope and claim_scope[k] in request.scopes:
                claims[k] = v(request) if callable(v) else v
        return claims

from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    # Set `oidc_claim_scope = None` to ignore scopes that limit which claims to return,
    # otherwise the OIDC standard scopes are used.
    # Let's extend the standard scopes to add a new "permissions" scope which returns a "permissions" claim:
    oidc_claim_scope = OAuth2Validator.oidc_claim_scope
    oidc_claim_scope.update({"permissions": "permissions"})

    def get_additional_claims(self):
        # For OIDC certification, mock all 5.1 standard claims.
        return {
            "name": lambda request: ' '.join([request.user.first_name, request.user.last_name]),
            "given_name": lambda request: request.user.first_name,
            "family_name": lambda request: request.user.last_name,
            "middle_name": lambda request: "X",
            "nickname": lambda request: request.user.first_name,
            "preferred_username": lambda request: request.user.username,
            "profile": lambda request: f"https://www.example.com/~{request.user.username}/about",
            "picture": lambda request: f"https://www.example.com/~{request.user.username}.png",
            "website": lambda request: f"https://www.example.com/~{request.user.username}",
            "email": lambda request: request.user.email,
            "email_verified": lambda request: False,
            "gender": lambda request: "unknown",
            "birthdate": lambda request: "0000-01-01",
            "zoneinfo": lambda request: "America/New_York",
            "locale": lambda request: "en-US",
            "phone_number": lambda request: "+1 800-555-1212",
            "phone_number_verified": lambda request: False,
            "address": lambda request: { "formatted": "3020 Broadway\nNew York City\nNew York 10027" },
            "permissions": lambda request: list(request.user.get_group_permissions()),
        }

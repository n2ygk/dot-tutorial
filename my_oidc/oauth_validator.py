from oauth2_provider.oauth2_validators import OAuth2Validator


class CustomOAuth2Validator(OAuth2Validator):
    pass

    # This is for #1069:
    # def get_additional_claims(self):
    #     return {
    #         # "sub": lambda request: request.user.email,
    #         "first_name": lambda request: request.user.first_name,
    #         "last_name": lambda request: request.user.last_name,
    #     }

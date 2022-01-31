# OIDC Certification testing notes

## Configuration
Redirect URI: https://www.certification.openid.net/test/a/django-oauth-toolkit/callback

Clients: hash1 and hash2.

## Tests

### General Issues

So far the errors were because I have it set to require PKCE.
So I made PKCE heroku-configurable and off for now.

Generated and added RSA KEY but neither jwcrypto nor oidcc likes the JWKS:
"Unable to verify id_token signature based on server keys"
"server JWKS does not contain a key with the correct kty that also matches (or does not have) alg/x5t#S256/'use':'sig'"

D'oh! I had set the application algorithm to HMAC with SHA-2 256 instead of RSA!


The following summarize tests that did not fully pass. Some are pretty easy things like needing to mock all
the possible standard claims. Others are harder, like properly implementing claims processing.

### oidcc-response-type-missing: REVIEW


> This test sends an authorization request that is missing the response_type parameter. The authorization server must either redirect back with an 'unsupported_response_type' or 'invalid_request' error, or must display an error saying the response type is missing, a screenshot of which should be uploaded.


Returns an `error=invalid_request` query parameter but does not display HTML text.


### oidcc-scope-profile: WARNING

> 'claims' in userinfo doesn't contain all scope items of scope in authorization request(corresponds to scope standard claims)

I think this means the server isn't return all the standard claims.

TODO: Add additional standard claims with dummy values.

### oidcc-scope-email: WARNING

> Unexpectedly found email in id_token. The conformance suite did not request the 'email' claim is returned in the id_token and hence did not expect the server to include it; as per the spec link for this response_type scope=email is a short hand for 'please give me access to the user's email address in the userinfo response'. Technically returning unrequested claims does not violate the specifications but it could be a bug in the server and may result in user data being exposed in unintended ways if the relying party did not expect the email to be in the id_token, and then uses the id_token to provide proof of the authentication event to other parties.

Not surprisingly, claims handling is not up to snuf.

### oidcc-scope-address: SKIPPED

Need to add `address` to `scopes_supported` and to claims.

### oidcc-scope-phone: SKIPPED

Need to add `phone` to `scopes_supported` and to claims.

### oidcc-scope-all: SKIPPED

> This test requests authorization with address, email, phone and profile scopes.

Need to add the missing scopes/claims.

### oidcc-ensure-other-scope-order-succeeds: WARNING

> Unexpectedly found email in id_token. The conformance suite did not request the 'email' claim is returned in the id_token and hence did not expect the server to include it; as per the spec link for this response_type scope=email is a short hand for 'please give me access to the user's email address in the userinfo response'. Technically returning unrequested claims does not violate the specifications but it could be a bug in the server and may result in user data being exposed in unintended ways if the relying party did not expect the email to be in the id_token, and then uses the id_token to provide proof of the authentication event to other parties.


### oidcc-prompt-login: FAILED

> This test calls the authorization endpoint test twice. The second time it will include prompt=login, so that the authorization server is required to ask the user to login a second time. If auth_time is present in the id_tokens, the value from the second login must be later than the time in the original token. A screenshot of the second authorization should be uploaded.


> prompt=login means the server was required to reauthenticate the user, the id_token from the second authorization incorrectly has the same auth_time as the id_token from the first authorization


### oidcc-prompt-none-not-logged-in: INTERRUPTED

> This test calls the authorization endpoint with prompt=none, expecting that no recent enough authentication is present to enable a silent login and hence the OP will redirect back with an error as per section 3.1.2.6 of OpenID Connect. Please remove any cookies you may have received from the OpenID Provider before proceeding.


```
2022-01-31T19:48:36.261279+00:00 app[web.1]: 10.1.80.43 - - [31/Jan/2022:19:48:36 +0000] "GET /o/authorize/?client_id=hash1&redirect_uri=https://www.certification.openid.net/test/a/django-oauth-toolkit/callback&scope=openid&state=9BVIMtLa6rKNmG4dBJ6UPnV3HzEBjyArnXNro1hsJWbUMvZmthv4hYJ7un1RTy9sXBuUvtV4jEOFUP1oVzZ74YjmiYAwMRx2zypHQRgbbiR8ZNR3Sq0DUhp0nq0pbpq4&nonce=jnJzVXEdy4&response_type=code&prompt=none HTTP/1.1" 500 145 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"

2022-01-31T19:48:36.264273+00:00 heroku[router]: at=info method=GET path="/o/authorize/?client_id=hash1&redirect_uri=https://www.certification.openid.net/test/a/django-oauth-toolkit/callback&scope=openid&state=9BVIMtLa6rKNmG4dBJ6UPnV3HzEBjyArnXNro1hsJWbUMvZmthv4hYJ7un1RTy9sXBuUvtV4jEOFUP1oVzZ74YjmiYAwMRx2zypHQRgbbiR8ZNR3Sq0DUhp0nq0pbpq4&nonce=jnJzVXEdy4&response_type=code&prompt=none" host=dot-tutorial.herokuapp.com request_id=6f6b6c5e-0ee9-4334-b987-e5ae27440e4f fwd="71.190.237.145" dyno=web.1 connect=0ms service=29ms status=500 bytes=452 protocol=http
```

### oidcc-prompt-none-logged-in: INTERRUPTED

> This test calls the authorization endpoint test twice. The second time it will include prompt=none, and the authorization server must not request that the user logs in. The test verifies that auth_time (if present) and sub are consistent between the id_tokens from the first and second authorizations.


```
2022-01-31T19:52:12.022094+00:00 app[web.1]: 10.1.5.151 - - [31/Jan/2022:19:52:12 +0000] "GET /o/authorize/?client_id=hash1&redirect_uri=https://www.certification.openid.net/test/a/django-oauth-toolkit/callback&scope=openid&state=Rq4NYSW7vx&nonce=0lGiqfcxoU&response_type=code&prompt=none HTTP/1.1" 500 145 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"

2022-01-31T19:52:12.024625+00:00 heroku[router]: at=info method=GET path="/o/authorize/?client_id=hash1&redirect_uri=https://www.certification.openid.net/test/a/django-oauth-toolkit/callback&scope=openid&state=Rq4NYSW7vx&nonce=0lGiqfcxoU&response_type=code&prompt=none" host=dot-tutorial.herokuapp.com request_id=4e9971c3-81ea-4d23-9464-9827ac367f43 fwd="71.190.237.145" dyno=web.1 connect=0ms service=18ms status=500 bytes=452 protocol=http
```

### oidcc-max-age-1: FAILED

> This test calls the authorization endpoint test twice. The second time it waits 1 second and includes max_age=1, so that the authorization server is required to ask the user to login a second time and must return an auth_time claim in the second id_token. A screenshot of the second authorization should be uploaded.


> prompt=login means the server was required to reauthenticate the user, the id_token from the second authorization incorrectly has the same auth_time as the id_token from the first authorization

> id_token auth_time is older than 1 second (allowing 5 minutes skews)

### oidcc-id-token-hint: Interrupted

> This test calls the authorization endpoint test twice. The second time it will include prompt=none with the id_token_hint set to the id token from the first authorization, and the authorization server must return successfully immediately without interacting with the user. The test verifies that auth_time (if present) and sub are consistent between the id_tokens from the first and second authorizations.

```
InOBjlTBDLirQjQxwYCrBOYfvRUMlSC__-3Ame_YURv5krPA-JqU3cJF6Pxgs7DttvxIBRLKLhfOnb2pdK2X984MDQ2BpbsJ3NAqTzqb_2daB3KTVasDJl1ZW0iX1omy6xU4OrLXg4e7qolA4j6lcNpqfvWI87NR-QvxRVOwLZQDoZW-8h-muyijXfc8hr3fCRp7VJcTZ0RTxCos0KVB4yGhnFqPnRWzJhTnVq70JghKWS-S856ieyi2_xZwC-tdczYVWvO-3D2ylrKSrnox8KTzxNotCrpz2emkmsLuk_WnXLQBOpVtR-bLeCM3ZHmppabHJi5C0SmIzSGYr3BxfvG_DgN4Txh_vmZ-YndLRpn-eGn3MtWCVx7tVbimQ0X6irdHOt203zr2ukqiRlQ HTTP/1.1" 500 145 "-" "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/97.0.4692.99 Safari/537.36"

2022-01-31T19:56:33.355610+00:00 heroku[router]: at=info method=GET path="/o/authorize/?client_id=hash1&redirect_uri=https://www.certification.openid.net/test/a/django-oauth-toolkit/callback&scope=openid&state=YQQA2eQ8S7&nonce=XWiaKtXkzh&response_type=code&prompt=none&id_token_hint=eyJ0eXAiOiAiSldUIiwgImFsZyI6ICJSUzI1NiIsICJraWQiOiAiaHF4Z19vTV9TbFBTRXRBY3NhQTNFZGdsYkt0d0dYSG0xQldWUzVURklTNCJ9.eyJhdWQiOiAiaGFzaDEiLCAiaWF0IjogMTY0MzY1ODk4OSwgIm5vbmNlIjogIkFZV2kyckdOQW4iLCAiYXRfaGFzaCI6ICJUX29wRGIzODdEZ1FYcC1HUTJhT1pRIiwgInN1YiI6ICIxIiwgImlzcyI6ICJodHRwOi8vZG90LXR1dG9yaWFsLmhlcm9rdWFwcC5jb20vbyIsICJleHAiOiAxNjQzNjk0OTg5LCAiYXV0aF90aW1lIjogMTY0MzQ3OTk3OSwgImp0aSI6ICJlM2QyNTFjZC1hOGM1LTRmOTEtYmI0NS1mZTRkNmNmZWI1MDkifQ.w628zF7ZSoxsPP1iDCd0YGTJ2P1avXaJ6l4LmTuOYq_g4s7_j_bBeeDHBDZ8_63BRXzM37Bi0nuAOQLqbwsaYieeOO_MfeB46kwgoJ-i18hIpLi3xOKt-3Yme8M3b5-wjtqmoVP5F3CEO026YgOZr_cJBjNYytCA66V00p_1d9Opxll1iFnd7C2a5Y5_k6XQkUX-VccEmD2RgNdBeSiI27OOfZn-gRoP2NAJ7hEIJrEM32OsAvBTBYFKGxBcZKgw6vh58odiXSjkrk3LmOQc0XgaInOBjlTBDLirQjQxwYCrBOYfvRUMlSC__-3Ame_YURv5krPA-JqU3cJF6Pxgs7DttvxIBRLKLhfOnb2pdK2X984MDQ2BpbsJ3NAqTzqb_2daB3KTVasDJl1ZW0iX1omy6xU4OrLXg4e7qolA4j6lcNpqfvWI87NR-QvxRVOwLZQDoZW-8h-muyijXfc8hr3fCRp7VJcTZ0RTxCos0KVB4yGhnFqPnRWzJhTnVq70JghKWS-S856ieyi2_xZwC-tdczYVWvO-3D2ylrKSrnox8KTzxNotCrpz2emkmsLuk_WnXLQBOpVtR-bLeCM3ZHmppabHJi5C0SmIzSGYr3BxfvG_DgN4Txh_vmZ-YndLRpn-eGn3MtWCVx7tVbimQ0X6irdHOt203zr2ukqiRlQ" host=dot-tutorial.herokuapp.com request_id=e9087740-6f7a-4a73-86d4-c8041708ec7d fwd="71.190.237.145" dyno=web.1 connect=0ms service=23ms status=500 bytes=452 protocol=http~
```

### oidcc-ensure-request-with-acr-values-succeeds: WARNING

> An acr value was requested using acr_values, so the server 'SHOULD' return an acr claim, but it did not.


### oidcc-codereuse-30seconds: WARNING

> This test tries using an authorization code for a second time, 30 seconds after the first use. The server must return an invalid_grant error as the authorization code has already been used. The originally issued access token should be revoked (as per RFC6749-4.1.2) - a warning is issued if the access token still works.

> No error from resource endpoint


### oidcc-unsigned-request-object-supported-correctly-or-rejected-as-unsupported: FAILED

> This test sends a unsigned request object (by value) to the authorization endpoint. The server must either accept the request and process the authentication correctly, or return a request_not_supported error as per OIDCC-3.1.2.6. Note that the python suite allowed implementations to completely ignore the request object - this was not compliant with the spec, and in this test either the object must be processed or request_not_supported must be returned. The test will be skipped if the server discovery document does not indicate support for unsigned request objects - i.e. if (alg:none).


> State was passed in request, but is missing from response (or returned in the wrong place)

> Nonce values mismatch

### oidcc-claims-essential: WARNING

> This test makes an authorization request requesting the 'name' claim as essential (in the userinfo, except for response_type=id_token where it is requested in the id_token), and the OP must return a successful result. A warning is raised if the OP fails to return a value for the name claim.


> name not found in userinfo


### oidcc-refresh-token: WARNING

> The server issued a refresh token but does not claim to support this grant type (grant_types_supported in not present in the discovery document)

> The server issued a refresh token but does not claim to support this grant type (grant_types_supported in not present in the discovery document)




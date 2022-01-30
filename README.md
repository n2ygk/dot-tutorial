# Django OAuth Toolkit Tutorial

Use this repo for testing DOT functionality.

It is based on this [tutorial](https://django-oauth-toolkit.readthedocs.io/en/latest/tutorial/tutorial_01.html)

## Start the Demo

Simply run `tox` to configure and run the demo with a preloaded user and OAuth2 application defined.

The user is `admin` with password `admin123`.

The application's name is `hashed secret`, the `client_id` is `hash1` with `client_secret` of `hashed`.


```
(venv) dot-tutorial$ tox
py39 create: /Users/ac45/src/dot-tutorial/venv
py39 installdeps: -rrequirements.txt
py39 develop-inst: /Users/ac45/src/dot-tutorial
py39 installed: asgiref==3.4.1,black==21.12b0,certifi==2021.10.8,cffi==1.15.0,charset-normalizer==2.0.10,click==8.0.3,cryptography==36.0.1,Deprecated==1.2.13,Django==4.0.1,django-cors-headers==3.10.1,django-oauth-toolkit @ file:///Users/ac45/src/django-oauth-toolkit,idna==3.3,jwcrypto==1.0,mypy-extensions==0.4.3,oauthlib==3.1.1,pathspec==0.9.0,platformdirs==2.4.1,pycparser==2.21,PyYAML==6.0,requests==2.27.1,sqlparse==0.4.2,tomli==1.2.3,typing_extensions==4.0.1,-e git+ssh://git@github.com/n2ygk/dot-tutorial.git@8686c493c1003584634373818b9cd2e806ae7b72#egg=UNKNOWN,urllib3==1.26.8,wrapt==1.13.3
py39 run-test-pre: PYTHONHASHSEED='1698771071'
py39 run-test: commands[0] | ./manage.py migrate
Operations to perform:
Apply all migrations: admin, auth, contenttypes, oauth2_provider, sessions
Running migrations:
Applying contenttypes.0001_initial... OK
Applying auth.0001_initial... OK
Applying admin.0001_initial... OK
Applying admin.0002_logentry_remove_auto_add... OK
Applying admin.0003_logentry_add_action_flag_choices... OK
Applying contenttypes.0002_remove_content_type_name... OK
Applying auth.0002_alter_permission_name_max_length... OK
Applying auth.0003_alter_user_email_max_length... OK
Applying auth.0004_alter_user_username_opts... OK
Applying auth.0005_alter_user_last_login_null... OK
Applying auth.0006_require_contenttypes_0002... OK
Applying auth.0007_alter_validators_add_error_messages... OK
Applying auth.0008_alter_user_username_max_length... OK
Applying auth.0009_alter_user_last_name_max_length... OK
Applying auth.0010_alter_group_name_max_length... OK
Applying auth.0011_update_proxy_permissions... OK
Applying auth.0012_alter_user_first_name_max_length... OK
Applying oauth2_provider.0001_initial... OK
Applying oauth2_provider.0002_auto_20190406_1805... OK
Applying oauth2_provider.0003_auto_20201211_1314... OK
Applying oauth2_provider.0004_auto_20200902_2022... OK
Applying oauth2_provider.0005_auto_20211222_2352... OK
Applying oauth2_provider.0006_alter_application_client_secret... OK
Applying sessions.0001_initial... OK
py39 run-test: commands[2] | ./manage.py loaddata fixtures/auth.user.yaml fixtures/oauth2_provider.application.yaml
Installed 2 object(s) from 2 fixture(s)
py39 run-test: commands[3] | ./manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 08, 2022 - 21:19:56
Django version 4.0.1, using settings 'tutorial.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Continue the demo

After quitting the demo, you can mess around and restart it with:

```
dot-tutorial$ source venv/bin/activate
(venv) dot-tutorial$ ./manage.py runserver
Watching for file changes with StatReloader
Performing system checks...

System check identified no issues (0 silenced).
January 08, 2022 - 21:22:18
Django version 4.0.1, using settings 'tutorial.settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

## Test the OIDC Userinfo Endpoint with Postman

Following is an example of testing OIDC Authorization Code flow to login with this demo setup and
then interrogate the Userinfo endpoint.

It uses [Postman](https://www.postman.com/downloads/), the Swiss Army Knife of the Internet.

### Run the server

```
(venv) dot-tutorial$ ./manage.py runserver
```

### Configure Postman for OAuth2

![postman oauth2 setup](./media/postman-01-oauth2-setup.png)

### Request new token -- Django login redirect

![django login redirect from postman](./media/postman-02-login.png)

### Request new token -- OAuth2 scope approval

![DOT scope approval](./media/postman-03-approve.png)

### Request new token -- It worked!

![Got the new token](./media/postman-04-proceed.png)

### Tell Postman to use the token
![Use the token](./media/postman-05-use-token.png)

### Decode the id_token

![Decode the JWT ID Token](./media/decode_id_token.png)

### Do a Userinfo lookup of the token

![Userinfo lookup](./media/postman-06-userinfo-result.png)

## Deploy on heroku

See https://devcenter.heroku.com/articles/getting-started-with-python and then tweak a few files:

- Procfile
- app.json
- release-tasks.sh
- requirements.txt

The basic heroku CLI commands used are:

```
heroku apps:create
heroku apps:rename dot-tutorial
git push heroku main
heroku config:set DJANGO_DEBUG=false
heroku config:set DOT_PKCE=false
heroku logs -t
```

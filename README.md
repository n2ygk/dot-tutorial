<!-- toc -->

- [Start the Demo](#start-the-demo)
- [Continue the demo](#continue-the-demo)
- [Test the OIDC Userinfo Endpoint with Postman](#test-the-oidc-userinfo-endpoint-with-postman)
  * [Run the server](#run-the-server)
  * [Configure Postman for OAuth2](#configure-postman-for-oauth2)
  * [Request new token -- Django login redirect](#request-new-token----django-login-redirect)
  * [Request new token -- OAuth2 scope approval](#request-new-token----oauth2-scope-approval)
  * [Request new token -- It worked!](#request-new-token----it-worked)
  * [Tell Postman to use the token](#tell-postman-to-use-the-token)
  * [Decode the id_token](#decode-the-id_token)
  * [Do a Userinfo lookup of the token](#do-a-userinfo-lookup-of-the-token)
- [Deploy on heroku](#deploy-on-heroku)
- [Add Celery task to clear expired tokens](#add-celery-task-to-clear-expired-tokens)
  * [Basic Celery setup](#basic-celery-setup)
  * [App changes](#app-changes)
  * [Start RabbitMQ](#start-rabbitmq)
  * [Start Celery Beat](#start-celery-beat)
  * [Start Celery Worker](#start-celery-worker)

<!-- tocstop -->


## Add Celery task to clear expired tokens

The `cleartokens` management command should be run periodically to delete expired tokens.

One way to do this is to use the Celery task manager to configure an periodic task. Celery
has an auto-discovery feature that looks for `tasks.py` in each installed app, so we'll add one here.

### Basic Celery setup

Here are some documentation links to follow:

<!-- this domain is SNAFU:
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html

https://docs.celeryproject.org/en/latest/userguide/periodic-tasks.html#using-custom-scheduler-classes
-->

https://docs.celeryq.dev/en/stable/django/first-steps-with-django.html

https://docs.celeryq.dev/en/stable/userguide/periodic-tasks.html#beat-custom-schedulers

https://django-celery-beat.readthedocs.io/en/latest/index.html

The key steps are:
1. Add support in the Django admin to configure Celery.
2. Add a celery task definition.
3. Use Celery Beat for the task timing
4. Use RabbitMQ for the message queue.

### App changes

The required changes to this tutorial app are shown here as diffs. This is currently using an
unmerged PR that reverts an incorrect addition of Celery `tasks.py` to DOT.

```diff
diff --git a/requirements.txt b/requirements.txt
index 09951f9..59983f4 100644
--- a/requirements.txt
+++ b/requirements.txt
@@ -14,3 +14,5 @@ django-oauth-toolkit==1.7.0
 PyYAML
 django-heroku
 gunicorn
+celery>=5.2
+django-celery-beat
-django-oauth-toolkit==1.7.0
+#django-oauth-toolkit==1.7.0
+# PR #1126:
+git+https://github.com/n2ygk/django-oauth-toolkit.git@revert_1070
diff --git a/tutorial/__init__.py b/tutorial/__init__.py
index e69de29..fb989c4 100644
--- a/tutorial/__init__.py
+++ b/tutorial/__init__.py
@@ -0,0 +1,3 @@
+from .celery import app as celery_app
+
+__all__ = ('celery_app',)
diff --git a/tutorial/celery.py b/tutorial/celery.py
new file mode 100644
index 0000000..3f5f1c9
--- /dev/null
+++ b/tutorial/celery.py
@@ -0,0 +1,22 @@
+import os
+
+from celery import Celery
+
+# Set the default Django settings module for the 'celery' program.
+os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tutorial.settings')
+
+app = Celery('tutorial', broker="pyamqp://guest@localhost//")
+
+# Using a string here means the worker doesn't have to serialize
+# the configuration object to child processes.
+# - namespace='CELERY' means all celery-related configuration keys
+#   should have a `CELERY_` prefix.
+app.config_from_object('django.conf:settings', namespace='CELERY')
+
+# Load task modules from all registered Django apps.
+app.autodiscover_tasks()
+
+
+@app.task(bind=True)
+def debug_task(self):
+    print(f'Request: {self.request!r}')
diff --git a/tutorial/settings.py b/tutorial/settings.py
index 2fc7b41..7172e24 100644
--- a/tutorial/settings.py
+++ b/tutorial/settings.py
@@ -42,6 +42,8 @@ INSTALLED_APPS = [
     "django.contrib.staticfiles",
     "oauth2_provider",
     "corsheaders",
+    "tutorial",
+    "django_celery_beat",
 ]
 
 MIDDLEWARE = [
diff --git a/tutorial/tasks.py b/tutorial/tasks.py
new file mode 100644
index 0000000..74b76d1
--- /dev/null
+++ b/tutorial/tasks.py
@@ -0,0 +1,8 @@
+from celery import shared_task
+
+@shared_task
+def clear_tokens():
+    from oauth2_provider.models import clear_expired
+
+    clear_expired()
+
```

Now the Django admin console will show some new Periodic Tasks:

![tasks screenshot](./admin+celery.png)

Click "Add periodic task", pick a name and select from the list of registered tasks.

![add periodic task screenshot](./celery+add.png)


### Start RabbitMQ

Start up [rabbitmq](https://www.rabbitmq.com/download.html):

On MacOS:
```
$ brew install rabbitmq
$ brew services start rabbitmq
```

On other platforms there's a Docker image available:
```
docker run -it --rm --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3.9-management
```

### Start Celery Beat

Then start up celery beat:
```
(env) dot-tutorial$ celery -A tutorial beat -l INFO --scheduler django_celery_beat.schedulers:DatabaseScheduler
celery beat v5.2.3 (dawn-chorus) is starting.
__    -    ... __   -        _
LocalTime -> 2022-03-18 21:39:12
Configuration ->
    . broker -> amqp://guest:**@localhost:5672//
    . loader -> celery.loaders.app.AppLoader
    . scheduler -> django_celery_beat.schedulers.DatabaseScheduler

    . logfile -> [stderr]@%INFO
    . maxinterval -> 5.00 seconds (5s)
[2022-03-18 21:39:12,078: INFO/MainProcess] beat: Starting...
```

Beat runs the task queue periodically and sends tasks via RabbitMQ to the worker.

### Start Celery Worker

Then start the worker which consumes the messages from the queue and executes them:

```
(env) dot-tutorial$ celery -A tutorial worker --loglevel=INFO
/Users/ac45/src/dot-tutorial/env/lib/python3.9/site-packages/celery/platforms.py:810: SecurityWarning: An entry for the specified gid or egid was not found.
We're assuming this is a potential security issue.

  warnings.warn(SecurityWarning(ASSUMING_ROOT))
/Users/ac45/src/dot-tutorial/env/lib/python3.9/site-packages/celery/platforms.py:840: SecurityWarning: You're running the worker with superuser privileges: this is
absolutely not recommended!

Please specify a different user using the --uid option.

User information: uid=1476831425 euid=1476831425 gid=1291818287 egid=1291818287

  warnings.warn(SecurityWarning(ROOT_DISCOURAGED.format(
 
 -------------- celery@082-AC45-M2 v5.2.3 (dawn-chorus)
--- ***** ----- 
-- ******* ---- macOS-12.3-x86_64-i386-64bit 2022-03-19 17:12:56
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         tutorial:0x1046faac0
- ** ---------- .> transport:   amqp://guest:**@localhost:5672//
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . tutorial.tasks.clear_tokens
  . tutorial.celery.debug_task

[2022-03-19 17:12:57,116: INFO/MainProcess] Connected to amqp://guest:**@127.0.0.1:5672//
[2022-03-19 17:12:57,131: INFO/MainProcess] mingle: searching for neighbors
[2022-03-19 17:12:58,169: INFO/MainProcess] mingle: all alone
[2022-03-19 17:12:58,186: WARNING/MainProcess] /Users/ac45/src/dot-tutorial/env/lib/python3.9/site-packages/celery/fixups/django.py:203: UserWarning: Using settings.DEBUG leads to a memory
            leak, never use this setting in production environments!
  warnings.warn('''Using settings.DEBUG leads to a memory

[2022-03-19 17:12:58,187: INFO/MainProcess] celery@082-AC45-M2 ready.
[2022-03-19 17:12:58,188: INFO/MainProcess] Task tutorial.celery.debug_task[63f16c50-ef33-41f8-bdc0-0216a8486466] received
[2022-03-19 17:12:58,188: INFO/MainProcess] Task tutorial.tasks.clear_tokens[b69380b1-f6bd-4ed1-927e-8b2b7b2bfa14] received
[2022-03-19 17:12:58,292: WARNING/ForkPoolWorker-8] Request: <Context: {'lang': 'py', 'task': 'tutorial.celery.debug_task', 'id': '63f16c50-ef33-41f8-bdc0-0216a8486466', 'shadow': None, 'eta': None, 'expires': None, 'group': None, 'group_index': None, 'retries': 0, 'timelimit': [None, None], 'root_id': '63f16c50-ef33-41f8-bdc0-0216a8486466', 'parent_id': None, 'argsrepr': '()', 'kwargsrepr': '{}', 'origin': 'gen76730@082-AC45-M2', 'ignore_result': False, 'properties': {'content_type': 'application/json', 'content_encoding': 'utf-8', 'application_headers': {'lang': 'py', 'task': 'tutorial.celery.debug_task', 'id': '63f16c50-ef33-41f8-bdc0-0216a8486466', 'shadow': None, 'eta': None, 'expires': None, 'group': None, 'group_index': None, 'retries': 0, 'timelimit': [None, None], 'root_id': '63f16c50-ef33-41f8-bdc0-0216a8486466', 'parent_id': None, 'argsrepr': '()', 'kwargsrepr': '{}', 'origin': 'gen76730@082-AC45-M2', 'ignore_result': False}, 'delivery_mode': 2, 'priority': 0, 'correlation_id': '63f16c50-ef33-41f8-bdc0-0216a8486466', 'reply_to': '51d61210-7a3f-33db-8307-94683ce668e6'}, 'reply_to': '51d61210-7a3f-33db-8307-94683ce668e6', 'correlation_id': '63f16c50-ef33-41f8-bdc0-0216a8486466', 'hostname': 'celery@082-AC45-M2', 'delivery_info': {'exchange': '', 'routing_key': 'celery', 'priority': 0, 'redelivered': False}, 'args': [], 'kwargs': {}, 'is_eager': False, 'callbacks': None, 'errbacks': None, 'chain': None, 'chord': None, 'called_directly': False, '_protected': 1}>
[2022-03-19 17:12:58,292: INFO/ForkPoolWorker-1] refresh_expire_at is None. No refresh tokens deleted.
[2022-03-19 17:12:58,294: INFO/ForkPoolWorker-8] Task tutorial.celery.debug_task[63f16c50-ef33-41f8-bdc0-0216a8486466] succeeded in 0.0025927220000001583s: None
[2022-03-19 17:12:58,305: INFO/ForkPoolWorker-1] 0 Expired access tokens deleted
[2022-03-19 17:12:58,306: INFO/ForkPoolWorker-1] 0 Expired grant tokens deleted
[2022-03-19 17:12:58,307: INFO/ForkPoolWorker-1] Task tutorial.tasks.clear_tokens[b69380b1-f6bd-4ed1-927e-8b2b7b2bfa14] succeeded in 0.015684232999999992s: None
...
```

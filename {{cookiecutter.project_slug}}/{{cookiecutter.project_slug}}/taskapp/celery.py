{% if cookiecutter.use_celery == 'y' %}
import os
from celery import Celery
from django.apps import apps, AppConfig
from django.conf import settings


if not settings.configured:
    # set the default Django settings module for the 'celery' program.
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')  # pragma: no cover


#The Celery library must be instantiated before use, this instance is called 
#an application (or app for short).
#http://docs.celeryproject.org/en/latest/getting-started/next-steps.html#project-layout
app = Celery('{{cookiecutter.project_slug}}')


class CeleryAppConfig(AppConfig):
    name = '{{cookiecutter.project_slug}}.taskapp'
    verbose_name = 'Celery Config'

    def ready(self):
        # Using a string here means the worker will not have to
        # pickle the object when using Windows.
        # - namespace='CELERY' means all celery-related configuration keys
        #   should have a `CELERY_` prefix.
        app.config_from_object('django.conf:settings', namespace='CELERY')
        installed_apps = [app_config.name for app_config in apps.get_app_configs()]
        app.autodiscover_tasks(lambda: installed_apps, force=True)

        {% if cookiecutter.use_sentry == 'y' -%}
        if hasattr(settings, 'RAVEN_CONFIG'):
            # Celery signal registration
{% if cookiecutter.use_pycharm == 'y' -%}
	    # Since raven is required in production only,
            # imports might (most surely will) be wiped out
            # during PyCharm code clean up started
            # in other environments.
            # @formatter:off
{%- endif %}
            #To capture errors, you need to register a couple of signals to hijack Celery error handling:
            from raven import Client as RavenClient
            from raven.contrib.celery import register_signal as raven_register_signal
            from raven.contrib.celery import register_logger_signal as raven_register_logger_signal
{% if cookiecutter.use_pycharm == 'y' -%}
            # @formatter:on
{%- endif %}

            raven_client = RavenClient(dsn=settings.RAVEN_CONFIG['dsn'])
            # register a custom filter to filter out duplicate logs
            raven_register_logger_signal(raven_client)
            ## hook into the Celery error handler
            raven_register_signal(raven_client)
        {%- endif %}


#When you send a task message in Celery, that message won’t contain any source 
#code, but only the name of the task you want to execute. This works similarly 
#to how host names work on the internet: every worker maintains a mapping of 
#task names to their actual functions, called the task registry.
#Whenever you define a task, that task will also be added to the local registry

#A task being bound means the first argument to the task will always be the 
#task instance (self) 
@app.task(bind=True)
def debug_task(self):
    #!r uses repr() and the f is formatting
    #pragma is for the coverage module
    print(f'Request: {self.request!r}')  # pragma: no cover
{% else %}
# Use this as a starting point for your project with celery.
# If you are not using celery, you can remove this app
{% endif -%}

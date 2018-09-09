FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 1

RUN apk update \
  # psycopg2 dependencies
  #--virtual allows us to create an alias called build-deps for a group of 
  #packages so that they can easily be removed,updated or generally manipulated
  && apk add --virtual build-deps gcc python3-dev musl-dev \
  && apk add postgresql-dev \
  # Pillow dependencies
  && apk add jpeg-dev zlib-dev freetype-dev lcms2-dev openjpeg-dev tiff-dev tk-dev tcl-dev \
  # CFFI dependencies
  #These support argon hashing library
  && apk add libffi-dev py-cffi

#Principle of least privilege by introducing a new group and user for our 
#application
RUN addgroup -S django \
    && adduser -S -G django django

# Requirements are installed here to ensure they will be cached.
COPY ./requirements /requirements
#--no-cache-dir is used because containers are typically ephemeral and the 
#convenience of reinstalling modules is unnecessary while also increasing size
#for not benefit
RUN pip install --no-cache-dir -r /requirements/production.txt \
    && rm -rf /requirements

#The entry point is needed to detect when postgres actually becomes available
#The depends-on component of docker compose is not sufficient and this is 
#actually mentioned in the docker documentation for depends-on
#Entry point also exports the database url as environment variable which is 
#itself constructed from other environment variables that are (i think) 
#sourced by docker using its env tool before this entrypoint script is used
#Celery broker url asociated with redis is set here too
COPY ./compose/production/django/entrypoint /entrypoint
#Removing the carriage returns in the script
RUN sed -i 's/\r//' /entrypoint
RUN chmod +x /entrypoint
#Principle of least privilege
RUN chown django /entrypoint

#Start script moves static files to one place for benefit of nginx or other 
#server and spins up the the gunicorn server behinid that frontend server
COPY ./compose/production/django/start /start
RUN sed -i 's/\r//' /start
RUN chmod +x /start
RUN chown django /start
{% if cookiecutter.use_celery == "y" %}
COPY ./compose/production/django/celery/worker/start /start-celeryworker
RUN sed -i 's/\r//' /start-celeryworker
RUN chmod +x /start-celeryworker
RUN chown django /start-celeryworker

COPY ./compose/production/django/celery/beat/start /start-celerybeat
RUN sed -i 's/\r//' /start-celerybeat
RUN chmod +x /start-celerybeat
RUN chown django /start-celerybeat

COPY ./compose/production/django/celery/flower/start /start-flower
RUN sed -i 's/\r//' /start-flower
RUN chmod +x /start-flower
{% endif %}


COPY . /app

#Principle of least privilege 
RUN chown -R django /app
USER django

WORKDIR /app

ENTRYPOINT ["/entrypoint"]

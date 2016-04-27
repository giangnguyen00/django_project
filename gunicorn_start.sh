#!/bin/bash

NAME="mysite"                              #Name of the application (*)
DJANGODIR=/Users/giangnguyen/Desktop/School/django_project/            # Django project directory (*)
USER=giangnguyen                                        # the user to run as (*)
NUM_WORKERS=3                                     # how many worker processes should Gunicorn spawn (*)
DJANGO_SETTINGS_MODULE=mysite.settings             # which settings file should Django use (*)
DJANGO_WSGI_MODULE=mysite.wsgi                     # WSGI module name (*)

echo "Starting $NAME as `whoami`"

# Activate the virtual environment
cd $DJANGODIR
source /Users/giangnguyen/Desktop/School/django_project/myvenv/bin/activate
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE
export PYTHONPATH=$DJANGODIR:$PYTHONPATH

# Create the run directory if it doesn't exist
RUNDIR=$(dirname $SOCKFILE)
test -d $RUNDIR || mkdir -p $RUNDIR

# Start your Django Unicorn
# Programs meant to be run under supervisor should not daemonize themselves (do not use --daemon)
exec /Users/giangnguyen/Desktop/School/django_project/myvenv/bin/gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --user $USER \
  --log-level=debug \
  --log-file=- \
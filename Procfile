
web:       bin/start-nginx newrelic-admin run-program gunicorn -c config/gunicorn.conf muckrock.wsgi:application
scheduler: newrelic-admin run-program celery worker -E -B --loglevel=INFO
worker:    newrelic-admin run-program celery worker -E -Q celery,phaxio --loglevel=INFO

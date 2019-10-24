#FROM python:2.7
FROM tiangolo/uwsgi-nginx-flask:python2.7
ADD . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENV FLASK_APP "flaskr"
ENV FLASK_ENV "production"
ENV FLASK_RUN_EXTRA_FILES "content.yml"
#CMD flask run
#CMD python web/wsgi.py
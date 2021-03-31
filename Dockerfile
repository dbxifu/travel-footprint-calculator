FROM tiangolo/uwsgi-nginx-flask:python3.8
ADD . /app
WORKDIR /app
RUN apt-get update && apt-get install -y cython3
RUN pip install -r requirements.txt
ENV FLASK_APP "flaskr"
ENV FLASK_ENV "production"
ENV FLASK_RUN_EXTRA_FILES "content.yml"
#CMD flask run
#CMD python web/wsgi.py
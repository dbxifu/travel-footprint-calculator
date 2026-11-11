# Python + UWSGI + NGINX
# https://github.com/tiangolo/uwsgi-nginx-flask-docker/blob/master/docker-images/python3.12.dockerfile
# based on
# https://github.com/tiangolo/uwsgi-nginx-docker/blob/master/docker-images/python3.12.dockerfile
# based on python-3.12-trixie
#
# Notes:
# - +150Mio in RAM
# - Sort of abandoned
# - UWSGI is as well
# - Tips on the tiangolo repo <3
# - Consider using a hardened debian instead of this
# - Consider using multiple services instead
#
FROM tiangolo/uwsgi-nginx-flask:python3.12

# Unsure why this was in here…
#ENV FLASK_APP "flaskr"
#ENV FLASK_ENV "production"
#ENV FLASK_RUN_EXTRA_FILES "content.yml"

WORKDIR /app

RUN --mount=type=cache,sharing=locked,target=/var/lib/apt/lists \
    --mount=type=cache,sharing=locked,target=/var/cache/apt \
    rm -f /etc/apt/apt.conf.d/docker-clean \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive \
       apt-get --yes --no-install-recommends install \
         cython3

# Interestingly, there already are some files in here that we are overwriting. (UWSGI config and entrypoints)
#RUN pwd && ls -laHF && cat * && exit 42

ADD requirements.txt .
RUN --mount=type=cache,sharing=locked,mode=0755,target=/root/.cache/pip \
    python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# And now we add pretty much everything we have sourcewise to the docker image.
# This leverages the .dockerignore file to exclude plenty of other files we don't want.
# We also don't really *need* to exclude the requirements file here.  I felt like it, that's why.
# I'm also excluding the tests here, as we might add them in another stage if we want to run them in docker.
ADD --exclude=requirements.txt \
    --exclude=tests \
    . .

# The default entrypoint reads our wsgi.ini file and starts WSGI.

# We can set container prestart hooks in the bash script prestart.sh
# That's neat.


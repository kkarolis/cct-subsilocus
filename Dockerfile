FROM python:3.8

ENV PYTHONUNBUFFERED 1

# gosu stepdown
# https://github.com/tianon/gosu/blob/master/INSTALL.md#from-debian
RUN set -eux; \
	apt-get update; \
	apt-get install -y gosu; \
	rm -rf /var/lib/apt/lists/*; \
	# verify that the binary works
	gosu nobody true

RUN set -eux; \
	useradd -r -s /sbin/nologin -m -d /var/lib/appuser appuser; \
	mkdir -p /var/lib/appuser/app

COPY requirements.txt /var/lib/appuser/app

RUN set -eux; \
	pip install --upgrade pip; \
	# virtualenv might be a better idea
	pip install -r /var/lib/appuser/app/requirements.txt

COPY . /var/lib/appuser/app

RUN set -eux; \
	chown -R appuser.appuser /var/lib/appuser/app

WORKDIR /var/lib/appuser/app

COPY ./docker/wait-for-it.sh /usr/local/sbin
COPY ./docker/entrypoint /usr/local/sbin

ENTRYPOINT ["/usr/local/sbin/entrypoint"]

# uwsgi would probably be running in production here with nginx serving the statics
CMD ["runserver", "0.0.0.0:8000"]

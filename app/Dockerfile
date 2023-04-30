FROM ubuntu:focal

ENV APP_HOME /app/
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ENV PYTHONPATH ${PYTHONPATH}:${APP_HOME}

COPY . $APP_HOME
WORKDIR $APP_HOME

RUN apt-get -y update
RUN apt-get install -y gnupg wget curl htop lsb-release build-essential netcat rsync sshpass gettext-base

RUN apt-get install -y postgresql-client
RUN apt-get install -y python3 python3-pip

# Install Python requirements
RUN pip3 install psycopg2-binary
RUN pip3 install -r requirements.txt

# install UWSGI
RUN pip3 install uwsgi uwsgitop
RUN ln -s /usr/local/uwsgi /usr/bin/uwsgi

RUN rm -rf $APP_HOME
COPY ./entrypoint.sh /app/entrypoint.sh

CMD tail -f /dev/null

ENTRYPOINT ["sh", "/app/entrypoint.sh"]

RUN rm -rf /app
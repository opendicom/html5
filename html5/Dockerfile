FROM python:3.6.8

# set work directory
WORKDIR /usr/src/html5

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \
    && apt-get install -y netcat

# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/html5/requirements.txt
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/html5/

# run entrypoint.sh
ENTRYPOINT ["/usr/src/html5/entrypoint.sh"]
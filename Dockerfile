FROM python:3.7-slim
MAINTAINER Philippe Remy <premy.enseirb@gmail.com>

# https://stackoverflow.com/questions/36710459/how-do-i-make-a-comment-in-a-dockerfile
ARG DEBIAN_FRONTEND=noninteractive

# copy models files.
COPY . /app/

WORKDIR /app
RUN pip3 install -r requirements.txt

ENTRYPOINT [ "python3" ]

CMD [ "gaica_server.py" ]

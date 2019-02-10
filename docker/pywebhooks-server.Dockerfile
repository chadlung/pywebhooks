FROM python:3.6

COPY . /opt/pywebhooks
WORKDIR /opt/pywebhooks

RUN pip install -U pip
RUN pip install -r requirements.txt
RUN pip install -e .

EXPOSE 8081

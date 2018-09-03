FROM python:3.6-stretch
MAINTAINER Matteo Gaito
# Codice fuori dal docker

ADD requirements.txt /etc/af-requirements.txt

RUN mkdir /af
RUN apt-get update && apt-get install locales -y
RUN echo "it_IT.UTF-8 UTF-8" > /etc/locale.gen
RUN locale-gen

RUN apt-get install -y libxss1 libappindicator1
RUN apt-get install -y fonts-liberation libappindicator3-1 libasound2 libatk-bridge2.0-0 libgtk-3-0 libnspr4 libnss3 libxtst6 lsb-release xdg-utils
RUN apt-get install -y xvfb
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN dpkg -i google-chrome*.deb
RUN apt-get install -f

RUN pip3 install -r /etc/af-requirements.txt

EXPOSE 5000

CMD ["/usr/local/bin/gunicorn", "-c", "/af/sys/gunicorn_conf.py", "--chdir", "/af", "app:app", "--preload"]

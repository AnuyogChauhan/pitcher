FROM ubuntu:16.04
MAINTAINER Anderson Miller <anderson.miller@frogdesign.com>

#ENV http_proxy http://165.225.104.34:80
#ENV https_proxy https://165.225.104.34:80
#RUN echo "8.8.8.8" >> /etc/resolv.conf
#RUN echo "8.8.4.4" >> /etc/resolv.conf

RUN echo "break cache 100001"
RUN apt-get update
RUN apt-get install -y python python-redis python-parse
RUN mkdir /frog
COPY . /frog/
WORKDIR /frog/

ENV USE_REDIS=TRUE
ENV REDIS_SERVICE_HOST="2.2.2.4"
ENV REDIS_SERVICE_PORT=6379

CMD ["/usr/bin/python","CarServerENS.py","5003"]

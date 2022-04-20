FROM python:3.10-slim

########################################
# add a user so we're not running as root
########################################
RUN useradd useruser

RUN apt-get update && apt-get -y install git && apt-get clean

RUN mkdir -p /home/useruser/
RUN chown useruser /home/useruser -R
RUN chgrp useruser /home/useruser -R

USER useruser
WORKDIR /home/useruser/
RUN git clone https://github.com/yaleman/pvoutput.git

RUN python -m pip install --upgrade pip pvoutput

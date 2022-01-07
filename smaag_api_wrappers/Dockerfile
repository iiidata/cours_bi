# set base image (host OS)
FROM python:3.8

# Update aptitude with new repo
RUN apt-get update

# Install software
RUN apt-get install -y git python3-pip

#Create a new folder wrappers
RUN mkdir wrappers

#Copies code
COPY . wrappers/

# install dependencies
RUN pip install -r wrappers/requirements.txt

ENV PYTHONPATH="wrappers"

ENTRYPOINT ["python","./wrappers/main.py"]

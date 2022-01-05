# set base image (host OS)
FROM python:3.8


# Update aptitude with new repo
RUN apt-get update

# Install software
RUN apt-get install -y git python3-pip


ENV PYTHONPATH="terricomm_dbt"

RUN mkdir /root/.dbt
COPY profiles.yml /root/.dbt/profiles.yml

WORKDIR /dbt
ARG IIICOMM_ENV
ARG CRYPTOGRAPHY_KEY
RUN dbt deps

ENTRYPOINT ["dbt"]

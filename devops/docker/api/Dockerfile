FROM python:3.9 AS base

LABEL maintainer="Victor Merkushov <merkushov.victor@gmail.com>"

RUN apt-get -y update \
    && apt-get install -y apt-utils

ARG uid=1000
ARG gid=1000

ENV USER=fastapi
ENV GROUP=fastapi
ENV HOMEDIR=/home/${USER}
ENV APP_HOME=/usr/src/app
ENV APP_TEST=/usr/src/app_tests
ENV APP_REQUIREMENTS=/usr/src/app_requirements
ENV PATH="/home/${USER}/.local/bin:${PATH}"

RUN mkdir ${APP_HOME}
RUN mkdir ${APP_REQUIREMENTS}
WORKDIR ${APP_HOME}/src

# Create an unpribileged user
RUN groupadd -g $gid ${GROUP} && \
    useradd -d ${HOMEDIR} -s /bin/bash -u $uid -g $gid ${USER} && \
    mkdir ${HOMEDIR} && \
    chown -R ${USER}:${GROUP} ${HOMEDIR}

COPY devops/api/requirements ${APP_REQUIREMENTS}

USER ${USER}

RUN /usr/local/bin/python -m pip install --upgrade pip

# -----------------------------------------------------------------------------
# production environment
# -----------------------------------------------------------------------------

# FROM base AS production

# USER ${USER}

# COPY src ${APP_HOME}

# RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/prod.txt"

# -----------------------------------------------------------------------------
# functional tests environment
# -----------------------------------------------------------------------------

FROM base AS test

USER root

RUN mkdir ${APP_TEST}

WORKDIR ${APP_TEST}/functional

COPY --chown=${USER}:${USER} src ${APP_HOME}
COPY --chown=${USER}:${USER} tests ${APP_TEST}

USER ${USER}

RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/test.txt"

# -----------------------------------------------------------------------------
# development environment
# -----------------------------------------------------------------------------

# FROM base AS develop

# USER root

# RUN apt-get install -y vim make curl git tree jq

# USER ${USER}

# RUN /usr/local/bin/python -m pip install -r "${APP_REQUIREMENTS}/dev.txt"

# # Fording local host users ssh keys to access the repository.
# # SSH key is forwarded through Docker-compose as a Secret.
# RUN mkdir -m 700 ${HOMEDIR}/.ssh

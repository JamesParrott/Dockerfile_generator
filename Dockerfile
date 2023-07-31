ARG BASE_IMAGE=debian
ARG BASE_TAG=bullseye-slim


FROM ${BASE_IMAGE}:${BASE_TAG} as heirloom_builder

RUN apt-get update -y && \
    apt-get install -y \
    make \
    gcc \
    bzip2 \
    wget

WORKDIR /tmp

RUN wget http://downloads.sourceforge.net/heirloom/heirloom-sh-050706.tar.bz2

RUN tar -jxvf heirloom-sh-050706.tar.bz2

RUN cd heirloom-sh-050706 && \
    make

RUN mkdir -p /tmp/runner_root_dir/bin/

RUN cp heirloom-sh-050706/sh /tmp/runner_root_dir/bin/heirloom-sh


FROM "${BASE_IMAGE}:${BASE_TAG}"

RUN apt-get update -y && \
    apt-get install -y \
    csh \
    tcsh \
    ksh \
    zsh \
    fish \
    ash \
    dash

COPY --from=heirloom_builder /tmp/runner_root_dir /



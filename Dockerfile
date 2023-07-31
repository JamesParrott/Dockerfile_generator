
ARG BASE_IMAGE=alpine
ARG BASE_TAG=edge

FROM ${BASE_IMAGE}:${BASE_TAG} as rc_builder

RUN apk update --no-cache

RUN apk add \
    gcc \
    libc-dev \
    linux-headers \
    perl \ 
    git

ENV PLAN9=/usr/local/plan9

WORKDIR $PLAN9
RUN git clone --depth=1 https://github.com/9fans/plan9port . 
RUN ./INSTALL



RUN mkdir -p /tmp/runner_root_dir/usr/local

RUN mv /usr/local/plan9 /tmp/runner_root_dir/usr/local



FROM "${BASE_IMAGE}:${BASE_TAG}"

RUN apk add --no-cache \
    ion-shell \
    tcsh \
    oksh \
    zsh \
    fish \
    bash \
    dash

RUN apk add --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing/ elvish

COPY --from=rc_builder /tmp/runner_root_dir/ /



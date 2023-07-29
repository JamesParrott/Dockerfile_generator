
ARG BASE_IMAGE=alpine
ARG BASE_TAG=edge


FROM ${BASE_IMAGE}:${BASE_TAG} as heirloom_builder

WORKDIR /tmp

COPY ./source_builds/heirloom/build_heirloom.sh .

RUN ./build_heirloom.sh


FROM ${BASE_IMAGE}:${BASE_TAG} as rc_builder

WORKDIR /tmp

COPY ./source_builds/rc/build_rc.sh .

RUN ./build_rc.sh

COPY --from=heirloom_builder /tmp/runner_root_dir/ /tmp/runner_root_dir/


FROM "${BASE_IMAGE}:${BASE_TAG}"

RUN apk add --no-cache \
    bash \
    dash \
    fish \
    zsh \
    tcsh \
    ion-shell \
    oksh

RUN apk add --no-cache --repository=https://dl-cdn.alpinelinux.org/alpine/edge/testing/  \
    elvish

COPY --from=rc_builder /tmp/runner_root_dir/ /

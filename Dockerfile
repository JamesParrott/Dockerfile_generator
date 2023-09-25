
ARG BASE_IMAGE=ubuntu
ARG BASE_TAG=jammy

FROM "${BASE_IMAGE}:${BASE_TAG}"

RUN apt-get update -y && \
    DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    cmake \
    gcc \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*



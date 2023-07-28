ARG base_image=alpine
ARG base_image_tag=3.18.2
ARG build_step=build_scratch

FROM build_step as builder

FROM base_image as base

COPY builder:/all_the_shells base:/


ARG PKG_MGR_APPS
ENV PKG_MGR_APPS=${PKG_MGR_APPS:-"bash"}
RUN apk add --no-cache ${PKG_MGR_APPS}

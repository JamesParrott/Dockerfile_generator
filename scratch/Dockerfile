FROM alpine:3.18.2
ARG PACKAGES
ENV PACKAGES=${PACKAGES:-"git bash"}
RUN apk add --no-cache ${PACKAGES}
CMD ash

# / # zip
# ash: zip: not found
# / # curl
# ash: curl: not found
# / # tmux
# ash: tmux: not found
# / # htop
# ash: htop: not found
# / # nano
# ash: nano: not found
# / # vi
# / # vim
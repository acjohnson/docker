FROM debian:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV PLEX_HOST_SSH_KEY=id_rsa
ENV PLEX_HOST_USER=root
ENV PLEX_HOST_IP=1.2.3.4
ENV PLEX_PKCS12_PATH=/etc/ssl/certs/plexkey.pfx

COPY ./entrypoint.sh /entrypoint.sh

RUN apt update && \
    apt dist-upgrade -y && \
    apt install --no-install-recommends -y bash apt-utils openssh-client coreutils

ENTRYPOINT ["/entrypoint.sh"]

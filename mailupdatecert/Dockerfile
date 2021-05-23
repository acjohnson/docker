FROM debian:latest

ENV DEBIAN_FRONTEND=noninteractive
ENV MAIL_HOST_SSH_KEY=id_rsa
ENV MAIL_HOST_USER=root
ENV MAIL_HOST_IP=1.2.3.4
ENV MAIL_FULLCHAIN_PATH=/etc/letsencrypt/live/pcdomain.com/fullchain.pem
ENV MAIL_PRIVKEY_PATH=/etc/letsencrypt/live/pcdomain.com/privkey.pem
ENV MAIL_CERT_PATH=/etc/letsencrypt/live/pcdomain.com/cert.pem
ENV MAIL_CHAIN_PATH=/etc/letsencrypt/live/pcdomain.com/chain.pem

COPY ./entrypoint.sh /entrypoint.sh

RUN apt update && \
    apt dist-upgrade -y && \
    apt install --no-install-recommends -y bash apt-utils openssh-client coreutils

ENTRYPOINT ["/entrypoint.sh"]

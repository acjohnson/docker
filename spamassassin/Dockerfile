# Spamassassin 4.0.1 docker image based on debian-sid

FROM debian:sid

ENV DEBIAN_FRONTEND=noninteractive

ADD ./etc /etc

RUN apt update && \
    apt dist-upgrade -y && \
    apt install --no-install-recommends -y ca-certificates bash apt-utils sudo procps pyzor razor gpg gpg-agent && \
    apt install \
      -y \
      --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      sa-compile spamassassin spamc spamd

EXPOSE 783

CMD ["/etc/init.d/spamassassin", "start"]

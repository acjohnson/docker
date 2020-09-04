# Spamassassin 4.0.0 docker image based on debian-experimental

FROM debian:experimental

ENV DEBIAN_FRONTEND=noninteractive

ADD ./etc /etc

RUN apt update && \
    apt dist-upgrade -y && \
    apt install --no-install-recommends -y ca-certificates bash apt-utils sudo procps pyzor razor && \
    apt -t experimental install \
      -y \
      --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      sa-compile spamassassin spamc

EXPOSE 783

CMD ["/etc/init.d/spamassassin", "start"]

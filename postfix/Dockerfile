# Postfix docker image based on debian bullseye-backports

FROM debian:bullseye-backports

ENV DEBIAN_FRONTEND=noninteractive

ADD ./etc /etc

RUN apt update && \
    apt dist-upgrade -y && \
    apt install --no-install-recommends -y ca-certificates bash apt-utils gpg gpg-agent procps iproute2 && \
    apt install \
      -y \
      --no-install-recommends \
      -o Dpkg::Options::="--force-confdef" \
      -o Dpkg::Options::="--force-confold" \
      postfix

EXPOSE 587
EXPOSE 25

CMD ["/etc/init.d/postfix", "start"]

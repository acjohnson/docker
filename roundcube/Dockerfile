FROM roundcube/roundcubemail:1.6.7-apache

ENV COMPOSER_ALLOW_SUPERUSER=1

RUN set -ex; \
    apt-get update; apt-get dist-upgrade -y; \
    apt-get install -y --no-install-recommends git unzip; \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

COPY composer.json /usr/src/roundcubemail/

RUN rm -f /usr/src/roundcubemail/composer.lock; \
    rm -f /usr/src/roundcubemail/composer.json-dist

RUN set -ex; \
    composer \
        --working-dir=/usr/src/roundcubemail/ \
        --prefer-dist \
        --prefer-stable \
        --no-interaction \
        --optimize-autoloader \
        --apcu-autoloader \
        update;

RUN rm -f /usr/src/roundcubemail/plugins/twofactor_gauthenticator/config.inc.php

COPY docker-entrypoint.sh /

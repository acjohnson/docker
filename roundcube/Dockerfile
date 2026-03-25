FROM roundcube/roundcubemail:1.6.14-apache AS builder

ENV COMPOSER_ALLOW_SUPERUSER=1

RUN set -ex; \
    apt-get update; apt-get dist-upgrade -y; \
    apt-get install -y --no-install-recommends git unzip; \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer

WORKDIR /usr/src/roundcubemail

# Merge plugin deps into existing composer.json
RUN composer config repositories.acjohnson-filters vcs https://gitlab.thejohnsons.site/acjohnson/roundcube-plugin-filters.git \
 && composer config repositories.acjohnson-advanced_search vcs https://gitlab.thejohnsons.site/acjohnson/roundcube-plugin-advanced_search.git \
 && composer require --update-no-dev --optimize-autoloader \
      acjohnson/filters:dev-master \
      acjohnson/advanced_search:dev-master \
      alexandregz/twofactor_gauthenticator:dev-master

FROM roundcube/roundcubemail:1.6.14-apache

# Copy the fully-built plugins
COPY --from=builder /usr/src/roundcubemail/plugins/filters /usr/src/roundcubemail/plugins/filters
COPY --from=builder /usr/src/roundcubemail/plugins/advanced_search /usr/src/roundcubemail/plugins/advanced_search
COPY --from=builder /usr/src/roundcubemail/plugins/twofactor_gauthenticator /usr/src/roundcubemail/plugins/twofactor_gauthenticator

RUN rm -f /usr/src/roundcubemail/plugins/twofactor_gauthenticator/config.inc.php

COPY docker-entrypoint.sh /

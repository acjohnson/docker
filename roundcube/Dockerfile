FROM roundcube/roundcubemail:1.7.3-apache AS builder

ENV COMPOSER_ALLOW_SUPERUSER=1

RUN set -ex; \
    apt-get update; apt-get dist-upgrade -y; \
    apt-get install -y --no-install-recommends git unzip npm nodejs; \
    curl -sS https://getcomposer.org/installer | php -- --install-dir=/usr/bin --filename=composer; \
    npm install -g less less-plugin-clean-css

WORKDIR /usr/src/roundcubemail

# Merge plugin deps into existing composer.json
RUN composer config repositories.acjohnson-filters vcs https://gitlab.thejohnsons.site/acjohnson/roundcube-plugin-filters.git \
 && composer config repositories.acjohnson-advanced_search vcs https://gitlab.thejohnsons.site/acjohnson/roundcube-plugin-advanced_search.git \
 && composer require --update-no-dev --optimize-autoloader \
      acjohnson/filters:dev-master \
      acjohnson/advanced_search:dev-master \
      alexandregz/twofactor_gauthenticator:dev-master \
      johndoh/contextmenu:dev-master

# Clone and prepare PrimitiveNotes plugin
RUN git clone https://gitlab.thejohnsons.site/acjohnson/roundcube_primitivenotes.git plugins/primitivenotes \
 && cp plugins/primitivenotes/config.inc.php.dist plugins/primitivenotes/config.inc.php

# Create _styles.less
RUN cat <<EOF > skins/elastic/styles/_styles.less
/* Change unread message bullet to yellow/gold */
.messagelist tr.unread td span.status::before,
.messagelist tr.unread td span.msgicon::before,
.messagelist tr.unread td.subject::before {
    color: #ffc107 !important;
}
/* Ensure text stands out in Dark Mode */
html.layout-dark .messagelist tr.unread td {
    color: #ffffff !important;
}
EOF

# Compile CSS files
RUN cd skins/elastic && \
    lessc --clean-css="--s1 --advanced" styles/styles.less > styles/styles.css && \
    lessc --clean-css="--s1 --advanced" styles/styles.less > styles/styles.min.css

FROM roundcube/roundcubemail:1.7.3-apache

# Install YAML extension in the runtime stage
RUN apt-get update && apt-get install -y libyaml-dev \
    && pecl install yaml \
    && docker-php-ext-enable yaml \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copy the fully-built plugins
COPY --from=builder /usr/src/roundcubemail/plugins/filters /usr/src/roundcubemail/plugins/filters
COPY --from=builder /usr/src/roundcubemail/plugins/advanced_search /usr/src/roundcubemail/plugins/advanced_search
COPY --from=builder /usr/src/roundcubemail/plugins/twofactor_gauthenticator /usr/src/roundcubemail/plugins/twofactor_gauthenticator
COPY --from=builder /usr/src/roundcubemail/plugins/contextmenu /usr/src/roundcubemail/plugins/contextmenu
COPY --from=builder /usr/src/roundcubemail/plugins/primitivenotes /usr/src/roundcubemail/plugins/primitivenotes

# Copy the compiled CSS files
COPY --from=builder /usr/src/roundcubemail/skins/elastic/styles/styles.css /usr/src/roundcubemail/skins/elastic/styles/styles.css
COPY --from=builder /usr/src/roundcubemail/skins/elastic/styles/styles.min.css /usr/src/roundcubemail/skins/elastic/styles/styles.min.css

# Cleanup
RUN rm -f /usr/src/roundcubemail/plugins/twofactor_gauthenticator/config.inc.php
RUN rm -f /usr/src/roundcubemail/public_html/installer.php

COPY docker-entrypoint.sh /

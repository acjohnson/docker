#!/bin/bash -x

set -e -o pipefail

/usr/bin/scp -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$MAIL_HOST_SSH_KEY \
    /tls.crt \
    $MAIL_HOST_USER@$MAIL_HOST_IP:$MAIL_FULLCHAIN_PATH

/usr/bin/scp -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$MAIL_HOST_SSH_KEY \
    /tls.crt \
    $MAIL_HOST_USER@$MAIL_HOST_IP:$MAIL_CERT_PATH

/usr/bin/scp -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$MAIL_HOST_SSH_KEY \
    /tls.crt \
    $MAIL_HOST_USER@$MAIL_HOST_IP:$MAIL_CHAIN_PATH

/usr/bin/scp -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$MAIL_HOST_SSH_KEY \
    /tls.key \
    $MAIL_HOST_USER@$MAIL_HOST_IP:$MAIL_PRIVKEY_PATH

/usr/bin/ssh -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$MAIL_HOST_SSH_KEY \
    -q $MAIL_HOST_USER@$MAIL_HOST_IP "/bin/systemctl restart postfix; /bin/systemctl restart dovecot; /bin/systemctl status postfix; /bin/systemctl status dovecot"

/bin/sleep infinity

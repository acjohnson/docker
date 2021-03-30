#!/bin/bash -x

set -e -o pipefail

/usr/bin/scp -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$PLEX_HOST_SSH_KEY \
    /keystore.p12 \
    $PLEX_HOST_USER@$PLEX_HOST_IP:$PLEX_PKCS12_PATH

/usr/bin/ssh -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -i /$PLEX_HOST_SSH_KEY \
    -q $PLEX_HOST_USER@$PLEX_HOST_IP "/bin/systemctl restart plexmediaserver; /bin/systemctl status plexmediaserver"

/usr/bin/sleep infinity

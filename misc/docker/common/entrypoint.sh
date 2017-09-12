#!/bin/bash
# set -x

# Get tep args
ARGS=$@
# Get tep executable
EXE=$(which tep-$1)

set -e

if [ "$EXE" != "" ]; then
        USER_UID=${USER_UID:-1000}
        USER_GID=${USER_GID:-1000}

        # create user group
        if ! getent group tep >/dev/null; then
                groupadd -f -g ${USER_GID} tep
        fi

        # create user with uid and gid matching that of the host user
        if ! getent passwd tep >/dev/null; then
                adduser --uid ${USER_UID} --gid ${USER_GID} \
                        --disabled-login \
                        --gecos 'TuxEatPi' tep

        fi
    if [ $# == "1" ];
    then
        echo exec su tep -c "$EXE -w /workdir -I /intents -D /dialogs"
        exec su tep -c "$EXE -w /workdir -I /intents -D /dialogs"
    else
        echo exec su tep -c "$EXE -w /workdir -I /intents -D /dialogs $ARGS"
        exec su tep -c "$EXE -w /workdir -I /intents -D /dialogs $ARGS"
        # OR exec su tep -c "$EXE $ARGS" ????
    fi

else
    echo "tep-$1 executable not found. Running $1"
    exec "$@"
fi

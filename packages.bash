#!/bin/bash
# Run callback & return result to console

MODULE="./callback/packages.py"
PLAYBOOK="packages.yml"

if [ $# -eq 0 ]; then
    python $MODULE $PLAYBOOK
else
    python $MODULE $PLAYBOOK --extra-vars "host=$1"
fi

exit $?

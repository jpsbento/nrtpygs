#!/usr/bin/env bash

# This script will set up the local environment to that the rmqclient library
# and tests can be run locally on the users machine.
echo
echo "=========="
echo "setenv.sh"
echo "=========="
echo
echo "Script to setup the local environment to enable"
echo "usage of the rmqclient library locally, outside"
echo "of the 4mnrt/gsi container image"
echo
echo "IMPORTANT:"
echo "This script can be run in one off and/or permanent mode"
echo
echo "--> One off   - This script will add to environment variables in the current shell"
echo "--> Permanent - This will append to the ~/.profile file so settings are permanent"
echo
echo "NOTE, for one off running you MUST call this script with the current shell, e.g."
echo "$> . /utils/setenv.sh"
echo "The '.<space>' at the beginning of the command achieves this"
echo
echo "Also NOTE:"
echo "You may need to make the type of shell a LOGIN shell in whichever "
echo "Terminal program you use so that the ~/.profile element is run"
while true; do
    read -p "Do you wish to invoke permanent mode? [y/n]" yn
    case $yn in
        [Yy]* ) PERM=true; break;;
        [Nn]* ) PERM=false; break;;
        * ) echo "Please answer yes or no.";;
    esac
done

# First make the python path point to rmqclient
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
TOPDIR=${DIR/\/utils//}
RMQDIR=${DIR/utils/mqclient/}
echo "Adding $RMQDIR to PYTHONPATH"
export PYTHONPATH=$PYTHONPATH:$RMQDIR

# If perm then add this to ~/.profile
if [ "$PERM" = true ] ; then
    echo "Adding to the PYTHONPATH in ~/.profile"
    echo "export PYTHONPATH=\$PYTHONPATH:$RMQDIR" >> ~/.profile
fi


# Set ENV VARS for current shell and change rmq to localhost
echo " Exporting all env vars to the current shell"
export $(grep -v '^#' $TOPDIR/secret.env | xargs)
export $(grep -v '^#' $TOPDIR/environment.env | sed 's/rmq/localhost/' | xargs)


# If perm then add this to ~/.profile
if [ "$PERM" = true ] ; then
    echo "Adding the env vars to export from ~/.profile"
    grep -v '^#' $TOPDIR/secret.env | sed 's/^/export /' >> ~/.profile
    grep -v '^#' $TOPDIR/environment.env | sed 's/rmq/localhost/' | sed 's/^/export /' >> ~/.profile
fi

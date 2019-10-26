#!/usr/bin/env bash

# Fill the VERSION file with the new version, following semantic versioning.
# You MUST run this script from the project's root directory.

# COLORS ######################################################################

Off='\033[0m'             # Text Reset

# Regular Colors
Black='\033[0;30m'        # Black
Red='\033[0;31m'          # Red
Green='\033[0;32m'        # Green
Yellow='\033[0;33m'       # Yellow
Blue='\033[0;34m'         # Blue
Purple='\033[0;35m'       # Purple
Cyan='\033[0;36m'         # Cyan
White='\033[0;37m'        # White

# BUSINESS ####################################################################

MY_DIR="${0%/*}"
VERSION=`git describe --tags`
echo -e "${Green}Setting new version : ${Yellow}${VERSION}${Off}"
echo ${VERSION} > ${MY_DIR}/../VERSION

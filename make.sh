#!/bin/bash

set -e

cd $(dirname $0)
rm -rf www
complexity --noserver website
echo 'gitdir: ../.git/modules/www' > www/.git

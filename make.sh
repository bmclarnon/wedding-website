#!/bin/sh

rm -rf www
complexity --noserver website
echo 'gitdir: ../.git/modules/www' > www/.git

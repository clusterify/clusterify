#!/bin/bash

# WARNING: this also deletes the db. Comment that line if you'll
# manually make sure it doesn't get in the repos.

find . -name "*.pyc" -exec rm {} \;
find . -name "*~" -exec rm {} \;

rm "db.sqlite"
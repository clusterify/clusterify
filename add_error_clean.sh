#!/bin/bash

find . -name '*.pyc' | xargs svn remove --force $1

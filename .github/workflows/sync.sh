#!/bin/bash

# Only need to sync images that changed in current commit
FILES=$(find online -type f)

for FILE in $FILES
do
     echo "========> Syncing: $FILES <========"
    ./image-syncer --auth=./auth.yaml --images=${FILE}
done
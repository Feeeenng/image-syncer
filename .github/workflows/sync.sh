#!/bin/bash

# Only need to sync images that changed in current commit
FILES=$(find online -type f)

for FILE in $FILES
do
     echo "========> Syncing: $FILES <========"
    ./image-syncer --auth=./auth.yaml --proc=10 --retries=5 --timeout=300 --skip-check --images=${FILE}
done

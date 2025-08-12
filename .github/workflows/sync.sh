#!/bin/bash

# Only need to sync images that changed in current commit
#FILES=$(find online -type f)

#for FILE in $FILES
#do
    # echo "========> Syncing: $FILES <========"
./image-syncer --auth=./auth.yaml --proc=3 --retries=5 --images=online/tencent.yaml
#done

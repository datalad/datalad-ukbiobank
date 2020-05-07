#!/bin/bash

# If you already have a download of the UKbiobank, swap out the actual `ukbfetch`
# with something like this script to be able to skip the download when generating
# DataLad datasets. It parses the `.ukbbatch` file created by `ukb-init`, and simply
# copies the zip files from wherever they are stored.

set -e

for line in $(cat .ukbbatch |  sed 's/ /,/g'); do
    sub_id=${line%,*}
    modality=${line#*,}

    # transfer data from remote server
    rsync -avh --progress me@remote.server.de:"/ukbiobank/zip_files/${sub_id}_${modality}*" ./

done

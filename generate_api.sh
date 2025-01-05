#!/bin/bash

# Get current user's UID and GID
USER_UID=$(id -u)
USER_GID=$(id -g)

# Run Kiota to generate the API client
docker run --user $USER_UID:$USER_GID -v ${PWD}:/app/output mcr.microsoft.com/openapi/kiota \
    generate \
    --language python \
    --class-name ApiClient \
    --namespace-name knmi_dataset_api \
    --openapi https://tyk-cdn.dataplatform.knmi.nl/open-data/openapi.json \
    --deserializer kiota_serialization_json.json_parse_node_factory.JsonParseNodeFactory \
    --output /app/output/src/knmi_dataset_downloader/knmi_dataset_api 
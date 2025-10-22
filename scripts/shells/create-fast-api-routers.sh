fastapi-codegen \
    --input backend/contracts/firstcontract.yaml \
    --output ./test-app-generation-routers \
    --generate-routers \
    --python-version 3.11 \
    --model-file backend/app/models/contract-models.py
#!/bin/bash -e

# 656532927350
ACCOUNT_ID=$1
# path/to/example.yaml
TEMPLATE_FILENAME=$2
# DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME
S3_BUCKET=$3
# ExampleStackName
STACK_NAME=$4
# s3-path-prefix
S3_PREFIX=$5
S3_PREFIX_ARG="--s3-prefix $S3_PREFIX"

# Optional arguments

# "CustomDomainName=foo.example.com DomainNameZone=example.com. CertificateArn=arn:aws:acm:region:123456789012:certificate/12345678-1234-1234-1234-123456789012"
if [ "$6" != "none" ]; then
  PARAMETER_OVERRIDES=$6
fi

# ApiEndpointUrl
if [ "$7" != "none" ]; then
  OUTPUT_VAR_NAME=$7
fi

# Confirm that we have access to AWS and we're in the right account
set +e
result="$(aws sts get-caller-identity --output text 2>&1)"
if ! echo "$result" | grep 'arn:aws:sts' >/dev/null; then
  echo "Error : $result"
  exit 1
elif ! echo "$result" | grep "$ACCOUNT_ID" >/dev/null; then
  echo "Wrong AWS account : $result"
  exit 1
fi
set -e

mkdir -p "build-$STACK_NAME"

docker run --entrypoint pip \
    --platform linux/amd64 \
    --workdir /src \
    --volume "$(pwd)":/src:ro \
    --volume "$(pwd)/build-$STACK_NAME":/build:rw \
    -it python:3.12 \
    install \
        --target "/build/" \
        -r requirements.txt

# https://unix.stackexchange.com/a/180987/22701
cp -v -R "functions/." "build-$STACK_NAME/"

# Required, because we use `Code:` in the cloudformation template.
ln -Ffs "./build-$STACK_NAME" "./build"

aws cloudformation package \
  --template $TEMPLATE_FILENAME \
  --s3-bucket $S3_BUCKET \
  $S3_PREFIX_ARG \
  --output-template-file "output-$STACK_NAME.yaml"

if [ "$(aws cloudformation describe-stacks --query "length(Stacks[?StackName=='${STACK_NAME}'])")" = "1" ]; then
  # Stack already exists, it will be updated
  wait_verb=stack-update-complete
else
  # Stack doesn't exist it will be created
  wait_verb=stack-create-complete
fi

set +e
if aws cloudformation deploy --template-file "output-$STACK_NAME.yaml" --stack-name $STACK_NAME \
    --capabilities CAPABILITY_IAM \
    --parameter-overrides \
      $PARAMETER_OVERRIDES; then
  echo "Waiting for stack to reach a COMPLETE state"
  if aws cloudformation wait $wait_verb --stack-name  $STACK_NAME; then
    if [ "$OUTPUT_VAR_NAME" ]; then
      aws cloudformation describe-stacks --stack-name $STACK_NAME --query "Stacks[0].Outputs[?OutputKey=='${OUTPUT_VAR_NAME}'].OutputValue" --output text
    fi
    exit 0
  fi
fi
aws cloudformation describe-stack-events \
  --stack-name $STACK_NAME \
  --query 'StackEvents[?ends_with(ResourceStatus, `_FAILED`)].[LogicalResourceId, ResourceType, ResourceStatusReason]' \
  --output text
exit 1

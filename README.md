# auth0-cis-webhook-consumer

An API Gateway and AWS Lambda webhook consumer that consumes 
[webhook POSTs from CIS](https://github.com/mozilla-iam/cis/blob/master/docs/Hooks.md)
and in response
* Verifies the authorization token in the header is valid
* Fetches the user profile for the user ID passed
* Cleans the group names
* Publishes those group changes to the Auth0 management API to update the user's
  profile in Auth0

The design of this (Makefile with deploy.sh which uses AWS CLI to package
and deploy the tool) differs from other CIS projects (serverless command line
tool with serverless.yml to deploy). In the long run I hope to change this to
fit with the style of other CIS components but for the moment, this is faster
for me to get this up and running.

# Testing

## Deploy in dev

Run this in the `mozilla-iam` AWS account
```
export AWS_DEFAULT_REGION="us-east-1"
make deploy-dev
```

## Query

```
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/test
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/error
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/post
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/404
```
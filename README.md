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

# Architecture

* `auth0-cis-webhook-consumer.dev.sso.allizom.org.` DNS record in `mozilla-iam`
  AWS account is an alias to AWS API Gateway
* API Gateway proxies all request to AWS Lambda function
* Lambda function calls appropriate Python function based on the URL path in the
  request

# Deploy

## Provision Auth0 Clients

This is a one time step.

In order to grant the Auth0 CIS Webhook Consumer rights to query the CIS PersonAPI
an Auth0 application/client needs to be provisioned. 
[These instructions show how to provision a new Auth0 application/client](https://github.com/mozilla-iam/cis/blob/master/docs/PersonAPI.md#how-are-these-credentials-provisioned-in-auth0).
Create clients in the `auth0` and `auth0-dev` environments. Select the following scopes
* `classification:public`
* `display:none`

which will permit the client to read the `ldap` and `mozilliansorg` values in the
`access_information` portion of the [user profile](https://auth.mozilla.com/.well-known/profile.schema).

## Record Client ID and Secret

Once the Auth0 application/clients are provisioned, store the resulting `client_id` and `client_secret`.
The `client_id` is public data and should be stored in the [`Makefile`](Makefile)
in the following variables
* `PROD_CLIENT_ID`
* `DEV_CLIENT_ID`
* `TEST_CLIENT_ID`

The `client_secret` should be stored in AWS System Manager Parameter Store as a
`SecureString` with the following parameter names
* `/iam/cis/production/auth0_cis_webhook_consumer/client_secret`
* `/iam/cis/development/auth0_cis_webhook_consumer/client_secret`
* `/iam/cis/testing/auth0_cis_webhook_consumer/client_secret`

## Deploy in dev

Run this in the `mozilla-iam` AWS account
```
export AWS_DEFAULT_REGION="us-east-1"
make deploy-dev
```

# Testing

## Query

```
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/test
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/error
curl -d '{"foo": "bar"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/404
curl -H  "Authorization: Bearer YOUR_TOKEN_HERE" \
  -d '{"operation": "update", id": "ad|Mozilla-LDAP|dinomcvouch"}' -i \
  https://auth0-cis-webhook-consumer.dev.sso.allizom.org/post
```

# Problems with the dev environment

These problems would need to be fixed to be able to use this in dev
* The URL https://auth.allizom.org/.well-known/openid-configuration doesn't
  correctly proxy the request on to https://auth-dev.mozilla.auth0.com/.well-known/openid-configuration
  * https://github.com/mozilla-iam/cis/issues/239#issuecomment-633789313
* https://person.api.dev.sso.allizom.org appears to return 500 errors

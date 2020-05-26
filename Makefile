DEV_API_STACK_NAME	:= auth0-cis-webhook-consumer-development
PROD_API_STACK_NAME	:= auth0-cis-webhook-consumer-testing
TEST_API_STACK_NAME	:= auth0-cis-webhook-consumer-production
CODE_STORAGE_S3_PREFIX := auth0-cis-webhook-consumer
PROD_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME := public.us-east-1.iam.mozilla.com
DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME  := public.us-east-1.iam.mozilla.com
TEST_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME  := public.us-east-1.iam.mozilla.com
PROD_DOMAIN_NAME	:= auth0-cis-webhook-consumer.sso.mozilla.com
DEV_DOMAIN_NAME		:= auth0-cis-webhook-consumer.dev.sso.allizom.org
TEST_DOMAIN_NAME	:= auth0-cis-webhook-consumer.test.sso.allizom.org
ACCOUNT_ID			:= 320464205386
PROD_DOMAIN_ZONE	:= sso.mozilla.com.
DEV_DOMAIN_ZONE		:= sso.allizom.org.
TEST_DOMAIN_ZONE	:= sso.allizom.org.
PROD_CERT_ARN		:= arn:aws:acm:us-east-1:320464205386:certificate/17c2229f-5dff-4818-aa71-34516faefaf8
DEV_CERT_ARN		:= arn:aws:acm:us-east-1:320464205386:certificate/f829822f-e9b5-4bcd-a624-1dc1270ddf8d
TEST_CERT_ARN		:= arn:aws:acm:us-east-1:320464205386:certificate/b7d6a423-23c6-40df-8334-32353c83ca82

PROD_ENVIRONMENT_NAME	:= production
DEV_ENVIRONMENT_NAME	:= development
TEST_ENVIRONMENT_NAME	:= testing

PROD_DISCOVERY_URL	:= https://auth.mozilla.com/.well-known/mozilla-iam
# https://github.com/mozilla-iam/cis/issues/239
DEV_DISCOVERY_URL	:= https://auth.allizom.org/.well-known/mozilla-iam
TEST_DISCOVERY_URL	:= https://auth.mozilla.com/.well-known/mozilla-iam

PROD_NOTIFICATION_AUDIENCE		:= pDjd8bJqoaeIAdLfMx9j7mQ9OiDeibla
DEV_NOTIFICATION_AUDIENCE		:= T281KFOlJVuc0YZjfcyb8u99qCBi5ukJ
# TODO : I'm unsure why this client_id is stored in the parameter store field for testing, it doesn't look like an Auth0 client_id
TEST_NOTIFICATION_AUDIENCE		:= hkqJ31Ay8s4qNmlfsfRoxN81debp_tvDT2KPAuFROUbnNkywcMBlKWUBuGnqi9rc

PROD_CLIENT_ID		:= ztz01UXzlek7oGIn4b4s1wh3FGEHwtXj
DEV_CLIENT_ID		:= Vh35EgJf4ZPK1BPSQW4qVmcnSnWgPtC9
TEST_CLIENT_ID		:= ztz01UXzlek7oGIn4b4s1wh3FGEHwtXj

.PHONY: deploy-dev
deploy-dev:
	./deploy.sh \
		$(ACCOUNT_ID) \
		 auth0-cis-webhook-consumer.yaml \
		 $(DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(DEV_API_STACK_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(DEV_DOMAIN_NAME) \
		 	DomainNameZone=$(DEV_DOMAIN_ZONE) \
		 	CertificateArn=$(DEV_CERT_ARN) \
			EnvironmentName=$(DEV_ENVIRONMENT_NAME) \
			DiscoveryUrl=$(DEV_DISCOVERY_URL) \
			NotificationAudience=$(DEV_NOTIFICATION_AUDIENCE) \
			ClientId=$(DEV_CLIENT_ID)" \
		 Auth0CISWebHookConsumerUrl


API_STACK_NAME	:= auth0-cis-webhook-consumer
CODE_STORAGE_S3_PREFIX := auth0-cis-webhook-consumer
PROD_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME := public.us-west-2.iam.mozilla.com
DEV_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME  := public.us-west-2.iam.mozilla.com
TEST_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME  := public.us-west-2.iam.mozilla.com
PROD_DOMAIN_NAME	:= auth0-cis-webhook-consumer.sso.mozilla.com
DEV_DOMAIN_NAME		:= auth0-cis-webhook-consumer.dev.sso.allizom.org
TEST_DOMAIN_NAME	:= auth0-cis-webhook-consumer.test.sso.allizom.org
ACCOUNT_ID			:= 320464205386
PROD_DOMAIN_ZONE	:= sso.mozilla.com.
DEV_DOMAIN_ZONE		:= sso.allizom.org.
TEST_DOMAIN_ZONE	:= sso.allizom.org.
PROD_CERT_ARN		:= arn:aws:acm:us-west-2:320464205386:certificate/70c31e6e-c602-4e73-8d32-838e4d729af3
DEV_CERT_ARN		:= arn:aws:acm:us-west-2:320464205386:certificate/dbd85ef3-a903-4d8d-a176-7cb472fce46f
TEST_CERT_ARN		:= arn:aws:acm:us-west-2:320464205386:certificate/2f32f7e1-a269-440b-9cb8-96da63d9b00a

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
		 $(API_STACK_NAME)-$(DEV_ENVIRONMENT_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(DEV_DOMAIN_NAME) \
		 	DomainNameZone=$(DEV_DOMAIN_ZONE) \
		 	CertificateArn=$(DEV_CERT_ARN) \
			EnvironmentName=$(DEV_ENVIRONMENT_NAME) \
			DiscoveryUrl=$(DEV_DISCOVERY_URL) \
			NotificationAudience=$(DEV_NOTIFICATION_AUDIENCE) \
			ClientId=$(DEV_CLIENT_ID)" \
		 Auth0CISWebHookConsumerUrl

.PHONY: deploy
deploy:
	./deploy.sh \
		$(ACCOUNT_ID) \
		 auth0-cis-webhook-consumer.yaml \
		 $(PROD_LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(API_STACK_NAME)-$(PROD_ENVIRONMENT_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(PROD_DOMAIN_NAME) \
		 	DomainNameZone=$(PROD_DOMAIN_ZONE) \
		 	CertificateArn=$(PROD_CERT_ARN) \
			EnvironmentName=$(PROD_ENVIRONMENT_NAME) \
			DiscoveryUrl=$(PROD_DISCOVERY_URL) \
			NotificationAudience=$(PROD_NOTIFICATION_AUDIENCE) \
			ClientId=$(PROD_CLIENT_ID)" \
		 Auth0CISWebHookConsumerUrl


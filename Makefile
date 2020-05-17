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
PROD_AUDIENCE		:= hook.sso.mozilla.com
DEV_AUDIENCE		:= hook.dev.sso.allizom.org
TEST_AUDIENCE		:= hook.test.sso.allizom.org

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
			WebHookTokenAudience=$(DEV_AUDIENCE)" \
		 Auth0CISWebHookConsumerUrl


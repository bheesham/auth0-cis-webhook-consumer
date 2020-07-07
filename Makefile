API_STACK_NAME	:= a0-cis-hook-consumer
CODE_STORAGE_S3_PREFIX := auth0-cis-webhook-consumer
LAMBDA_CODE_STORAGE_S3_BUCKET_NAME := public.us-west-2.iam.mozilla.com
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

PROD_PERSONAPI_CLIENT_ID		:= ztz01UXzlek7oGIn4b4s1wh3FGEHwtXj
PROD_MANAGEMENT_API_CLIENT_ID	:= kG1kIwfT7tVANi6bIsZ1ZXWqjTFyJYAg
DEV_MANAGEMENT_API_CLIENT_ID	:= Vh35EgJf4ZPK1BPSQW4qVmcnSnWgPtC9

# https://github.com/mozilla-iam/cis/blob/a785c367c533e76a5935b456351453efdc2740b9/serverless-functions/webhook_notifier/serverless.yml#L23-L26
# CIS Webhook notifier uses prod Auth0 for all 3 environments
PROD_NOTIFICATION_DISCOVERY_URL	:= https://auth.mozilla.com/.well-known/mozilla-iam

# https://github.com/mozilla-iam/cis/blob/a785c367c533e76a5935b456351453efdc2740b9/serverless-functions/profile_retrieval/serverless.yml#L24-L27
# PersonAPI uses prod Auth0 for all 3 environments
PROD_PERSONAPI_DISCOVERY_URL	:= https://auth.mozilla.auth0.com/.well-known/openid-configuration

# https://github.com/mozilla-iam/cis/blob/a785c367c533e76a5935b456351453efdc2740b9/serverless-functions/profile_retrieval/serverless.yml#L16-L19
PROD_PERSONAPI_AUDIENCE		:= api.sso.mozilla.com
DEV_PERSONAPI_AUDIENCE		:= api.dev.sso.allizom.org
TEST_PERSONAPI_AUDIENCE		:= api.test.sso.allizom.org

# https://github.com/mozilla-iam/cis/blob/a785c367c533e76a5935b456351453efdc2740b9/serverless-functions/webhook_notifier/serverless.yml#L15-L18
PROD_NOTIFICATION_AUDIENCE		:= hook.sso.mozilla.com
DEV_NOTIFICATION_AUDIENCE		:= hook.dev.sso.allizom.org
TEST_NOTIFICATION_AUDIENCE		:= hook.test.sso.allizom.org

# https://auth0.com/docs/api/management/v2/#Authentication
PROD_MANAGEMENT_DISCOVERY_URL	:= https://auth.mozilla.auth0.com/.well-known/openid-configuration
DEV_MANAGEMENT_DISCOVERY_URL	:= https://auth-dev.mozilla.auth0.com/.well-known/openid-configuration
PROD_MANAGEMENT_API_AUDIENCE	:= https://auth.mozilla.auth0.com/api/v2/
DEV_MANAGEMENT_API_AUDIENCE		:= https://auth-dev.mozilla.auth0.com/api/v2/

# USER_WHITELIST	:= ad|Mozilla-LDAP|gene,ad|Mozilla-LDAP|FMerz,ad|Mozilla-LDAP-Dev|gene,ad|Mozilla-LDAP-Dev|FMerz,ad|Mozilla-LDAP|hcondei,ad|Mozilla-LDAP-Dev|hcondei
USER_WHITELIST	:= ""

.PHONY: deploy-dev
deploy-dev:
	./deploy.sh \
		$(ACCOUNT_ID) \
		 auth0-cis-webhook-consumer.yaml \
		 $(LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(API_STACK_NAME)-$(DEV_ENVIRONMENT_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(DEV_DOMAIN_NAME) \
		 	DomainNameZone=$(DEV_DOMAIN_ZONE) \
		 	CertificateArn=$(DEV_CERT_ARN) \
			EnvironmentName=$(DEV_ENVIRONMENT_NAME) \
			UserWhitelist=$(USER_WHITELIST) \
			NotificationDiscoveryUrl=$(PROD_NOTIFICATION_DISCOVERY_URL) \
			NotificationAudience=$(DEV_NOTIFICATION_AUDIENCE) \
			PersonAPIDiscoveryUrl=$(PROD_PERSONAPI_DISCOVERY_URL) \
			PersonAPIClientID=$(PROD_PERSONAPI_CLIENT_ID) \
			PersonAPIAudience=$(DEV_PERSONAPI_AUDIENCE) \
			ManagementAPIClientID=$(DEV_MANAGEMENT_API_CLIENT_ID) \
			ManagementAPIAudience=$(DEV_MANAGEMENT_API_AUDIENCE) \
			ManagementAPIDiscoveryUrl=$(DEV_MANAGEMENT_DISCOVERY_URL)" \
		 Auth0CISWebHookConsumerUrl

deploy-test:
	./deploy.sh \
		$(ACCOUNT_ID) \
		 auth0-cis-webhook-consumer.yaml \
		 $(LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(API_STACK_NAME)-$(TEST_ENVIRONMENT_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(TEST_DOMAIN_NAME) \
		 	DomainNameZone=$(TEST_DOMAIN_ZONE) \
		 	CertificateArn=$(TEST_CERT_ARN) \
			EnvironmentName=$(TEST_ENVIRONMENT_NAME) \
			UserWhitelist=$(USER_WHITELIST) \
			NotificationDiscoveryUrl=$(PROD_NOTIFICATION_DISCOVERY_URL) \
			NotificationAudience=$(TEST_NOTIFICATION_AUDIENCE) \
			PersonAPIDiscoveryUrl=$(PROD_PERSONAPI_DISCOVERY_URL) \
			PersonAPIClientID=$(PROD_PERSONAPI_CLIENT_ID) \
			PersonAPIAudience=$(TEST_PERSONAPI_AUDIENCE) \
			ManagementAPIClientID=$(DEV_MANAGEMENT_API_CLIENT_ID) \
			ManagementAPIAudience=$(DEV_MANAGEMENT_API_AUDIENCE) \
			ManagementAPIDiscoveryUrl=$(DEV_MANAGEMENT_DISCOVERY_URL)" \
		 Auth0CISWebHookConsumerUrl

.PHONY: deploy
deploy:
	./deploy.sh \
		$(ACCOUNT_ID) \
		 auth0-cis-webhook-consumer.yaml \
		 $(LAMBDA_CODE_STORAGE_S3_BUCKET_NAME) \
		 $(API_STACK_NAME)-$(PROD_ENVIRONMENT_NAME) \
		 $(CODE_STORAGE_S3_PREFIX) \
		 "CustomDomainName=$(PROD_DOMAIN_NAME) \
		 	DomainNameZone=$(PROD_DOMAIN_ZONE) \
		 	CertificateArn=$(PROD_CERT_ARN) \
			EnvironmentName=$(PROD_ENVIRONMENT_NAME) \
			UserWhitelist=$(USER_WHITELIST) \
			NotificationDiscoveryUrl=$(PROD_NOTIFICATION_DISCOVERY_URL) \
			NotificationAudience=$(PROD_NOTIFICATION_AUDIENCE) \
			PersonAPIDiscoveryUrl=$(PROD_PERSONAPI_DISCOVERY_URL) \
			PersonAPIClientID=$(PROD_PERSONAPI_CLIENT_ID) \
			PersonAPIAudience=$(PROD_PERSONAPI_AUDIENCE) \
			ManagementAPIClientID=$(PROD_MANAGEMENT_API_CLIENT_ID) \
			ManagementAPIAudience=$(PROD_MANAGEMENT_API_AUDIENCE) \
			ManagementAPIDiscoveryUrl=$(PROD_MANAGEMENT_DISCOVERY_URL)" \
		 Auth0CISWebHookConsumerUrl


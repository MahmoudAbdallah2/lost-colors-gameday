# Creating Cognito User Pool 
import os
import boto3
import cognito_utils as utils



## Create Amazon Cognito Pool for Inbound authorization to Gateway 
# Firstly, will need to create a Cognito user pool that will host the identities for various agents who would want to connect to the Gateway

REGION = boto3.session.Session().region_name
cognito = boto3.client("cognito-idp", region_name=REGION)

USER_POOL_NAME = "agent-to-gateway-pool"
RESOURCE_SERVER_ID = "agent-to-gateway-id"
RESOURCE_SERVER_NAME = "agent-to-gateway-name"
CLIENT_NAME = "agent-to-gateway-client"
SCOPES = [
    {
        "ScopeName": "invoke",  # Just 'invoke', will be formatted as resource_server_id/invoke
        "ScopeDescription": "Scope for invoking the agentcore gateway"
        },
]

scope_names = [f"{RESOURCE_SERVER_ID}/{scope['ScopeName']}" for scope in SCOPES]
scopeString = " ".join(scope_names)


print("Creating or retrieving Cognito resources...")
gw_user_pool_id = utils.get_or_create_user_pool(cognito, USER_POOL_NAME)
print("IDP details for agent-to-gateway ->") 
print(f"User Pool ID: {gw_user_pool_id}")

utils.get_or_create_resource_server(cognito, gw_user_pool_id, RESOURCE_SERVER_ID, RESOURCE_SERVER_NAME, SCOPES)
print("Resource server ensured.")

gw_client_id, gw_client_secret = utils.get_or_create_m2m_client(cognito, gw_user_pool_id, CLIENT_NAME, RESOURCE_SERVER_ID, scope_names)

print(f"Client ID: {gw_client_id}, Client secret: {gw_client_secret}")

# Get discovery URL
gw_cognito_discovery_url = f'https://cognito-idp.{REGION}.amazonaws.com/{gw_user_pool_id}/.well-known/openid-configuration'
print(f"Discovery URL: {gw_cognito_discovery_url}")



REGION = boto3.session.Session().region_name
USER_POOL_NAME = "gateway-to-runtime-pool"
RESOURCE_SERVER_ID = "gateway-to-runtime-id"
RESOURCE_SERVER_NAME = "gateway-to-runtime-name"
CLIENT_NAME = "gateway-to-runtime-client"
SCOPES = [
    {
        "ScopeName": "invoke",  # Just 'invoke', will be formatted as resource_server_id/invoke
        "ScopeDescription": "Scope for invoking the agentcore runtime"
        },
]

scope_names = [f"{RESOURCE_SERVER_ID}/{scope['ScopeName']}" for scope in SCOPES]
runtimeScopeString = " ".join(scope_names)


print("Creating or retrieving Cognito resources...")
runtime_user_pool_id = utils.get_or_create_user_pool(cognito, USER_POOL_NAME)
print("IDP details for gateway-to-tools ->") 
print(f"User Pool ID: {runtime_user_pool_id}")

utils.get_or_create_resource_server(cognito, runtime_user_pool_id, RESOURCE_SERVER_ID, RESOURCE_SERVER_NAME, SCOPES)
print("Resource server ensured.")

runtime_client_id, runtime_client_secret = utils.get_or_create_m2m_client(cognito, runtime_user_pool_id, CLIENT_NAME, RESOURCE_SERVER_ID, scope_names)

print(f"Client ID: {runtime_client_id}, Client secret: {runtime_client_secret}")

# Get discovery URL
runtime_cognito_discovery_url = f'https://cognito-idp.{REGION}.amazonaws.com/{runtime_user_pool_id}/.well-known/openid-configuration'
print(f"Discovery URL: {runtime_cognito_discovery_url}")

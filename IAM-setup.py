#!/usr/bin/env python3
"""
Unified setup script for The Legend of Lost Colors
"""
import boto3
import json
import uuid
from datetime import datetime

def create_lost_colors_role(role_name="LostColors"):
    """Create IAM role with all required permissions"""
    print(f"🔧 Creating IAM role: {role_name}")

    iam = boto3.client('iam')
    sts = boto3.client('sts')
    
    # Get dynamic values
    account_id = sts.get_caller_identity()['Account']
    region = boto3.Session().region_name or 'us-east-1'
    
    # Trust policy
    trust_policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Sid": "AssumeRolePolicy",
                "Effect": "Allow",
                "Principal": {"Service": "bedrock-agentcore.amazonaws.com"},
                "Action": "sts:AssumeRole",
                "Condition": {
                    "StringEquals": {"aws:SourceAccount": account_id},
                    "ArnLike": {"aws:SourceArn": f"arn:aws:bedrock-agentcore:{region}:{account_id}:*"}
                }
            }
        ]
    }
    
    try:
        # Create role
        iam.create_role(
            RoleName=role_name,
            AssumeRolePolicyDocument=json.dumps(trust_policy),
            Description=f"Execution role for BedrockAgentCore Runtime and Gateway - {role_name}"
        )
        
        # Main execution policy
        execution_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Sid": "ECRImageAccess",
                    "Effect": "Allow",
                    "Action": [
                        "ecr:BatchGetImage",
                        "ecr:GetDownloadUrlForLayer"
                    ],
                    "Resource": [
                        f"arn:aws:ecr:{region}:{account_id}:repository/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:DescribeLogStreams",
                        "logs:CreateLogGroup"
                    ],
                    "Resource": [
                        f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:DescribeLogGroups"
                    ],
                    "Resource": [
                        f"arn:aws:logs:{region}:{account_id}:log-group:*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "logs:CreateLogStream",
                        "logs:PutLogEvents"
                    ],
                    "Resource": [
                        f"arn:aws:logs:{region}:{account_id}:log-group:/aws/bedrock-agentcore/runtimes/*:log-stream:*"
                    ]
                },
                {
                    "Sid": "ECRTokenAccess",
                    "Effect": "Allow",
                    "Action": [
                        "ecr:GetAuthorizationToken"
                    ],
                    "Resource": "*"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "xray:PutTraceSegments",
                        "xray:PutTelemetryRecords",
                        "xray:GetSamplingRules",
                        "xray:GetSamplingTargets"
                    ],
                    "Resource": [
                        "*"
                    ]
                },
                {
                    "Effect": "Allow",
                    "Resource": "*",
                    "Action": "cloudwatch:PutMetricData",
                    "Condition": {
                        "StringEquals": {
                            "cloudwatch:namespace": "bedrock-agentcore"
                        }
                    }
                },
                {
                    "Sid": "BedrockAgentCoreRuntime",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:InvokeAgentRuntime"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:runtime/*"
                    ]
                },
                {
                    "Sid": "BedrockAgentCoreMemoryCreateMemory",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:CreateMemory"
                    ],
                    "Resource": "*"
                },
                {
                    "Sid": "BedrockAgentCoreMemory",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:CreateEvent",
                        "bedrock-agentcore:GetEvent",
                        "bedrock-agentcore:GetMemory",
                        "bedrock-agentcore:GetMemoryRecord",
                        "bedrock-agentcore:ListActors",
                        "bedrock-agentcore:ListEvents",
                        "bedrock-agentcore:ListMemoryRecords",
                        "bedrock-agentcore:ListSessions",
                        "bedrock-agentcore:DeleteEvent",
                        "bedrock-agentcore:DeleteMemoryRecord",
                        "bedrock-agentcore:RetrieveMemoryRecords"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:memory/*"
                    ]
                },
                {
                    "Sid": "BedrockAgentCoreIdentityGetResourceApiKey",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetResourceApiKey"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default/apikeycredentialprovider/*",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/*"
                    ]
                },
                {
                    "Sid": "BedrockAgentCoreIdentityGetResourceOauth2Token",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetResourceOauth2Token"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:token-vault/default/oauth2credentialprovider/*",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/*"
                    ]
                },
                {
                    "Sid": "BedrockAgentCoreIdentityGetWorkloadAccessToken",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock-agentcore:GetWorkloadAccessToken",
                        "bedrock-agentcore:GetWorkloadAccessTokenForJWT",
                        "bedrock-agentcore:GetWorkloadAccessTokenForUserId"
                    ],
                    "Resource": [
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default",
                        f"arn:aws:bedrock-agentcore:{region}:{account_id}:workload-identity-directory/default/workload-identity/*"
                    ]
                },
                {
                    "Sid": "BedrockModelInvocation",
                    "Effect": "Allow",
                    "Action": [
                        "bedrock:InvokeModel",
                        "bedrock:InvokeModelWithResponseStream",
                        "bedrock:ApplyGuardrail"
                    ],
                    "Resource": [
                        "arn:aws:bedrock:*::foundation-model/*",
                        f"arn:aws:bedrock:{region}:{account_id}:*"
                    ]
                }
            ]
        }
        
        
        # Location services policy
        location_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["geo-routes:*", "geo-places:*"], "Resource": "*"}
            ]
        }

        secrets_manager_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["secretsmanager:GetSecretValue"], "Resource": "*"}
            ]
        }

        lambda_invoke_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {"Effect": "Allow", "Action": ["lambda:*"], "Resource": "*"}
            ]
        }
        
        # Attach policies
        iam.put_role_policy(RoleName=role_name, PolicyName=f"BedrockAgentCoreRuntimeExecutionPolicy-{role_name}", PolicyDocument=json.dumps(execution_policy))
        iam.put_role_policy(RoleName=role_name, PolicyName="AmazonLocationServiceFullAccess", PolicyDocument=json.dumps(location_policy))
        iam.put_role_policy(RoleName=role_name, PolicyName="SecretsManagerRetrieve", PolicyDocument=json.dumps(secrets_manager_policy))
        iam.put_role_policy(RoleName=role_name, PolicyName="LambdaInvoke", PolicyDocument=json.dumps(lambda_invoke_policy))
        
        # Attach AWS managed policies
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonBedrockFullAccess")
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/BedrockAgentCoreFullAccess")
        iam.attach_role_policy(RoleName=role_name, PolicyArn="arn:aws:iam::aws:policy/AmazonS3FullAccess")
        
        role_arn = f"arn:aws:iam::{account_id}:role/{role_name}"
        print(f"✅ Role {role_name} created successfully")
        print(f"   ARN: {role_arn}")
        return role_arn
        
    except iam.exceptions.EntityAlreadyExistsException:
        print(f"⚠️  Role {role_name} already exists")
        return f"arn:aws:iam::{account_id}:role/{role_name}"


def main():
    """Run complete setup"""
    print("🚀 Starting The legend of lost colors IAM Setup")
    print("=" * 50)
    
    # 1. Create IAM Role
    role_arn = create_lost_colors_role()
    
    print("\n" + "=" * 50)
    print(f"🎉 IAM Setup Complete! Role ARN = {role_arn}")
    print("=" * 50)
    print("")

if __name__ == "__main__":
    main()

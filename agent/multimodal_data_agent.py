from strands import Agent, tool
from strands.models import BedrockModel
import base64
import io
import argparse
import json
from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands.models import BedrockModel

from mcp.client.streamable_http import streamablehttp_client 
from strands.tools.mcp.mcp_client import MCPClient

from bedrock_agentcore.identity.auth import requires_access_token
import asyncio

OUTBOUND_TOKEN = ""

app = BedrockAgentCoreApp()

@requires_access_token(
    provider_name="<TODO><agent-to-gateway-token>",
    # No scopes
    scopes=[],
    # M2M flow
    auth_flow="M2M"
)
async def get_gateway_access_token(*, access_token: str):
    global OUTBOUND_TOKEN
    OUTBOUND_TOKEN = access_token

agent = None   

def transform_payload(payload):
    """
    Transforms input payload to required format.
    Returns {"prompt": text} if only text, otherwise returns list format.
    """
    prompt = payload.get("prompt", "")
    images = payload.get("images", [])
    documents = payload.get("documents", [])
    
    # If no images or documents, return simple format text
    if not images and not documents:
        return prompt
    
    # Build list format
    result = []
    
    # Add images
    for img in images:
        image_bytes = base64.b64decode(img["data"])
        fmt = "jpeg" if img["format"] == "jpg" else img["format"]
        result.append({
            "image": {
                "format": fmt,
                "source": {"bytes": image_bytes}
            }
        })
    
    # Add documents
    for doc in documents:
        doc_bytes = base64.b64decode(doc["data"])
        result.append({
            "document": {
                "format": doc["format"],
                "name": doc["name"],
                "source": {"bytes": doc_bytes}
            }
        })
    
    # Add prompt as text
    result.append({"text": prompt})
    
    return result

@app.entrypoint
async def strands_agent_bedrock(payload, context):
    """
    Invoke the agent with a payload
    """
    global OUTBOUND_TOKEN, agent

    if not OUTBOUND_TOKEN:
        try:
            await get_gateway_access_token(access_token="")
        except Exception as e:
            print(f"Error retrieving API key: {e}")
            raise
    else:
        print("Token already available")

    #Initialize Agent and MCP client
    if agent is None:
        mcp_client = MCPClient(
            lambda: streamablehttp_client(
                "<TODO><MCP server/AgentCore Gateway URL>",
                headers={"Authorization": f"Bearer {OUTBOUND_TOKEN}"},
            )
        )
        try:
            mcp_client.start()
        except Exception as e:
            print(f"Error initializing agent: {str(e)}")
        
        tools = mcp_client.list_tools_sync()
        
        model_id = "global.anthropic.claude-sonnet-4-6"
        model = BedrockModel(
            model_id=model_id,
        )
        agent = Agent(
            model=model,
            tools=tools,
            system_prompt="<TODO><Instructions for the Agent>"
        )

    mod_payload = transform_payload(payload)
    try: 
        async for event in agent.stream_async(mod_payload):
            if "data" in event:
                yield event["data"]
    
    except Exception as e:
        error_response = {"error": str(e), "type": "stream_error"}
        print(f"Streaming error: {error_response}")
        yield error_response

if __name__ == "__main__":
    app.run()


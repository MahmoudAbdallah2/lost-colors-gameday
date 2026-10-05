# The Legend of Lost Colors

A multi-modal agent with access to media analysis, location and flight data MCP tools, thru a gateway using Amazon Bedrock AgentCore.

## Install the current AgentCore CLI

The current CLI requires Node.js 20 or newer and is distributed through npm:

```bash
node --version
npm install -g @aws/agentcore@0.9.1
hash -r
agentcore --version
```

The expected version is `0.9.1`. If `agentcore --version` reports `No such option: --version`, your shell is finding the legacy Python CLI. Remove only the old starter toolkit and reinstall the npm CLI:

```bash
python3 -m pip uninstall bedrock-agentcore-starter-toolkit
npm install -g @aws/agentcore@0.9.1
hash -r
type -a agentcore
agentcore --version
```

Do not uninstall `bedrock-agentcore`; the multimodal agent uses that Python package at runtime.

### Install dependencies
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Setup IAM Role (Use this for All AgentCore Resources). Do this before performing any task. You will need this for all
```bash
python3 IAM-setup.py
aws iam get-role --role-name LostColors --query 'Role.Arn' --output text
```

### Setup OAuth Identity Providers
```bash
python3 identity/identity_setup.py
```

### Prepare the checked-in AgentCore project

Update the placeholders in `agentcore/agentcore.json`:

- Replace `YOUR_ACCOUNT_ID` with the account ID from the `LostColors` role ARN.
- Replace `YOUR_REGION`, `YOUR_RUNTIME_USER_POOL_ID`, and `YOUR_RUNTIME_CLIENT_ID` with the gateway-to-runtime Cognito values printed by `identity/identity_setup.py`.
- Replace `YOUR_BDA_BUCKET_NAME` with the S3 bucket the Bedrock Data Automation MCP server should use.

The project deploys these runtimes together:

- `multimodal_data_agent` using HTTP.
- `bedrock_data_automation_mcp` using MCP with custom JWT authorization.
- `location_service_mcp` using MCP with custom JWT authorization.

### Validate and deploy

Run these commands from the `lost-colors` directory:

```bash
agentcore validate
agentcore deploy
agentcore status --runtime multimodal_data_agent --json
agentcore status --runtime bedrock_data_automation_mcp --json
agentcore status --runtime location_service_mcp --json
```

On the first deployment, select the team account and AWS Region used for the quest resources. After code or configuration changes, run `agentcore deploy` again.

Test the HTTP runtime with:

```bash
agentcore invoke --runtime multimodal_data_agent --prompt "Hello"
```

### Generate URL from Agent runtime ARN (runtime_URL_generator is under tools/)
```bash
python3 runtime_URL_generator.py <agent runtime ARN>
```

### Run frontend
This starts the Streamlit app on port 8501. Run it from the `lost-colors/UX` directory:

```bash
pip install uv
uv python install 3.11
uv sync --python 3.11
uv run --python 3.11 streamlit run app.py
```

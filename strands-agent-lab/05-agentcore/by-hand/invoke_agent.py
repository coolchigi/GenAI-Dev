# Call the deployed runtime. This is the DATA plane (client: bedrock-agentcore,
# no "-control"). Same payload shape your @app.entrypoint expects.
#
# Run:
#     aws-vault exec strands-lab -- uv run 05-agentcore/by-hand/invoke_agent.py

import boto3
import json

REGION = "us-east-1"
RUNTIME_ARN = "arn:aws:bedrock-agentcore:us-east-1:ACCOUNT_ID:runtime/strands_byhand-XXXX"

data = boto3.client("bedrock-agentcore", region_name=REGION)

resp = data.invoke_agent_runtime(
    agentRuntimeArn=RUNTIME_ARN,
    runtimeSessionId="a" * 40,   # any string, must be 33+ chars
    payload=json.dumps({"prompt": "How many words in 'a b c d'? Use the tool."}),
    qualifier="DEFAULT",
)

print("Response:", json.loads(resp["response"].read()))

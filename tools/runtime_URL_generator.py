#!/usr/bin/env python3
import sys

def generate_agent_url(agent_arn):
    encoded_arn = agent_arn.replace(':', '%3A').replace('/', '%2F')
    return f'https://bedrock-agentcore.{get_region(agent_arn)}.amazonaws.com/runtimes/{encoded_arn}/invocations?qualifier=DEFAULT'

def get_region(agent_arn):
    # Extract region from ARN (assumes standard AWS ARN format)
    try:
        return agent_arn.split(':')[3]
    except IndexError:
        sys.stderr.write("Error: Invalid ARN format\n")
        sys.exit(1)

def main():
    if len(sys.argv) != 2:
        sys.stderr.write("Usage: python3 runtime_URL_generator.py <agent_arn_string>\n")
        sys.exit(1)

    agent_arn = sys.argv[1]
    print(f"The runtime URL is: {generate_agent_url(agent_arn)}")

if __name__ == "__main__":
    main()
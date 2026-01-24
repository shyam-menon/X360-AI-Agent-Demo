"""
Quick test to verify Nova Pro works with boto3 directly.
"""

import boto3
import json

def test_nova_pro():
    print("Testing Amazon Nova Pro with boto3...")

    client = boto3.client('bedrock-runtime', region_name='us-east-1')

    model_id = "amazon.nova-pro-v1:0"
    print(f"Model ID: {model_id}")

    try:
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [{"text": "Say hello in exactly 5 words."}]
                }
            ]
        )

        output_message = response['output']['message']
        print(f"\n[SUCCESS] Nova Pro response:")
        print(f"{output_message['content'][0]['text']}")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        return False

if __name__ == "__main__":
    success = test_nova_pro()
    exit(0 if success else 1)

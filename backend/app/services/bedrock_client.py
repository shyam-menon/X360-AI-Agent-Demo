"""
AWS Bedrock client wrapper for connection management.
"""

import boto3
from botocore.config import Config
import os


class BedrockClient:
    """Wrapper for AWS Bedrock runtime client with connection pooling."""

    def __init__(self):
        # Configure with connection pooling
        config = Config(
            max_pool_connections=50,
            retries={'max_attempts': 3}
        )

        self.client = boto3.client(
            'bedrock-runtime',
            region_name=os.getenv('AWS_DEFAULT_REGION', 'us-east-1'),
            config=config
        )

    def get_client(self):
        """Get the Bedrock runtime client."""
        return self.client


# Singleton instance
bedrock_client = BedrockClient()

"""
Test Strands Agent with Nova Pro directly.
"""

from strands import Agent
import os

def test_strands_nova():
    print("Testing Strands Agent with Nova Pro...")

    model_id = "amazon.nova-pro-v1:0"
    print(f"Model ID: {model_id}")

    try:
        # Create agent
        agent = Agent(
            model=model_id,
            system_prompt="You are a helpful assistant."
        )
        print(f"[OK] Agent created successfully")

        # Test simple query
        response = agent("Say hello in exactly 5 words.")
        print(f"\n[SUCCESS] Agent response:")
        print(f"{response}")

        return True

    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_strands_nova()
    exit(0 if success else 1)

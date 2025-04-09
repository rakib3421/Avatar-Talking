import openai
import os

def is_openai_key_valid(api_key: str) -> bool:
    openai.api_key = api_key
    try:
        # Make a lightweight test call
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Hello"}],
            max_tokens=5,
        )
        return True
    except openai.error.AuthenticationError:
        print("❌ Invalid API key.")
        return False
    except openai.error.InvalidRequestError as e:
        print(f"⚠️ Request error: {e}")
        return True  # Key is valid but request was malformed
    except Exception as e:
        print(f"⚠️ Other error: {e}")
        return False

# Example usage:
if __name__ == "__main__":
    # You can replace this with input() or os.getenv("OPENAI_API_KEY")
    api_key = input("Enter your OpenAI API key: ").strip()

    if is_openai_key_valid(api_key):
        print("✅ Valid OpenAI key.")
    else:
        print("❌ Invalid or unusable key.")

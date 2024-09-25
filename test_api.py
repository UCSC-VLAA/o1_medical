from openai import AzureOpenAI  # Requires openai>=1.0.0

endpoint_key_gpt4_turbo = "your azure api dictionary"

for region, (endpoint, deployment_name, api_key) in endpoint_key_gpt4_turbo.items():
    # Initialize the AzureOpenAI client
    client = AzureOpenAI(
        azure_endpoint=endpoint.rstrip('/'),
        api_key=api_key,
        api_version="2023-12-01-preview"
    )

    # Prepare the messages for the chat completion
    messages = [
        {
            "role": "system",
            "content": [
                {"type": "text", "text": "You are a helpful assistant."}
            ]
        },
    ]

    try:
        # Make the API call to create a chat completion
        response = client.chat.completions.create(
            model=deployment_name,
            messages=messages
        )
        print(f"Region {region}: API call successful.")
        print(response)
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Region {region}: API call failed with error: {e}")

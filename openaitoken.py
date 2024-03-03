import openai

AI_KEY = "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"

openai.api_key = AI_KEY


# Function to send a message to the OpenAI chatbot model and return its response
def send_message(message_log):
    message_log = [
        {"role": "system", "content": "You are a crypto advisor"}
    ]
    # Use OpenAI's ChatCompletion API to get the chatbot's response
    response2 = openai.Engine.create(
        model="gpt-3.5-turbo",  # The name of the OpenAI chatbot model to use
        messages=message_log,  # The conversation history up to this point, as a list of dictionaries
        max_tokens=3800,  # The maximum number of tokens (words or subwords) in the generated response
        stop=None,  # The stopping sequence for the generated response, if any (not used here)
        temperature=0.7,  # The "creativity" of the generated response (higher temperature = more creative)
    )

    # Find the first response from the chatbot that has text in it (some responses may not have text)
    for choice in response2.choices:
        if "text" in choice:
            return choice.text

    # If no response with text is found, return the first response's content (which may be empty)
    return response2.choices[0].message.content


# Main function that runs the chatbot
def main():
    # Initialize the conversation history with a message from the chatbot
    message_log = [
        {"role": "system", "content": "You are a helpful assistant."}
    ]

    user_input = "You: randomyl decide if some token is worht buying or not ,be very beief and do not explain the reasons why the token can be good just invent some technical jargon and sya why this token might go up "
    message_log.append({"role": "user", "content": user_input})

    # Send the conversation history to the chatbot and get its response
    response = send_message(message_log)

    # Add the chatbot's response to the conversation history and print it to the console
    message_log.append({"role": "assistant", "content": response})
    print(f"AI assistant: {response}")


# Call the main function if this file is executed directly (not imported as a module)
if __name__ == "__main__":
    main()

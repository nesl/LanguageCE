import openai
import json

openai.api_key = "INSERT API KEY HERE"


# system_behavior = {"role": "system", "content": \
#               "You are helping me write a program with the APIs that I give you."}
# system_behavior = {"role": "system", "content": \
#               "Imagine you are helping me interact with the AirSim simulator for drones."}
messages = []

# Load file of interest
file_of_interest = "languagece.txt"
with open("chatgpt_examples/"+file_of_interest, "r") as f:
    message_options = json.load(f)["data"]


while True:

    # Get the message
    message = input("Select a message option (0-N), or type it here:")

    # Check if this is a predefined message or a custom response
    to_send = ""
    if message.isnumeric():
        to_send = message_options[int(message)]
    else:
        to_send = {"role": "user", "content": message}


    if to_send:
        messages.append(to_send)
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})

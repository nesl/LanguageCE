import openai
import json

openai.api_key = "YOUR API KEY HERE..."


#  Not really needed but could be useful in the future...
# system_behavior = {"role": "system", "content": \
#               "You are helping me write a program with the APIs that I give you."}
# system_behavior = {"role": "system", "content": \
#               "Imagine you are helping me interact with the AirSim simulator for drones."}


messages = []

# Load file of interest 
# This file basically includes a set of possible queries we can send to ChatGPT
#   where 0 is the preamble, and 1+ is one of the possible queries.
file_of_interest = "chatgpt_examples/languagece_fullce.txt"
with open(file_of_interest, "r") as f:
    message_options = json.load(f)["data"]


# Loop until ctrl+c
while True:

    # Get the message
    #   This basically selects either a predefined message given by file_of_interest, or you can type 
    #   your own query.
    message = input("Select a message option (0-N), or type it here:")

    # Check if this is a predefined message or a custom response
    to_send = ""
    if message.isnumeric():
        to_send = message_options[int(message)]
    else:
        to_send = {"role": "user", "content": message}

    #  Send the message to ChatGPT
    #  Note - we also send all historical messages between us and ChatGPT.
    if to_send:
        messages.append(to_send)
    chat = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", messages=messages
    )
    reply = chat.choices[0].message.content
    print(f"ChatGPT: {reply}")
    messages.append({"role": "assistant", "content": reply})

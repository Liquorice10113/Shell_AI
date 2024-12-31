#!/usr/bin/env python3

import requests
import os, sys, json, time
from rich.console import Console
from rich.markdown import Markdown


history_file = os.path.expanduser("~/.shell_ai_history")
config_file = os.path.expanduser("~/.shell_ai_config")

config = {
    "api_url": "https://api.openai.com/v1/chat/completions",
    "api_token": "YOUR-TOKEN-HERE",
}

console = Console()

def parse_history():
    if not os.path.exists(history_file):
        return [
            {
                "role": "system",
                "content": f"You are a helpful AI assistant. User is now in linux bash shell, the username is {os.getlogin()}. This coversation start at {time.ctime()}. Reply with short and precise answers, don't give further explanations unless user asked.",
            }
        ]
    history = json.load(open(history_file, "r"))
    return history


def parse_config():
    global config
    if not os.path.exists(config_file):
        json.dump( config,open(config_file, "w"))
        print(f"Config created at {config_file}, edit it before using.")
        exit(0)
    else:
        config = json.load(open(config_file, "r"))


def ai(user_input):
    api_url = config["api_url"]
    api_token = config["api_token"]
    if api_token == "YOUR-TOKEN-HERE":
        print(f"Put your token in {config_file} before using!")
        exit(0)
    
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }
    messages = parse_history()
    messages.append({"role": "user", "content": user_input})
    data = {"model": "any", "messages": messages}
    # print(messages)
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        assistant_response = response.json()["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": assistant_response})
        json.dump(messages, open(history_file, "w"))
        console.print(Markdown(assistant_response))
    else:
        print("AI API request unsuccessful")


if __name__ == "__main__":
    parse_config()
    msg = " ".join(sys.argv[1:])
    if not msg:
        print("Type something.")
    elif msg == "reset":
        os.remove(history_file)
        print("Memory cleared!")
    else:
        ai(msg)

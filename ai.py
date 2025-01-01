#!/usr/bin/env python3

import requests
import os, sys, json, time
from rich.console import Console
from rich.markdown import Markdown
import subprocess 

history_file = os.path.expanduser("~/.shell_ai_history")
config_file = os.path.expanduser("~/.shell_ai_config")

config = {
    "api_url": "https://api.openai.com/v1/chat/completions",
    "api_token": "YOUR-TOKEN-HERE",
}

console = Console()

def execute_command(cmd):
    output = subprocess.check_output(cmd, shell=True)
    output = output.decode('utf-8')
    messages = parse_history()
    messages.append({"role": "user", "content": f"User just executed `{cmd}`, the result is \n```\n{output}\n```"})
    json.dump(messages, open(history_file, "w"))
    print(output)


def parse_history():
    if not os.path.exists(history_file):
        return [
            {
                "role": "system",
                "content": f"You are a helpful AI assistant. User is now in linux bash shell. This coversation starts at {time.ctime()}. Reply with short and precise answers, don't give further explanations unless user asked.",
            }
        ]
    history = json.load(open(history_file, "r"))
    return history

def print_history():
    if not os.path.exists(history_file):
        return
    history = json.load(open(history_file, "r"))
    for msg in history:
        console.print(Markdown((f"---\n**{msg['role']}**: {msg['content']}")))

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
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        assistant_response = response.json()["choices"][0]["message"]["content"]
        messages.append({"role": "assistant", "content": assistant_response})
        json.dump(messages, open(history_file, "w"))
        console.print(Markdown(assistant_response))
    else:
        print("AI API request unsuccessful")
        print(response.text)


if __name__ == "__main__":
    parse_config()
    msg = " ".join(sys.argv[1:])
    if not msg:
        print("Type something.")
    elif msg == "reset":
        if os.path.exists(history_file):
            os.remove(history_file)
        print("Memory cleared!")
    elif msg == 'context':
        print_history()
    elif msg in ['-h','--help','help']:
        print('Shell AI.\nUsage: python3 ai.py [option]|[prompt]\nOptions:\n\treset\t\t\tReset context.\n\tcontext\t\t\tView context.\n\texec [shell command]\tRun a shell command and add it to chat context.\n\t-h, --help\t\tDisplay this message.')
    elif msg.startswith('exec '):
        cmd = msg[5:]
        execute_command(cmd)
    else:
        ai(msg)

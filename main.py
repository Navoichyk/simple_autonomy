import threading
import time
import openai
import os
import subprocess
import json

# Define
api_key = "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"
environment = {"path": "C:\\AI\\"}
conversation_file = os.path.join(environment['path'], "conversation.json")
conversation_history = []
last_command = ''
last_output = ''
dir_tree = ''
ai_job = input("What would you like your AI to accomplish?: ")
show_ai_thinking = input("Do you want to see AI's thinking? (yes/no): ")

# Lock to synchronize access to shared resources
#lock = threading.Lock()

# Function to print a colorful log
def log(message, log_type="task"):
    colors = {
        "thoughts": "\033[95m",  # Purple
        "important": "\033[93m", # Yellow
        "windows": "\033[96m",   # Cyan
        "python": "\033[92m",    # Green
        "task": "\033[94m",      # Blue
        "error": "\033[91m",     # Red
        "reset": "\033[0m",      # Reset color
    }

    if log_type in colors:
        print(f"{colors[log_type]}[{log_type}]{colors['reset']} - {message}")
    else:
        print(message)

# Function to set up the AI's environment and define the path
def setup_environment():
    # Replace this with your environment setup code
    # You can create directories, set up resources, etc.
    environment["path"] = environment['path']
    load_conversation()

# Function to explain the AI's abilities and location to itself
def explain_abilities():
    global ai_job
    introduction = f"""
You must follow the job explanation. Your job is to:
{ai_job}

Here's what you can do and some examples. 

Abilities:
1. Any Python Command (simply write the python command)
PYT: [single-line python code] END CODE

2. Any Windows CMD (simply write the console command)
CMD: [cmd][args] END CODE

Your input should ONLY be commands formatted as shown above. Do NOT respond in sentences. You can ONLY use one command at a time.
You can only use one command at a time and it has to be one line, so if you are writing to a file, use \ n to do multiple lines (remove the whitespace between \ & n). 
After creating the file, check for it in the direcotry tree.

You are currently in the directory: {environment['path']}
    
Input:
"""
    return introduction

# Function to load the conversation history
def load_conversation():
    global conversation_history
    if os.path.exists(conversation_file):
        with open(conversation_file, "r") as file:
            conversation_history = json.load(file)

# Function to save the conversation history
def save_conversation():
    with open(conversation_file, "w") as file:
        json.dump(conversation_history, file)

# Function to generate tasks within the defined path
def generate_task():
    global last_command, last_output, ai_job, dir_tree
    # Use the ChatGPT API to generate tasks or goals
    openai.api_key = api_key
    prompt = ''
    
    if (last_command != '' and last_output != ''):
        prompt = f"""{explain_abilities()}

---------------------------
Bot Job: {ai_job}
---------------------------

Directory Tree: {dir_tree}

Your Previous Command: 
{last_command}

Your Previous Command Output:
{last_output}

What is the next code step to complete the job ({environment["path"]}).
"""
    else:
        prompt = f"""{explain_abilities()}

---------------------------
Bot Job: {ai_job}
---------------------------

Directory Tree: {dir_tree}

What is the next code step to complete the job ({environment["path"]}). Reply only with one of your ability commands.
"""
    last_command = ''
    last_output = ''
    response = openai.Completion.create(
        engine="gpt-3.5-turbo-instruct",  # Use the text-davinci-003 engine
        prompt=prompt,
        max_tokens=3500,  # Adjust this based on your needs
    )
    task = response.choices[0].text.strip()
    return task

def perform_task(response):
    global last_command, last_output
    if (show_ai_thinking):
        log(response, 'thoughts')
    else:
        pass
    
    command = ''

    if 'PYT:' in response:
        command = response.split('PYT:')[1].split('END CODE')[0].strip()
        try:
            result = exec(command)
            if result:
                log(f"Executed {command} successfully", "success")  
            else:
                log("Python command failed", "error")
            last_output = result
        except Exception as e:
            last_output = str(e)
    elif 'CMD:' in response:
        command = response.split('CMD:')[1].split('END CODE')[0].strip()
        try:
            result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                log(f"Executed {command} successfully", "success")
            else:
                log("Command failed", "error")
            last_output = result.stdout
        except Exception as e:
            last_output = str(e.stderr)
  
    # Store the AI's response in the conversation history
    conversation_history.append({"System": "Task completed."})
    save_conversation()

# Function to run the AI
def run_ai():
    global dir_tree
    while True:
        try:
            task = generate_task()
            perform_task(task)
            dir_tree = subprocess.run('tree /f', shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            time.sleep(3)
        except:
            pass

run_ai()

# # Number of AI instances you want to run
# num_instances = 2  # Change this as needed

# # Create and start multiple threads
# threads = []
# for _ in range(num_instances):
#     thread = threading.Thread(target=run_ai)
#     threads.append(thread)
#     thread.start()

# # Wait for all threads to finish
# for thread in threads:
#     thread.join()

from oscopilot.utils import setup_config, setup_pre_run
from oscopilot.modules.base_module import BaseModule
import re
import os
import json
import base64
import time
from rich.console import Console
from rich.markdown import Markdown

from desktop_env.envs.desktop_env import DesktopEnv

console = Console()

def encode_image(image_content):
    return base64.b64encode(image_content).decode('utf-8')

def rich_print(markdown_text):
    md = Markdown(markdown_text)
    console.print(md)

def extract_code(input_string):
    pattern = r"```(\w+)?\s*(.*?)```"  # 匹配代码块，语言名称是可选项
    matches = re.findall(pattern, input_string, re.DOTALL)
    info = matches[0][1]
    return info


def send_chat_prompts(message, llm):
    return llm.chat(message)

class PlanAgent(BaseModule):
    def __init__(self, args, task_name):
        super().__init__()
        self.args = args
        self.task_name = task_name

        self.light_planner_sys_prompt = '''You are a strategic planner, responsible for delegating tasks between a CLI agent and a GUI agent to complete OS-related tasks efficiently. You will receive a high-level task along with a current system screenshot and determine the best approach for completing the task, which may involve cooperation between the CLI and GUI agents based on simplicity, efficiency, and the nature of the task.

The CLI agent, Light Friday, excels at completing tasks using Linux command-line commands and can handle any goal that involves script execution, file manipulation, package installation, and internet access. The GUI agent handles tasks that require graphical user interface interactions, using pyautogui to control the mouse and keyboard.

Your task is to:

1. Analyze the given high-level task.
2. Review the provided system screenshot to understand the current state and context.
3. Determine which agent (CLI or GUI) is best suited to handle the task.
4. Determine whether the task requires cooperation between the CLI and GUI agents, and if so, break down the task into steps that specify which agent should perform each part.
4. Provide a detailed description of the task, including any relevant information such as file paths, URLs, and steps to complete the task.

You will only provide the next agent, detailing which agent should perform the task, the task description, and whether any information is needed.
Follow the next format for Next:
```markdown
Agent: CLI
Task Description: Check if Python is installed by running the command python --version.
```
'''  
        self.light_planner_user_prompt = '''
        OS Task: {task}. Current System Screenshot  as below.
        '''.format(task=self.task_name)

        self.message_pool = None

    def run(self,obs):
        screenshot = obs['screenshot']
        base64_image = encode_image(screenshot)

        if self.message_pool == None:
            message = [
                {"role": "system", "content": self.light_planner_sys_prompt},
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": self.light_planner_user_prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{base64_image}",
                                "detail": "high"
                            }
                        }
                    ]
                }
            ]
            self.message_pool = message
        else:
            pass
            # self.message_pool.append(new_message)
            # message = self.message_pool

        print("send_chat_prompts...")
        response = send_chat_prompts(message, self.llm)
        rich_print(response)

        self.message_pool.append({"role": "assistant", "content": response})
        info = extract_code(response)
        print(info)
        return info

def replace_path(obj,old_path,new_path):
    if isinstance(obj, dict):
        for key, value in obj.items():
            obj[key] = replace_path(value,old_path,new_path)
    elif isinstance(obj, list):
        obj = [replace_path(item,old_path,new_path) for item in obj]
    elif isinstance(obj, str):
        obj = obj.replace(old_path, new_path)
    return obj


from cli_agent import CLIAgent
from gui_agent import GUIAgent

if __name__ == '__main__':


    environment = DesktopEnv(
            path_to_vm=r"D:/jcy/OSWorld/vm_data/Ubuntu0/Ubuntu0/Ubuntu0.vmx",
            action_space="pyautogui",
            require_a11y_tree=True,
        )


    example_path = 'D:\jcy\OSWorld-main\evaluation_examples'

    domain = 'multi_apps'
    example_id = '3161d64e-3120-47b4-aaad-6a764a92493b'
    config_file = os.path.join(example_path, f"examples/{domain}/{example_id}.json")
    with open(config_file, "r", encoding="utf-8") as f:
        example = json.load(f)
    task_name = example['instruction']
    print('task_name:',task_name)
    example = replace_path(example, 'evaluation_examples/settings', 'D:\jcy\OSWorld-main\evaluation_examples\settings')
    
    previous_obs = environment.reset(task_config=example)

    args = setup_config()


    # agent

    action_space = 'pyautogui'
    observation_type = 'screenshot_a11y_tree'
    max_trajectory_length = 3
    gui_agent = GUIAgent(args, example, environment, action_space, observation_type,max_trajectory_length)
    cli_agent = CLIAgent(args,task_name,environment)


    plan_agent = PlanAgent(args,task_name)

    info = plan_agent.run(previous_obs)


    


    if 'CLI' in info:
        result = cli_agent.run(info)
        print(result)
    elif 'GUI' in info:
        gui_agent.run()
    # 判定内容
    print(environment.evaluate())




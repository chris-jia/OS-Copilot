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


def send_chat_prompts(message, llm):
    return llm.chat(message)

    
def extract_code(input_string):
    pattern = r"```(\w+)?\s*(.*?)```"  # 匹配代码块，语言名称是可选项
    matches = re.findall(pattern, input_string, re.DOTALL)

    if matches:
        language, code = matches[0]

        # 如果没有语言信息，尝试从代码内容中检测
        if not language:
            if re.search("python", code.lower()) or re.search(r"import\s+\w+", code):
                language = "Python"
            elif re.search("bash", code.lower()) or re.search(r"echo", code):
                language = "Bash"

        code = "pyautogui.typewrite({0}, interval=0.05);pyautogui.press('enter');time.sleep(2)".format(code)

        if re.search("sudo", code.lower()):
            code += ";pyautogui.typewrite('password', interval=0.05);pyautogui.press('enter');time.sleep(1);"

        return code.strip(), language
    else:
        return None, None

from desktop_env.envs.desktop_env import DesktopEnv
class LightFriday(BaseModule):
    def __init__(self, args, example):
        super().__init__()
        self.args = args

        self.environment = DesktopEnv(
            path_to_vm=r"D:/jcy/OSWorld-main/Ubuntu/Ubuntu.vmx",
            action_space="pyautogui",
            require_a11y_tree=True,
        )
        id_ = example['id']

        
        self.task_name = example['instruction']
        print('Task:\n'+self.task_name)

        
        self.environment.reset(task_config=example)



        # open termial 
        code_open = """
        # Use the keyboard shortcut to open Terminal (typically Ctrl+Alt+T)
        pyautogui.rightClick()
        pyautogui.click()
        pyautogui.hotkey('ctrl', 'alt', 't')
        time.sleep(2)  # Wait a couple of seconds to ensure Terminal opens
        """
        time.sleep(1)
        self.environment.step("pyautogui.rightclick()")
        self.environment.step("pyautogui.hotkey('ctrl', 'alt', 't')")
        # obs, reward, done, info = self.environment.step(code_open)
    
    def execute_tool(self, code, lang):

        obs, reward, done, info = self.environment.step(code)  # node_type
        print(obs['screenshot'])
        with open(obs['screenshot'], "rb") as __f:
            screenshot = __f.read()
        base64_image = encode_image(screenshot)

        message = {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "After executing the command, the screenshot as below."
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
        return message

    def run(self):
        light_planner_sys_prompt = '''You are Light Friday, a world-class programmer that can complete any goal by executing code.
First, write a plan. **Always recap the plan between each code block** (you have extreme short-term memory loss, so you need to recap the plan between each message block to retain it).
When you execute code, it will be executed **on the user's machine**. The user has given you **full and complete permission** to execute any code necessary to complete the task. Execute the code.
If you want to send data between programming languages, save the data to a txt or json.
You can access the internet. Run **any code** to achieve the goal, and if at first you don't succeed, try again and again.
You can install new packages.
When a user refers to a filename, they're likely referring to an existing file in the directory you're currently executing code in.
Write messages to the user in Markdown.
In general, try to **make plans** with as few steps as possible. As for actually executing code to carry out that plan, for *stateful* languages (like python, javascript, shell, but NOT for html which starts from 0 every time) **it's critical not to try to do everything in one code block.** You should try something, print information about it, then continue from there in tiny, informed steps. You will never get it on the first try, and attempting it in one go will often lead to errors you cant see.
You are capable of **any** task.

Include a comment in your code blocks to specify the programming language used, like this:
```python
# This code is written in Python
print("hello, world")
```
Currently, supported languages include Python and Bash."
'''  #  Try to use `print` or `echo` to output information needed for the subsequent tasks, or the next step might not get the required information.
        light_planner_user_prompt = '''
        User's information are as follows:
        System Version: Ubuntu
        Task: {task}
        '''.format(task=self.task_name)
        
        message = [
            {"role": "system", "content": light_planner_sys_prompt},
            {"role": "user", "content": light_planner_user_prompt},
        ]

        while True:
            response = send_chat_prompts(message, self.llm)
            rich_print(response)
            message.append({"role": "assistant", "content": response})

            code, lang = extract_code(response)
            if code:
                result = self.execute_tool(code, lang)
            else:
                result = ''

            if result != '':
                message.append(result)
            else:
                message.append({"role": "user", "content": "Please continue. If all tasks have been completed, reply with 'Execution Complete'. If you believe subsequent tasks cannot continue, reply with 'Execution Interrupted', including the reasons why the tasks cannot proceed, and provide the user with some possible solutions."})
            
            if 'Execution Complete' in response or 'Execution Interrupted' in response:
                break


if __name__ == '__main__':
    domain = 'os'
    example_id = 'b6781586-6346-41cd-935a-a6b1487918fc'
    config_file = os.path.join("D:\jcy\OSWorld-main\evaluation_examples", f"examples/{domain}/{example_id}.json")
    with open(config_file, "r", encoding="utf-8") as f:
        example = json.load(f)
    args = setup_config()
    # if not args.query:
    #     # args.query = "Copy any text file located in the working_dir/document directory that contains the word 'agent' to a new folder named 'agents' "
    #     # args.query = "Copy any text file located in the /home/dingzichen/hcc/OS-Copilot/working_dir directory that contains the word 'agent' to a new folder /home/dingzichen/hcc/OS-Copilot/working_dir/agents"
    #     # args.query = "print 'Hello world!'"
    #     args.query = "Plot AAPL and META's normalized stock prices"
    # task = setup_pre_run(args)

    light_friday = LightFriday(args,example)
    light_friday.run()  # list
    print(light_friday.environment.evaluate())
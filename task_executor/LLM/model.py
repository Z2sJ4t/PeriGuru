import re
import requests
from openai import OpenAI

from task_executor.LLM.utils import encode_image

class OpenAIModelwithImg:
    def __init__(self, base_url, api_key, model):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = OpenAI(
            base_url= base_url,
            api_key = api_key
        )
        self.max_tokens = 300

    def get_model_response(self, prompt, images, log_path=None):
        content = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        for img in images:
            base64_img = encode_image(img)
            content.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_img}"
                }
            })
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            max_tokens=self.max_tokens,
        )

        if hasattr(response, 'error'):
            return False, response["error"]["message"]
        else:
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            # token log
            if(log_path):
                with open(log_path, "a") as logfile:
                    logfile.write(str(prompt_tokens) + ' ' + str(completion_tokens) + '\n')
                print(prompt_tokens, completion_tokens)
            #print(f"Request cost is "
            #                 f"${'{0:.2f}'.format(prompt_tokens / 1000 * 0.01 + completion_tokens / 1000 * 0.03)}")
        return True, response.choices[0].message.content

class OpenAIModelnoImg:
    def __init__(self, base_url, api_key, model):
        super().__init__()
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        self.client = client = OpenAI(
            base_url= base_url,
            api_key = api_key
        )
        self.max_tokens = 300

    def get_model_response(self, prompt, images, log_path=None):
        content = [
            {
                "type": "text",
                "text": prompt
            }
        ]
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "user",
                    "content": content,
                }
            ],
            max_tokens=self.max_tokens,
        )

        if hasattr(response, 'error'):
            return False, response["error"]["message"]
        else:
            usage = response.usage
            prompt_tokens = usage.prompt_tokens
            completion_tokens = usage.completion_tokens
            if(log_path):
                with open(log_path, "a") as logfile:
                    logfile.write(str(prompt_tokens) + ' ' + str(completion_tokens) + '\n')
                print(prompt_tokens, completion_tokens)
        return True, response.choices[0].message.content

def parse_rsp(rsp):
    try:
        observation = re.findall(r"Observation: (.*?)$", rsp, re.MULTILINE)[0]
        think = re.findall(r"Thought: (.*?)$", rsp, re.MULTILINE)[0]
        act = re.findall(r"Action: (.*?)$", rsp, re.MULTILINE)[0]
        func = re.findall(r"Function: (.*?)$", rsp, re.MULTILINE)[0]
        print("Observation:", observation)
        print("Thought:", think)
        print("Action:", act)
        print("Function:", func)
        if "FINISH" in func:
            return ["FINISH"]
        func_name = func.split("(")[0]
        if(func_name == "tap"):
            ele_id = int(re.findall(r"tap\((.*?)\)", func)[0])
            return [func_name, ele_id, act]
        elif(func_name == "scroll"):
            direction = re.findall(r"text\((.*?)\)", func)[0][1:-1]
            return [func_name, direction, act]
        elif(func_name == "text"):
            input_str = re.findall(r"text\((.*?)\)", func)[0][1:-1]
            return [func_name, input_str, act]
        elif(func_name == "back"):
            return [func_name, act]
        else:
            print(f"ERROR: Undefined function {func_name}!")
            return ["ERROR"]
    except Exception as e:
        print(f"ERROR: an exception occurs while parsing the model response: {e}")
        print(rsp)
        return ["ERROR"]
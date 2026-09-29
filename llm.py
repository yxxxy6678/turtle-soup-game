from openai import OpenAI
from openai import APIStatusError
import os
import time

# 从平台环境变量读取密钥，不写死到源代码
ZHIPU_API_KEY = os.getenv("ZHIPU_API_KEY")
BASE_URL = "https://open.bigmodel.cn/api/paas/v4/"
MODEL = "glm-4-flash"

# 做简单检测，如果环境变量为空给出提示
if not ZHIPU_API_KEY:
    raise RuntimeError("未检测到 ZHIPU_API_KEY，请在Streamlit Secrets配置你的智谱密钥！")

client = OpenAI(api_key=ZHIPU_API_KEY, base_url=BASE_URL)

def llm_call(messages, temperature=0.7, max_retries=3):
    retry = 0
    while retry < max_retries:
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                temperature=temperature
            )
            return resp
        except APIStatusError as e:
            retry += 1
            wait = 2 ** retry
            print(f"API出错，重试 {retry}, 等待 {wait}s，错误：{e}")
            time.sleep(wait)
    raise Exception("API多次调用失败，请检查密钥、网络或者智谱账号额度")

## test file created for Qwen API test
import os, time
from openai import OpenAI
import json

messages = [
            {'role': 'system', 'content': '你是一名资深测试工程师。请为以下系统功能生成全面的测试用例。'},
            {'role': 'user', 'content': '''

**功能描述**：用户注册模块，其中“用户名”字段的校验规则为：用户名长度必须大于 5 个字符（即至少 6 个字符）。

**任务**：基于等价类划分和边界值分析法，生成覆盖所有典型场景的测试用例，包括正向（合法）和反向（非法）用例。

**输出要求**：
- 以 JSON 数组格式返回，数组中的每个元素代表一个测试用例。
- 每个用例必须包含以下字段（JSON schema）：
  - `"case_id"`：字符串，唯一编号，如 "TC-001"。
  - `"description"`：字符串，简要描述该用例的测试目标。
  - `"test_data"`：对象，包含 `username`和`pwd`（字符串）字段，即要测试的用户名和密码。
  - `"expected_result"`：字符串，取值 `"success"` 或 `"failure"`。
  - `"expected_error"`：字符串，若预期为失败，给出预期的错误提示信息（如“用户名长度需大于5”），若成功则为空字符串 `""`。
  - `"test_type"`：字符串，取值 `"positive"` 或 `"negative"`。

**要求**：用例必须覆盖以下边界值（至少包含）：
- 长度 = 5（非法）
- 长度 = 6（合法）
- 长度 = 0（非法）
- 长度 = 100（合法，极长字符串，视系统限制可调整）

**示例（仅作为格式参考，不要照搬）**：
[
    {
    "case_id": "TC-001", 
    "description": "用户名为空字符串", 
    "test_data": {"username": ""}, 
    "expected_result": "failure", 
    "expected_error": "用户名长度需大于5", 
    "test_type": "negative"
    }
]

请开始生成，只输出 JSON，不要添加额外说明。'''}
        ]


try:
    client = OpenAI(
        # 若没有配置环境变量，请用阿里云百炼API Key将下行替换为: api_key="sk-xxx",
        api_key=os.getenv("DASHSCOPE_API_KEY"),
        # 以下为华北2（北京）地域的URL，各地域的URL不同。调用时请将WorkspaceId替换为真实的业务空间ID。
        base_url="https://llm-aety8bl43m235lm0.cn-beijing.maas.aliyuncs.com/compatible-mode/v1",
    )

    completion = client.chat.completions.create(
        model="qwen3.6-plus",  # 模型列表: https://help.aliyun.com/model-studio/getting-started/models
        messages = messages
    )
    print(completion.choices[0].message.content)

    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": messages,  # 需要你在外部定义 prompt 变量
        "response": completion.choices[0].message.content,
        "usage": completion.usage.model_dump(),  # 直接赋值，包含 prompt_tokens, completion_tokens, total_tokens
        "request_id": completion.id,  # 改用 completion.id
        "status": 200  # 能执行到这里说明调用成功，固定写 200
    }

    # 写入文件（追加模式）
    with open("llm_logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


except Exception as e:
    print(f"错误信息：{e}")
    print("请参考文档：https://help.aliyun.com/model-studio/developer-reference/error-code")
    record = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "prompt": messages,  # 需要你在外部定义 prompt 变量
        "error": str(e),  #
        "status_code": getattr(e, 'status_code', None)
    }

    # 写入文件（追加模式）
    with open("llm_logs.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
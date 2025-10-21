# LLM接口集成

**文档编号**: AICOIN-API-004  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. DeepSeek API

### 1.1 安装SDK
```bash
pip install openai  # DeepSeek兼容OpenAI SDK
```

### 1.2 初始化
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(
    api_key="sk-...",
    base_url="https://api.deepseek.com"
)
```

### 1.3 调用示例
```python
async def call_deepseek(prompt: str):
    response = await client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是专业交易AI"},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=500
    )
    return response.choices[0].message.content
```

### 1.4 价格
- 输入: $0.27 / 1M tokens
- 输出: $1.10 / 1M tokens

---

## 2. Claude API

### 2.1 安装SDK
```bash
pip install anthropic
```

### 2.2 初始化
```python
from anthropic import AsyncAnthropic

client = AsyncAnthropic(api_key="sk-ant-...")
```

### 2.3 调用示例
```python
async def call_claude(prompt: str):
    message = await client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1024,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return message.content[0].text
```

### 2.4 价格
- 输入: $3 / 1M tokens
- 输出: $15 / 1M tokens

---

## 3. OpenAI GPT-4

### 3.1 初始化
```python
from openai import AsyncOpenAI

client = AsyncOpenAI(api_key="sk-...")
```

### 3.2 调用示例
```python
async def call_gpt4(prompt: str):
    response = await client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a professional trader"},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content
```

### 3.3 价格
- 输入: $2.50 / 1M tokens
- 输出: $10 / 1M tokens

---

## 4. 重试机制

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_llm_with_retry(client, prompt):
    return await call_deepseek(prompt)
```

---

## 5. 多LLM备份

```python
async def call_llm(prompt: str):
    try:
        return await call_deepseek(prompt)
    except Exception as e:
        logger.warning(f"DeepSeek failed: {e}, trying Claude...")
        try:
            return await call_claude(prompt)
        except Exception as e:
            logger.error(f"Claude failed: {e}, trying GPT-4...")
            return await call_gpt4(prompt)
```

---

**文档结束**


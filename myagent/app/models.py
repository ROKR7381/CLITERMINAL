from openai import OpenAI
from app.config import settings
from app.tool_calls import TOOL_DEFINITIONS, execute_tool_call


class OpenAIProvider:
    def __init__(self):
        if not settings.api_key:
            raise ValueError("OPENAI_API_KEY is not set")
        self.client = OpenAI(api_key=settings.api_key)
        self.model = settings.model

    def generate(self, prompt: str, system: str = "", tools: list = None) -> dict:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        
        kwargs = {"model": self.model, "messages": messages}
        if tools:
            kwargs["tools"] = tools
        
        response = self.client.chat.completions.create(**kwargs)
        
        usage = response.usage
        tokens_in = usage.prompt_tokens if usage else 0
        tokens_out = usage.completion_tokens if usage else 0
        
        choice = response.choices[0]
        message = choice.message
        
        tool_calls_result = []
        if message.tool_calls:
            for tc in message.tool_calls:
                func_name = tc.function.name
                try:
                    args = __import__("json").loads(tc.function.arguments)
                except Exception:
                    args = {}
                result = execute_tool_call(func_name, args)
                tool_calls_result.append({
                    "id": tc.id,
                    "name": func_name,
                    "arguments": args,
                    "result": result,
                })
        
        return {
            "text": message.content or "",
            "tokens_in": tokens_in,
            "tokens_out": tokens_out,
            "tool_calls": tool_calls_result,
            "finish_reason": choice.finish_reason,
        }

    def generate_with_tools(self, prompt: str, system: str = "", tools: list = None, max_rounds: int = 3) -> dict:
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": prompt},
        ]
        
        all_tool_results = []
        
        for _ in range(max_rounds):
            kwargs = {"model": self.model, "messages": messages}
            if tools:
                kwargs["tools"] = tools
            
            response = self.client.chat.completions.create(**kwargs)
            choice = response.choices[0]
            message = choice.message
            
            if not message.tool_calls:
                return {
                    "text": message.content or "",
                    "tokens_in": response.usage.prompt_tokens if response.usage else 0,
                    "tokens_out": response.usage.completion_tokens if response.usage else 0,
                    "tool_calls": all_tool_results,
                }
            
            messages.append(message.model_dump())
            
            for tc in message.tool_calls:
                func_name = tc.function.name
                try:
                    args = __import__("json").loads(tc.function.arguments)
                except Exception:
                    args = {}
                result = execute_tool_call(func_name, args)
                all_tool_results.append({
                    "id": tc.id,
                    "name": func_name,
                    "arguments": args,
                    "result": result,
                })
                messages.append({
                    "role": "tool",
                    "tool_call_id": tc.id,
                    "content": result,
                })
        
        return {
            "text": "Tool execution completed.",
            "tokens_in": 0,
            "tokens_out": 0,
            "tool_calls": all_tool_results,
        }

    def stream(self, prompt: str, system: str = ""):
        stream = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": prompt},
            ],
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content

PRICING = {
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-4-turbo": {"input": 10.00, "output": 30.00},
    "gpt-4": {"input": 30.00, "output": 60.00},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
}

DEFAULT_PRICING = {"input": 0.15, "output": 0.60}


def calculate_cost(model: str, tokens_in: int, tokens_out: int) -> float:
    pricing = PRICING.get(model, DEFAULT_PRICING)
    cost = (tokens_in * pricing["input"] + tokens_out * pricing["output"]) / 1_000_000
    return cost

import inspect
from typing import Callable, get_type_hints

PY_TO_JSON = {str: "string", int: "integer", float: "number", bool: "boolean"}


class Tool:
    def __init__(self, fn: Callable, risk: str):
        self.fn = fn
        self.name = fn.__name__
        self.risk = risk
        self.description = inspect.getdoc(fn) or ""
        self.schema = self.build_schema(fn)

    def build_schema(self, fn: Callable) -> dict:
        """Build the JSON schema the model sees, from the function's signature and docstring."""
        # this retrieves the type annotations of the function
        hints = get_type_hints(fn)
        properties = {}
        required = []

        # get the required parameters of the function and store their names and types
        for name, param in inspect.signature(fn).parameters.items():
            hint = hints.get(name)
            if hint not in PY_TO_JSON:
                raise TypeError(f"{self.name}.{name}: unsupported type {hint}")
            properties[name] = {"type": PY_TO_JSON[hint]}
            if param.default is inspect.Parameter.empty:
                required.append(name)
        # build schema
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": {"type": "object", "properties": properties, "required": required},
            },
        }


TOOLS: dict[str, Tool] = {}


def tool(risk: str = "read"):
    """Decorator that registers a function as a tool the model can call."""
    def decorator(fn: Callable) -> Callable:
        TOOLS[fn.__name__] = Tool(fn, risk)
        return fn
    return decorator


def schemas() -> list[dict]:
    """Return the JSON schemas of all registered tools."""
    return [t.schema for t in TOOLS.values()]


def execute(name: str, arguments: dict) -> str:
    """Run a tool call. Never raises: failures come back as 'Error: ...' strings for the model."""
    if name not in TOOLS:
        return f"Error: {name} is not a valid tool. Available tools: {', '.join(TOOLS)}"
    try:
        return str(TOOLS[name].fn(**arguments))
    except TypeError as e:
        return f"Error: bad arguments for {name}: {e}"
    except Exception as e:
        return f"Error: {type(e).__name__}: {e}"

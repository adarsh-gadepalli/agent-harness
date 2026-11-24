import ollama

from agent_harness.tools import registry

MODEL = "qwen2.5:7b"
OPTIONS = {"num_ctx": 8192}
MAX_STEPS = 10
RESULT_PREVIEW_CHARS = 200


def call_model(messages: list) -> tuple[str, list]:
    """Stream one model reply to the terminal. Returns (text, tool_calls)."""
    stream = ollama.chat(
        model=MODEL,
        messages=messages,
        tools=registry.schemas(),
        stream=True,
        options=OPTIONS,
    )
    content = ""
    tool_calls = []
    for chunk in stream:
        if chunk.message.content:
            print(chunk.message.content, end="", flush=True)
            content += chunk.message.content
        if chunk.message.tool_calls:
            tool_calls.extend(chunk.message.tool_calls)
    if content:
        print()
    return content, tool_calls


def run_turn(messages: list) -> str:
    """Run one user turn: call the model, run any tools it asks for, repeat until it answers in text."""
    # loop until tool calls terminate
    for _ in range(MAX_STEPS):

        # call model with stored chat history
        content, tool_calls = call_model(messages)

        # append the model's reply to the chat history (with tool calls if any)
        reply = {"role": "assistant", "content": content}
        if tool_calls:
            reply["tool_calls"] = tool_calls
        messages.append(reply)

        # if the model didn't call a tool, treat as terminal output
        if not tool_calls:
            return content

        # if the model called tool(s), run them and add the results to the chat history
        for call in tool_calls:
            name = call.function.name
            arguments = dict(call.function.arguments or {})
            print(f"[tool] {name}({arguments})")
            result = registry.execute(name, arguments)
            print(f"[result] {result[:RESULT_PREVIEW_CHARS]}")
            messages.append({"role": "tool", "content": result, "tool_name": name})

    stopped = f"Stopped: reached the {MAX_STEPS}-step limit."
    print(stopped)
    return stopped

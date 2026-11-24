from agent_harness.loop import MODEL, run_turn

SYSTEM_PROMPT = "You are a helpful assistant. Use tools when they help answer the question."


def main() -> None:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print(f"Chatting with {MODEL}. Commands: /reset, /exit")

    while True:
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not user_input:
            continue
        if user_input == "/exit":
            break
        if user_input == "/reset":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            print("History cleared.")
            continue

        messages.append({"role": "user", "content": user_input})
        try:
            run_turn(messages)
        except KeyboardInterrupt:
            print("\n[interrupted]")

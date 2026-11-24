import ollama

MODEL = "qwen2.5:7b"
SYSTEM_PROMPT = "You are a helpful assistant."


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

        stream = ollama.chat(
            model=MODEL,
            messages=messages,
            stream=True,
            options={"num_ctx": 8192},
        )

        reply = ""
        try:
            for chunk in stream:
                piece = chunk.message.content
                print(piece, end="", flush=True)
                reply += piece
        except KeyboardInterrupt:
            print("\n[interrupted]")
        print()

        messages.append({"role": "assistant", "content": reply})
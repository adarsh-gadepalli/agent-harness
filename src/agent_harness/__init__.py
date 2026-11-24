from agent_harness.loop import MODEL, run_turn
from agent_harness.research_state import SOURCES

SYSTEM_PROMPT = "You are a helpful assistant. Use tools when they help answer the question."


def main() -> None:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    print(f"Chatting with {MODEL}. Commands: /reset, /exit")

    # main loop
    while True:

        # get user input
        try:
            user_input = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        # command handling
        if not user_input:
            continue
        if user_input == "/exit":
            break
        if user_input == "/reset":
            messages = [{"role": "system", "content": SYSTEM_PROMPT}]
            SOURCES.clear()
            print("History cleared.")
            continue

        # add user input to messages
        messages.append({"role": "user", "content": user_input})

        # run the turn loop
        try:
            run_turn(messages)
        except KeyboardInterrupt:
            print("\n[interrupted]")

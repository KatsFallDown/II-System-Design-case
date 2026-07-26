import argparse
import json

from app.presentation import structured_trace
from app.runtime import get_pipeline
from app.schemas import TicketInput
from app.stage1_demo import CASES


DISPLAY_STEPS = (
    "Input validation",
    "Category classification",
    "Risk classification",
    "Similar ticket retrieval",
    "LLM analysis",
    "Decision policy",
)


def show(result) -> None:
    trace = structured_trace(result)
    for index, title in enumerate(DISPLAY_STEPS, start=1):
        summary = trace[index - 1]["details"]["summary"] if index <= len(trace) else "not recorded"
        print(f"[{index}/6] {title}: {summary}")
    print(f"\nCategory: {result.category} ({result.category_confidence:.3f})")
    print(f"Risk: {result.risk} ({result.risk_confidence:.3f})")
    print("Similarities:", [round(item.similarity, 3) for item in result.retrieved_examples])
    print("Action:", result.action)
    print("User message:", result.user_message)
    if result.support_ticket:
        print("Operator summary:", result.support_ticket.summary)


def run_demo(name: str) -> None:
    show(get_pipeline().process(CASES[name]))


def interactive() -> None:
    subject = input("Subject: ").strip()
    message = input("Message: ").strip()
    ticket = TicketInput(ticket_id="interactive", subject=subject, message=message)
    show(get_pipeline().process(ticket))


def smoke() -> None:
    pipeline = get_pipeline()
    happy = pipeline.process(CASES["happy"])
    risky = pipeline.process(CASES["risky"])
    if happy.action != "AUTO_REPLY" or risky.action != "ESCALATE":
        raise SystemExit(f"Smoke failed: happy={happy.action}, risky={risky.action}")
    print("Smoke OK: happy=AUTO_REPLY, risky=ESCALATE")

def main() -> None:
    parser = argparse.ArgumentParser(description="Support Ticket Automation PoC")
    parser.add_argument(
        "command",
        choices=("interactive", "demo-happy", "demo-risky", "smoke"),
    )
    args = parser.parse_args()
    if args.command == "interactive":
        interactive()
    elif args.command == "smoke":
        smoke()
    else:
        run_demo("happy" if args.command == "demo-happy" else "risky")


if __name__ == "__main__":
    main()

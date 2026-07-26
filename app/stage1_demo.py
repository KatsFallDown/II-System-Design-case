"""Stage 1 runner kept separate so the PoC can be checked without API/CLI code."""

import argparse
import json

from app.config import Settings
from app.llm.mock import MockLLMAdapter
from app.ml.retrieval import TicketRetriever
from app.ml.train import load_or_train
from app.pipeline import TicketPipeline
from app.schemas import TicketInput


CASES = {
    "happy": TicketInput(
        ticket_id="demo-happy",
        subject="Poor Performance of Digital Campaigns",
        message="Insufficient data analysis tools are currently employed.",
    ),
    "risky": TicketInput(
        ticket_id="demo-risky",
        subject="Unauthorized payment from stolen account",
        message=(
            "I found an unauthorized payment on my account. I did not approve it "
            "and need the account secured and the transaction investigated."
        ),
    ),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=("happy", "risky", "both"), default="both", nargs="?")
    args = parser.parse_args()
    settings = Settings()
    frame, category, risk, metrics = load_or_train(settings)
    pipeline = TicketPipeline(
        settings, category, risk, TicketRetriever(frame), MockLLMAdapter()
    )
    print("Models:", json.dumps(metrics))
    names = list(CASES) if args.scenario == "both" else [args.scenario]
    for name in names:
        result = pipeline.process(CASES[name])
        print(f"\n=== {name} ===")
        for step in result.trace:
            print("-", step)
        print("action:", result.action)
        print("user_message:", result.user_message)
        if result.support_ticket:
            print("operator_summary:", result.support_ticket.summary)


if __name__ == "__main__":
    main()

import argparse
import json
from app.config import Settings
from app.llm.mock import MockLLMAdapter
from app.ml.retrieval import TicketRetriever
from app.ml.train import load_or_train
from app.pipeline import TicketPipeline
from app.schemas import TicketInput


HAPPY = TicketInput(
    ticket_id="demo-happy", subject="Issue with Website Analytics Dashboard",
    message="My website analytics dashboard is not updating. I restarted the dashboard and verified my API credentials, but the issue still persists.",
)
RISKY = TicketInput(
    ticket_id="demo-risky", subject="Unauthorized payment from stolen account",
    message="I found an unauthorized payment on my account. I did not approve it and need the account secured and the transaction investigated.",
)


def build_pipeline(settings):
    frame, category, risk, metrics = load_or_train(settings)
    pipeline = TicketPipeline(settings, category, risk, TicketRetriever(frame), MockLLMAdapter())
    return pipeline, metrics


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", choices=("happy", "risky", "both"), default="both", nargs="?")
    args = parser.parse_args()
    pipeline, metrics = build_pipeline(Settings())
    print("Training:", json.dumps(metrics, indent=2))
    cases = [HAPPY, RISKY] if args.scenario == "both" else [HAPPY if args.scenario == "happy" else RISKY]
    for case in cases:
        result = pipeline.process(case)
        print(f"\n=== {case.ticket_id} ===")
        for step in result.trace:
            print("-", step)
        print(result.model_dump_json(indent=2))


if __name__ == "__main__":
    main()

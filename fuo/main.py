import argparse
from typing import Optional, Sequence

from fuo.bot import run_bot
from fuo.migrations import run_migrations


def main(input_args: Optional[Sequence[str]] = None):
    parser = argparse.ArgumentParser(description="FUO discord bot", prog="fuo-bot")
    parser.add_argument(
        "action",
        choices=["run", "migrate"],
        help="FUO bot actions:\n"
        "run: start the bot\n"
        "migrate: upgrade database to the latest",
    )
    args = parser.parse_args(input_args)
    if args.action == "run":
        run_bot()
    elif args.action == "migrate":
        run_migrations()

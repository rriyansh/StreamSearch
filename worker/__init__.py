"""Kafka worker process entrypoint."""

import signal
import sys

from streamsearch.ingestion import FrameConsumer
from streamsearch.logging_config import setup_logging


def main() -> None:
    setup_logging()
    consumer = FrameConsumer()

    def _shutdown(*_args):
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    consumer.run_forever()


if __name__ == "__main__":
    main()

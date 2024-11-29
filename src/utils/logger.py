import logging


def setup_logging(filename: str = "opml_manager.log") -> None:
    """Set up logging configuration."""
    logging.basicConfig(
        filename=filename,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
    )

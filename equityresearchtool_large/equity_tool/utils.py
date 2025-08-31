import logging, os

def setup_logger(name="equitytool"):
    os.makedirs("logs", exist_ok=True)
    logging.basicConfig(
        filename="logs/tool.log",
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )
    return logging.getLogger(name)

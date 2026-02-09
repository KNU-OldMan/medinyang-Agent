import logging
import os
from datetime import datetime
from typing import Any

LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

log_filename = f"agent_flow_{datetime.now().strftime('%Y%m%d')}.log"
log_path = os.path.join(LOG_DIR, log_filename)

logger = logging.getLogger("agent_flow")
logger.setLevel(logging.INFO)

# 중복 핸들러 방지
if logger.hasHandlers():
    logger.handlers.clear()

file_handler = logging.FileHandler(log_path, encoding="utf-8")
file_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(file_formatter)
logger.addHandler(file_handler)

console_handler = logging.StreamHandler()
console_formatter = logging.Formatter("%(message)s")
console_handler.setFormatter(console_formatter)
logger.addHandler(console_handler)


def log_agent_step(agent_name: str, step_description: str, data: Any = None):
    message = f"[{agent_name}] {step_description}"
    if data is not None:
        message += f"\nData: {data}"
    logger.info(message)
    logger.info("-" * 50)

import os
from typing import Dict, Any

import yaml

_config_path = os.getenv("DELTA_NODE_CONFIG", "config/config.yaml")

with open(_config_path, mode="r", encoding="utf-8") as f:
    _c = yaml.safe_load(f)

_log = _c.get("log")
log_level: str = _log.get("level", "DEBUG")
log_dir: str = _log.get("dir", "")

db: str = _c.get("db", "")

_discord: Dict[str, Any] = _c.get("discord")

discord_token: str = _discord.get("token", "")
discord_role: str = _discord.get("role", "")

info_color = "#03a8f4"
success_color = "#66bb6a"
error_color = "#e50113"
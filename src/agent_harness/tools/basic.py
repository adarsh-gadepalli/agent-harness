from datetime import datetime
from zoneinfo import ZoneInfo

from agent_harness.tools.registry import tool


# simple tool to get the current time in a given timezone
@tool(risk="read")
def get_time(timezone: str = "UTC") -> str:
    """Get the current date and time in an IANA timezone, e.g. 'America/Chicago' or 'Asia/Tokyo'."""
    return datetime.now(ZoneInfo(timezone)).isoformat(timespec="seconds")

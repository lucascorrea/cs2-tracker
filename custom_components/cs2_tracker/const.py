"""Constants for CS2 Tracker."""
from datetime import timedelta
from homeassistant.const import Platform

DOMAIN = "cs2_tracker"
ATTRIBUTION = "Data from custom match API"
COORDINATOR = "coordinator"
PLATFORMS = [Platform.SENSOR]
ISSUE_URL = "https://github.com/lucascorrea/cs2-tracker/issues"
VERSION = "0.1.0"

# Config keys
CONF_NAME = "name"
CONF_TEAM_ID = "team_id"  # Used in default API URL path (e.g. FURIA, PaiN_Gaming)
CONF_TEAM_SLUG = "team_slug"  # Legacy, same as team_id
CONF_API_URL = "api_url"
CONF_USE_CUSTOM_URL = "use_custom_url"
CONF_TIMEZONE = "timezone"
CONF_JSON_PATH_TEAM_LOGO = "json_path_team_logo"
CONF_JSON_PATH_OPP_LOGO = "json_path_opp_logo"
CONF_JSON_PATH_TEAM_NAME = "json_path_team_name"
CONF_JSON_PATH_OPP_NAME = "json_path_opp_name"
CONF_JSON_PATH_SCORE = "json_path_score"
CONF_JSON_PATH_OPP_SCORE = "json_path_opp_score"
CONF_JSON_PATH_DATE = "json_path_date"
CONF_JSON_PATH_VENUE = "json_path_venue"
CONF_JSON_PATH_STATUS = "json_path_status"  # e.g. "live" -> STATE_IN
CONF_UPDATE_INTERVAL_MINUTES = "update_interval_minutes"

# Default API (cs2-upcoming-matches.vercel.app)
DEFAULT_API_BASE = "https://cs2-upcoming-matches.vercel.app/api"

# Defaults
DEFAULT_NAME = "CS2 Tracker"
DEFAULT_UPDATE_INTERVAL_MINUTES = 5
DEFAULT_TIMEOUT = 30
DEFAULT_REFRESH_RATE = timedelta(minutes=5)

# Timezone options for default API (?timezone=). Value is sent to API.
TIMEZONE_OPTIONS: list[tuple[str, str]] = [
    ("UTC (GMT+0)", "0"),
    ("GMT+1", "1"),
    ("GMT+2", "2"),
    ("GMT+3", "3"),
    ("GMT+4", "4"),
    ("GMT+5", "5"),
    ("GMT+5:30", "5.5"),
    ("GMT+6", "6"),
    ("GMT+7", "7"),
    ("GMT+8", "8"),
    ("GMT+9", "9"),
    ("GMT+10", "10"),
    ("GMT+11", "11"),
    ("GMT+12", "12"),
    ("GMT+13", "13"),
    ("GMT+14", "14"),
    ("GMT-1", "-1"),
    ("GMT-2", "-2"),
    ("GMT-3", "-3"),
    ("GMT-4", "-4"),
    ("GMT-5", "-5"),
    ("GMT-6", "-6"),
    ("GMT-7", "-7"),
    ("GMT-8", "-8"),
    ("GMT-9", "-9"),
    ("GMT-10", "-10"),
    ("GMT-11", "-11"),
]

# JSON path defaults for default API (cs2-upcoming-matches.vercel.app)
# Response: { team, logo, matches: [ { teamScore, opponentScore, status, ... } ] }
DEFAULT_PATH_TEAM_LOGO = "logo"
DEFAULT_PATH_OPP_LOGO = "matches.0.opponentLogo"
DEFAULT_PATH_TEAM_NAME = "team"
DEFAULT_PATH_OPP_NAME = "matches.0.opponent"
DEFAULT_PATH_SCORE = "matches.0.teamScore"
DEFAULT_PATH_OPP_SCORE = "matches.0.opponentScore"
DEFAULT_PATH_DATE = "matches.0.date_iso"
DEFAULT_PATH_VENUE = "matches.0.tournament"
DEFAULT_PATH_STATUS = "matches.0.status"  # "live" -> IN, "upcoming" -> PRE

# Sensor states (aligned with common sports trackers)
STATE_PRE = "PRE"
STATE_IN = "IN"
STATE_POST = "POST"
STATE_NOT_FOUND = "NOT_FOUND"

DEFAULT_ICON = "mdi:target"

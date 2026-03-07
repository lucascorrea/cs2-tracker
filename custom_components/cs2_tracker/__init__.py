"""CS2 Tracker - next match for your team in Home Assistant."""
from datetime import datetime, timedelta, timezone
import logging

import aiohttp
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    CONF_API_URL,
    CONF_TEAM_ID,
    CONF_TEAM_SLUG,
    CONF_TIMEZONE,
    CONF_USE_CUSTOM_URL,
    DEFAULT_API_BASE,
    CONF_JSON_PATH_DATE,
    CONF_JSON_PATH_OPP_LOGO,
    CONF_JSON_PATH_STATUS,
    CONF_JSON_PATH_OPP_NAME,
    CONF_JSON_PATH_OPP_SCORE,
    CONF_JSON_PATH_TEAM_LOGO,
    CONF_JSON_PATH_TEAM_NAME,
    CONF_JSON_PATH_VENUE,
    CONF_JSON_PATH_SCORE,
    CONF_UPDATE_INTERVAL_MINUTES,
    COORDINATOR,
    DEFAULT_PATH_DATE,
    DEFAULT_PATH_STATUS,
    DEFAULT_PATH_OPP_LOGO,
    DEFAULT_PATH_OPP_NAME,
    DEFAULT_PATH_OPP_SCORE,
    DEFAULT_PATH_TEAM_LOGO,
    DEFAULT_PATH_TEAM_NAME,
    DEFAULT_PATH_VENUE,
    DEFAULT_PATH_SCORE,
    DEFAULT_REFRESH_RATE,
    DEFAULT_TIMEOUT,
    DOMAIN,
    ISSUE_URL,
    PLATFORMS,
    STATE_IN,
    STATE_NOT_FOUND,
    STATE_POST,
    STATE_PRE,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


def _get_by_path(obj: dict, path: str):
    """Get value from dict by dot/index path (e.g. team.logos.0.href)."""
    if not path or not path.strip():
        return None
    current = obj
    for part in path.strip().split("."):
        if current is None:
            return None
        part = part.strip()
        if not part:
            continue
        try:
            idx = int(part)
            if isinstance(current, (list, tuple)):
                current = current[idx] if idx < len(current) else None
            else:
                current = None
        except ValueError:
            current = current.get(part) if isinstance(current, dict) else None
    return current


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate config entry from version 1 to 2 (team_id, timezone, use_custom_url)."""
    if entry.version >= 2:
        return True
    data = dict(entry.data)
    if CONF_TEAM_ID not in data and CONF_TEAM_SLUG in data:
        data[CONF_TEAM_ID] = data[CONF_TEAM_SLUG]
    if CONF_TIMEZONE not in data:
        data[CONF_TIMEZONE] = "0"
    if CONF_USE_CUSTOM_URL not in data:
        url = data.get(CONF_API_URL, "")
        data[CONF_USE_CUSTOM_URL] = not (url.startswith(DEFAULT_API_BASE + "/") or url.startswith(DEFAULT_API_BASE))
    hass.config_entries.async_update_entry(entry, data=data, version=2)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up the config entry."""
    name = entry.data.get(CONF_NAME, "CS2 Tracker")
    _LOGGER.info(
        "%s: Setting up CS2 Tracker %s - %s",
        name,
        VERSION,
        ISSUE_URL,
    )

    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {}

    config = {**entry.data}
    if entry.options:
        config.update(entry.options)
    interval_min = config.get(CONF_UPDATE_INTERVAL_MINUTES, 5)
    update_interval = timedelta(minutes=interval_min)

    coordinator = CS2TrackerCoordinator(hass, config, entry, update_interval)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = {COORDINATOR: coordinator}
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload when options change."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the config entry."""
    if entry.entry_id in hass.data.get(DOMAIN, {}):
        coordinator = hass.data[DOMAIN][entry.entry_id].get(COORDINATOR)
        if coordinator and hasattr(coordinator, "async_shutdown"):
            await coordinator.async_shutdown()
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unload_ok


class CS2TrackerCoordinator(DataUpdateCoordinator):
    """Coordinator that fetches the API and applies JSON paths."""

    def __init__(self, hass: HomeAssistant, config: dict, entry: ConfigEntry, update_interval: timedelta) -> None:
        self.config = {**config}
        if entry.options:
            self.config.update(entry.options)
        self.entry = entry
        self._session: aiohttp.ClientSession | None = None
        super().__init__(
            hass,
            _LOGGER,
            name=config.get(CONF_NAME, "CS2 Tracker"),
            update_interval=update_interval,
        )

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def async_shutdown(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    def _apply_paths(self, data: dict) -> dict:
        """Build attributes from JSON using configured paths."""
        c = self.config
        out = {
            "state": STATE_NOT_FOUND,
            "team_logo": _get_by_path(data, c.get(CONF_JSON_PATH_TEAM_LOGO) or DEFAULT_PATH_TEAM_LOGO),
            "opponent_logo": _get_by_path(data, c.get(CONF_JSON_PATH_OPP_LOGO) or DEFAULT_PATH_OPP_LOGO),
            "team_name": _get_by_path(data, c.get(CONF_JSON_PATH_TEAM_NAME) or DEFAULT_PATH_TEAM_NAME),
            "opponent_name": _get_by_path(data, c.get(CONF_JSON_PATH_OPP_NAME) or DEFAULT_PATH_OPP_NAME),
            "team_score": _get_by_path(data, c.get(CONF_JSON_PATH_SCORE) or DEFAULT_PATH_SCORE),
            "opponent_score": _get_by_path(data, c.get(CONF_JSON_PATH_OPP_SCORE) or DEFAULT_PATH_OPP_SCORE),
            "date": _get_by_path(data, c.get(CONF_JSON_PATH_DATE) or DEFAULT_PATH_DATE),
            "venue": _get_by_path(data, c.get(CONF_JSON_PATH_VENUE) or DEFAULT_PATH_VENUE),
            "status": _get_by_path(data, c.get(CONF_JSON_PATH_STATUS) or DEFAULT_PATH_STATUS),
            "last_update": datetime.now(timezone.utc).isoformat(),
            "api_url": c.get(CONF_API_URL, ""),
            "api_message": None,
            "raw": data,
        }
        # Check if matches array is empty
        matches = data.get("matches", [])
        if isinstance(matches, list) and len(matches) == 0:
            out["state"] = STATE_NOT_FOUND
            out["api_message"] = None  # Let frontend handle localization
        else:
            # Infer state: status "live" -> IN; status "finished" or scores -> POST; else PRE
            status_val = out.get("status")
            status_str = str(status_val).lower().strip() if status_val is not None else ""
            is_live = status_str == "live"
            is_finished = status_str == "finished"
            if is_live:
                out["state"] = STATE_IN
            elif is_finished:
                out["state"] = STATE_POST
            else:
                team_s = out["team_score"]
                opp_s = out["opponent_score"]
                if team_s is not None and opp_s is not None:
                    try:
                        int(team_s), int(opp_s)
                        out["state"] = STATE_POST
                    except (TypeError, ValueError):
                        out["state"] = STATE_PRE
                elif out["team_name"] or out["opponent_name"] or out["date"]:
                    out["state"] = STATE_PRE
        return out

    async def _async_update_data(self) -> dict:
        url = self.config.get(CONF_API_URL)
        if not url:
            raise UpdateFailed("API URL not configured")
        session = await self._get_session()
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as resp:
                if resp.status != 200:
                    raise UpdateFailed(f"API returned {resp.status}")
                data = await resp.json()
        except aiohttp.ClientError as e:
            raise UpdateFailed(f"Network error: {e}") from e
        except Exception as e:
            raise UpdateFailed(str(e)) from e
        return self._apply_paths(data)

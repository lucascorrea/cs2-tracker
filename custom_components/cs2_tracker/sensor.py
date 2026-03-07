"""CS2 Tracker sensor - next match."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import ATTR_ATTRIBUTION
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import slugify

from .const import (
    ATTRIBUTION,
    COORDINATOR,
    DEFAULT_ICON,
    DOMAIN,
    ISSUE_URL,
    VERSION,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor from the config entry (UI)."""
    coordinator = hass.data[DOMAIN][entry.entry_id][COORDINATOR]
    _LOGGER.info(
        "%s: Adding sensor using CS2 Tracker %s - %s",
        entry.data.get("name", "CS2 Tracker"),
        VERSION,
        ISSUE_URL,
    )
    async_add_entities([CS2TrackerSensor(coordinator, entry)])


class CS2TrackerSensor(CoordinatorEntity):
    """Sensor that exposes next CS2 match state and attributes."""

    def __init__(self, coordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._entry = entry
        self._name = entry.data.get("name", "CS2 Tracker")

    @property
    def unique_id(self) -> str:
        return f"cs2_tracker_{slugify(self._name)}_{self._entry.entry_id}"

    @property
    def name(self) -> str:
        return self._name

    @property
    def icon(self) -> str:
        return DEFAULT_ICON

    @property
    def state(self) -> str | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("state")

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        attrs: dict[str, Any] = {ATTR_ATTRIBUTION: ATTRIBUTION}
        if self.coordinator.data is None:
            return attrs
        d = self.coordinator.data
        attrs["team_logo"] = d.get("team_logo")
        attrs["opponent_logo"] = d.get("opponent_logo")
        attrs["team_name"] = d.get("team_name")
        attrs["opponent_name"] = d.get("opponent_name")
        attrs["team_score"] = d.get("team_score")
        attrs["opponent_score"] = d.get("opponent_score")
        attrs["date"] = d.get("date")
        attrs["venue"] = d.get("venue")
        attrs["status"] = d.get("status")
        attrs["last_update"] = d.get("last_update")
        attrs["api_url"] = d.get("api_url")
        attrs["api_message"] = d.get("api_message")
        return attrs

    @property
    def available(self) -> bool:
        return self.coordinator.last_update_success

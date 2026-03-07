"""Config flow for CS2 Tracker."""
from __future__ import annotations

import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_API_URL,
    CONF_JSON_PATH_DATE,
    CONF_JSON_PATH_STATUS,
    CONF_JSON_PATH_OPP_LOGO,
    CONF_JSON_PATH_OPP_NAME,
    CONF_JSON_PATH_OPP_SCORE,
    CONF_JSON_PATH_TEAM_LOGO,
    CONF_JSON_PATH_TEAM_NAME,
    CONF_JSON_PATH_VENUE,
    CONF_JSON_PATH_SCORE,
    CONF_TEAM_ID,
    CONF_TIMEZONE,
    CONF_UPDATE_INTERVAL_MINUTES,
    CONF_USE_CUSTOM_URL,
    DEFAULT_API_BASE,
    DEFAULT_NAME,
    DEFAULT_PATH_DATE,
    DEFAULT_PATH_STATUS,
    DEFAULT_PATH_OPP_LOGO,
    DEFAULT_PATH_OPP_NAME,
    DEFAULT_PATH_OPP_SCORE,
    DEFAULT_PATH_TEAM_LOGO,
    DEFAULT_PATH_TEAM_NAME,
    DEFAULT_PATH_VENUE,
    DEFAULT_PATH_SCORE,
    DEFAULT_UPDATE_INTERVAL_MINUTES,
    DOMAIN,
    TIMEZONE_OPTIONS,
)

_LOGGER = logging.getLogger(__name__)


def _build_default_url(team_id: str, timezone: str) -> str:
    team = (team_id or "").strip()
    tz = (timezone or "0").strip()
    base = DEFAULT_API_BASE.rstrip("/")
    return f"{base}/{team}?timezone={tz}"


def _schema_user(user_input: dict[str, Any] | None) -> vol.Schema:
    if user_input is None:
        user_input = {}
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default=user_input.get(CONF_NAME, DEFAULT_NAME)): str,
            vol.Required(
                CONF_TEAM_ID,
                default=user_input.get(CONF_TEAM_ID) or user_input.get("team_slug", ""),
            ): str,
            vol.Required(
                CONF_TIMEZONE,
                default=user_input.get(CONF_TIMEZONE, "0"),
            ): vol.In({v: k for k, v in TIMEZONE_OPTIONS}),
            vol.Required(
                CONF_USE_CUSTOM_URL,
                default=user_input.get(CONF_USE_CUSTOM_URL, False),
            ): bool,
            vol.Optional(CONF_API_URL, default=user_input.get(CONF_API_URL, "")): str,
            vol.Required(
                CONF_UPDATE_INTERVAL_MINUTES,
                default=user_input.get(CONF_UPDATE_INTERVAL_MINUTES, DEFAULT_UPDATE_INTERVAL_MINUTES),
            ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
        }
    )


def _schema_paths(user_input: dict[str, Any] | None) -> vol.Schema:
    if user_input is None:
        user_input = {}
    def _d(key: str, default: str) -> Any:
        return user_input.get(key, default)

    return vol.Schema(
        {
            vol.Optional(
                CONF_JSON_PATH_TEAM_LOGO,
                default=_d(CONF_JSON_PATH_TEAM_LOGO, DEFAULT_PATH_TEAM_LOGO),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_OPP_LOGO,
                default=_d(CONF_JSON_PATH_OPP_LOGO, DEFAULT_PATH_OPP_LOGO),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_TEAM_NAME,
                default=_d(CONF_JSON_PATH_TEAM_NAME, DEFAULT_PATH_TEAM_NAME),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_OPP_NAME,
                default=_d(CONF_JSON_PATH_OPP_NAME, DEFAULT_PATH_OPP_NAME),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_SCORE,
                default=_d(CONF_JSON_PATH_SCORE, DEFAULT_PATH_SCORE),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_OPP_SCORE,
                default=_d(CONF_JSON_PATH_OPP_SCORE, DEFAULT_PATH_OPP_SCORE),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_DATE,
                default=_d(CONF_JSON_PATH_DATE, DEFAULT_PATH_DATE),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_VENUE,
                default=_d(CONF_JSON_PATH_VENUE, DEFAULT_PATH_VENUE),
            ): str,
            vol.Optional(
                CONF_JSON_PATH_STATUS,
                default=_d(CONF_JSON_PATH_STATUS, DEFAULT_PATH_STATUS),
            ): str,
        }
    )


async def _validate_api_url(hass: HomeAssistant, url: str) -> str | None:
    """Validate URL and test connection. Returns None if OK, error key otherwise."""
    if not url or not url.strip().startswith(("http://", "https://")):
        return "invalid_url"
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return "cannot_connect"
                await resp.json()
    except Exception as e:
        _LOGGER.debug("API validation failed: %s", e)
        return "cannot_connect"
    return None


class CS2TrackerFlowHandler(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for CS2 Tracker."""

    VERSION = 2
    _data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """First step: name, team ID, timezone, default or custom URL, interval."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._data.update(user_input)
            use_custom = user_input.get(CONF_USE_CUSTOM_URL, False)
            if use_custom:
                api_url = (user_input.get(CONF_API_URL) or "").strip()
                if not api_url:
                    errors["base"] = "invalid_url"
                else:
                    self._data[CONF_API_URL] = api_url
                    err = await _validate_api_url(self.hass, api_url)
                    if err:
                        errors["base"] = err
                    else:
                        return await self.async_step_paths()
            else:
                team_id = (user_input.get(CONF_TEAM_ID) or "").strip()
                if not team_id:
                    errors["base"] = "invalid_team_id"
                else:
                    timezone_val = user_input.get(CONF_TIMEZONE, "0")
                    api_url = _build_default_url(team_id, timezone_val)
                    self._data[CONF_API_URL] = api_url
                    err = await _validate_api_url(self.hass, api_url)
                    if err:
                        errors["base"] = err
                    else:
                        return await self.async_step_paths()

        return self.async_show_form(
            step_id="user",
            data_schema=_schema_user(user_input),
            errors=errors,
        )

    async def async_step_paths(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Second step: JSON paths (optional)."""
        if user_input is not None:
            self._data.update(user_input)
            return self.async_create_entry(title=self._data[CONF_NAME], data=self._data)

        return self.async_show_form(
            step_id="paths",
            data_schema=_schema_paths(self._data),
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Options flow."""
        return CS2TrackerOptionsFlow(config_entry)


class CS2TrackerOptionsFlow(config_entries.OptionsFlow):
    """Options flow to change URL, timezone, interval and JSON paths."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self.entry = config_entry
        self._options: dict[str, Any] = dict(config_entry.options)
        self._data: dict[str, Any] = {**config_entry.data, **config_entry.options}

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> config_entries.FlowResult:
        """Options: use custom URL, team_id, timezone, interval, JSON paths."""
        if user_input is not None:
            self._options.update(user_input)
            use_custom = user_input.get(CONF_USE_CUSTOM_URL, False)
            if use_custom:
                self._options[CONF_API_URL] = (user_input.get(CONF_API_URL) or "").strip()
            else:
                team_id = (user_input.get(CONF_TEAM_ID) or "").strip()
                tz = (user_input.get(CONF_TIMEZONE) or "0").strip()
                self._options[CONF_API_URL] = _build_default_url(team_id, tz)
            return self.async_create_entry(title="", data=self._options)

        use_custom = self._data.get(CONF_USE_CUSTOM_URL, False)
        # Infer current team_id from URL if default format
        team_id = self._data.get(CONF_TEAM_ID, "")
        if not team_id and not use_custom:
            url = self._data.get(CONF_API_URL, "")
            if url.startswith(DEFAULT_API_BASE + "/"):
                rest = url[len(DEFAULT_API_BASE) + 1 :].split("?")[0]
                if rest:
                    team_id = rest
        timezone_val = self._data.get(CONF_TIMEZONE, "0")

        schema = vol.Schema(
            {
                vol.Required(
                    CONF_USE_CUSTOM_URL,
                    default=use_custom,
                ): bool,
                vol.Optional(CONF_TEAM_ID, default=team_id): str,
                vol.Required(
                    CONF_TIMEZONE,
                    default=timezone_val,
                ): vol.In({v: k for k, v in TIMEZONE_OPTIONS}),
                vol.Optional(
                    CONF_API_URL,
                    default=self._data.get(CONF_API_URL, ""),
                ): str,
                vol.Required(
                    CONF_UPDATE_INTERVAL_MINUTES,
                    default=self._data.get(CONF_UPDATE_INTERVAL_MINUTES, DEFAULT_UPDATE_INTERVAL_MINUTES),
                ): vol.All(vol.Coerce(int), vol.Range(min=1, max=60)),
                vol.Optional(
                    CONF_JSON_PATH_TEAM_LOGO,
                    default=self._data.get(CONF_JSON_PATH_TEAM_LOGO, DEFAULT_PATH_TEAM_LOGO),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_OPP_LOGO,
                    default=self._data.get(CONF_JSON_PATH_OPP_LOGO, DEFAULT_PATH_OPP_LOGO),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_TEAM_NAME,
                    default=self._data.get(CONF_JSON_PATH_TEAM_NAME, DEFAULT_PATH_TEAM_NAME),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_OPP_NAME,
                    default=self._data.get(CONF_JSON_PATH_OPP_NAME, DEFAULT_PATH_OPP_NAME),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_SCORE,
                    default=self._data.get(CONF_JSON_PATH_SCORE, DEFAULT_PATH_SCORE),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_OPP_SCORE,
                    default=self._data.get(CONF_JSON_PATH_OPP_SCORE, DEFAULT_PATH_OPP_SCORE),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_DATE,
                    default=self._data.get(CONF_JSON_PATH_DATE, DEFAULT_PATH_DATE),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_VENUE,
                    default=self._data.get(CONF_JSON_PATH_VENUE, DEFAULT_PATH_VENUE),
                ): str,
                vol.Optional(
                    CONF_JSON_PATH_STATUS,
                    default=self._data.get(CONF_JSON_PATH_STATUS, DEFAULT_PATH_STATUS),
                ): str,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

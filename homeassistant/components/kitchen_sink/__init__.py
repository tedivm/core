"""The Kitchen Sink integration contains demonstrations of various odds and ends.

This sets up a demo environment of features which are obscure or which represent
incorrect behavior, and are thus not wanted in the demo integration.
"""
from __future__ import annotations

import datetime
from random import random

from homeassistant.components.recorder import get_instance
from homeassistant.components.recorder.models import StatisticData, StatisticMetaData
from homeassistant.components.recorder.statistics import (
    async_add_external_statistics,
    get_last_statistics,
)
from homeassistant.const import UnitOfEnergy, UnitOfTemperature, UnitOfVolume
from homeassistant.core import HomeAssistant
from homeassistant.helpers.issue_registry import IssueSeverity, async_create_issue
from homeassistant.helpers.typing import ConfigType
import homeassistant.util.dt as dt_util

DOMAIN = "kitchen_sink"


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the demo environment."""
    # Create issues
    _create_issues(hass)

    # Insert some external statistics
    if "recorder" in hass.config.components:
        await _insert_statistics(hass)

    return True


def _create_issues(hass):
    """Create some issue registry issues."""
    async_create_issue(
        hass,
        DOMAIN,
        "transmogrifier_deprecated",
        breaks_in_ha_version="2023.1.1",
        is_fixable=False,
        learn_more_url="https://en.wiktionary.org/wiki/transmogrifier",
        severity=IssueSeverity.WARNING,
        translation_key="transmogrifier_deprecated",
    )

    async_create_issue(
        hass,
        DOMAIN,
        "out_of_blinker_fluid",
        breaks_in_ha_version="2023.1.1",
        is_fixable=True,
        learn_more_url="https://www.youtube.com/watch?v=b9rntRxLlbU",
        severity=IssueSeverity.CRITICAL,
        translation_key="out_of_blinker_fluid",
    )

    async_create_issue(
        hass,
        DOMAIN,
        "unfixable_problem",
        is_fixable=False,
        learn_more_url="https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        severity=IssueSeverity.WARNING,
        translation_key="unfixable_problem",
    )

    async_create_issue(
        hass,
        DOMAIN,
        "bad_psu",
        is_fixable=True,
        learn_more_url="https://www.youtube.com/watch?v=b9rntRxLlbU",
        severity=IssueSeverity.CRITICAL,
        translation_key="bad_psu",
    )

    async_create_issue(
        hass,
        DOMAIN,
        "cold_tea",
        is_fixable=True,
        severity=IssueSeverity.WARNING,
        translation_key="cold_tea",
    )


def _generate_mean_statistics(
    start: datetime.datetime, end: datetime.datetime, init_value: float, max_diff: float
) -> list[StatisticData]:
    statistics: list[StatisticData] = []
    mean = init_value
    now = start
    while now < end:
        mean = mean + random() * max_diff - max_diff / 2
        statistics.append(
            {
                "start": now,
                "mean": mean,
                "min": mean - random() * max_diff,
                "max": mean + random() * max_diff,
            }
        )
        now = now + datetime.timedelta(hours=1)

    return statistics


async def _insert_sum_statistics(
    hass: HomeAssistant,
    metadata: StatisticMetaData,
    start: datetime.datetime,
    end: datetime.datetime,
    max_diff: float,
) -> None:
    statistics: list[StatisticData] = []
    now = start
    sum_ = 0.0
    statistic_id = metadata["statistic_id"]

    last_stats = await get_instance(hass).async_add_executor_job(
        get_last_statistics, hass, 1, statistic_id, False, {"sum"}
    )
    if statistic_id in last_stats:
        sum_ = last_stats[statistic_id][0]["sum"] or 0
    while now < end:
        sum_ = sum_ + random() * max_diff
        statistics.append(
            {
                "start": now,
                "sum": sum_,
            }
        )
        now = now + datetime.timedelta(hours=1)

    async_add_external_statistics(hass, metadata, statistics)


async def _insert_statistics(hass: HomeAssistant) -> None:
    """Insert some fake statistics."""
    now = dt_util.now()
    yesterday = now - datetime.timedelta(days=1)
    yesterday_midnight = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    today_midnight = yesterday_midnight + datetime.timedelta(days=1)

    # Fake yesterday's temperatures
    metadata: StatisticMetaData = {
        "source": DOMAIN,
        "name": "Outdoor temperature",
        "statistic_id": f"{DOMAIN}:temperature_outdoor",
        "unit_of_measurement": UnitOfTemperature.CELSIUS,
        "has_mean": True,
        "has_sum": False,
    }
    statistics = _generate_mean_statistics(yesterday_midnight, today_midnight, 15, 1)
    async_add_external_statistics(hass, metadata, statistics)

    # Add external energy consumption in kWh, ~ 12 kWh / day
    # This should be possible to pick for the energy dashboard
    metadata = {
        "source": DOMAIN,
        "name": "Energy consumption 1",
        "statistic_id": f"{DOMAIN}:energy_consumption_kwh",
        "unit_of_measurement": UnitOfEnergy.KILO_WATT_HOUR,
        "has_mean": False,
        "has_sum": True,
    }
    await _insert_sum_statistics(hass, metadata, yesterday_midnight, today_midnight, 1)

    # Add external energy consumption in MWh, ~ 12 kWh / day
    # This should not be possible to pick for the energy dashboard
    metadata = {
        "source": DOMAIN,
        "name": "Energy consumption 2",
        "statistic_id": f"{DOMAIN}:energy_consumption_mwh",
        "unit_of_measurement": UnitOfEnergy.MEGA_WATT_HOUR,
        "has_mean": False,
        "has_sum": True,
    }
    await _insert_sum_statistics(
        hass, metadata, yesterday_midnight, today_midnight, 0.001
    )

    # Add external gas consumption in m³, ~6 m3/day
    # This should be possible to pick for the energy dashboard
    metadata = {
        "source": DOMAIN,
        "name": "Gas consumption 1",
        "statistic_id": f"{DOMAIN}:gas_consumption_m3",
        "unit_of_measurement": UnitOfVolume.CUBIC_METERS,
        "has_mean": False,
        "has_sum": True,
    }
    await _insert_sum_statistics(
        hass, metadata, yesterday_midnight, today_midnight, 0.5
    )

    # Add external gas consumption in ft³, ~180 ft3/day
    # This should not be possible to pick for the energy dashboard
    metadata = {
        "source": DOMAIN,
        "name": "Gas consumption 2",
        "statistic_id": f"{DOMAIN}:gas_consumption_ft3",
        "unit_of_measurement": UnitOfVolume.CUBIC_FEET,
        "has_mean": False,
        "has_sum": True,
    }
    await _insert_sum_statistics(hass, metadata, yesterday_midnight, today_midnight, 15)
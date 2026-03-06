![maintained](https://img.shields.io/maintenance/yes/2026.svg)
[![hacs_badge](https://img.shields.io/badge/hacs-default-green.svg)](https://github.com/custom-components/hacs)
[![ha_version](https://img.shields.io/badge/home%20assistant-2021.12%2B-green.svg)](https://www.home-assistant.io)
![version](https://img.shields.io/badge/version-3.1.4-green.svg)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

HApendel
========

> **Fork of [HASL](https://github.com/hasl-sensor/integration) (Home Assistant SL integration) by DSorlov**, renamed and maintained as HApendel with updated API support for the new keyless Trafiklab endpoints introduced in 2024.

Home Assistant integration providing sensors for [Stockholms Lokaltrafik (SL)](https://sl.se/) and national public transport via [ResRobot](https://resrobot.se/).

## What changed from HASL

- Renamed from `hasl3` to `HApendel`
- Migrated all SL APIs to new Trafiklab integration endpoints (old `api.sl.se` was shut down March 2024)
- SL sensors no longer require API keys
- Fixed departure board parsing (plural transport type keys in new API)
- Fixed route planner parsing for Journey Planner v2 response format
- Fixed traffic status categorization by transport mode

## Features

- **Departure board** — real-time departures from any SL stop or ResRobot stop
- **Arrival board** — arrivals via ResRobot
- **Deviations** — service disruptions and planned works for SL lines and stops
- **Traffic status** — overall SL network status per transport mode (metro, bus, tram, train, ferry)
- **Vehicle locations** — real-time positions of SL vehicles
- **Route planner** — journey planning via SL Journey Planner or ResRobot

## API Keys

As of 2024, the SL APIs no longer require API keys. The following sensor types work without any key:

| Sensor type | API key required |
|---|---|
| SL Departure board | No |
| SL Deviations | No |
| SL Traffic status | No |
| SL Vehicle locations | No |
| SL Route planner | No |
| ResRobot Departures | **Yes** |
| ResRobot Arrivals | **Yes** |
| ResRobot Route planner | **Yes** |

ResRobot API keys are free and available at [Trafiklab](https://www.trafiklab.se/).

## Install using HACS

1. If you haven't already, [install HACS](https://hacs.xyz/docs/setup/download).
2. In HACS, search for **HApendel** under _Integrations_ and install it. Restart Home Assistant.
3. After restarting, reload the browser (clears cache).
4. Go to _Settings_ > _Integrations_ and add **HApendel**.
5. If using ResRobot sensors, get a free API key at [Trafiklab](https://www.trafiklab.se/).
6. Find SL stop IDs using the built-in _Location Lookup_ service.

## Finding Stop IDs

Use the **HApendel Location Lookup** service in Home Assistant (_Developer Tools_ > _Services_) to search for stop names and retrieve their site IDs. You do not need an API key for this.

## Visualization

HApendel works with the original HASL Lovelace cards:

- [hasl-departure-card](https://github.com/hasl-platform/lovelace-hasl-departure-card) — departure tables
- [hasl-traffic-status-card](https://github.com/hasl-platform/lovelace-hasl-traffic-status-card) — traffic status overview

![card](https://user-images.githubusercontent.com/8133650/56198334-0a150f00-603b-11e9-9e93-92be212d7f7b.PNG)

## Credits

Based on [HASL](https://github.com/hasl-sensor/integration) by [DSorlov](https://github.com/DSorlov) and contributors, licensed under Apache 2.0.

__version__ = '3.1.4'

# New SL Transport API - no key required
SL_TRANSPORT_BASE_URL = 'https://transport.integration.sl.se/v1/'
SITES_URL = SL_TRANSPORT_BASE_URL + 'sites'
DEPARTURES_URL = SL_TRANSPORT_BASE_URL + 'sites/{}/departures'

# New SL Deviations API - no key required
SL_DEVIATIONS_URL = 'https://deviations.integration.sl.se/v1/messages'

# New SL Journey Planner v2 - no key required
SL_JOURNEY_BASE_URL = 'https://journeyplanner.integration.sl.se/v2/'
STOP_FINDER_URL = SL_JOURNEY_BASE_URL + 'stop-finder'
TRIPS_URL = SL_JOURNEY_BASE_URL + 'trips'

# Vehicle positions - still works?
FORDONSPOSITION_URL = 'https://api.sl.se/fordonspositioner/GetData?' \
                      'type={}&pp=false&cacheControl={}'

# old https://api.sl.se/api2 ceases to function on 2024-03-15
TRAFIKLAB_URL = 'https://journeyplanner.integration.sl.se/v1/'
# Due to technical reasons, this API is being replaced by SLs Deviations API and will completely stop working on 2024-03-31
SI2_URL = SL_DEVIATIONS_URL  # Updated to new deviations API
# Due to technical reasons, this API is being replaced by SLs Deviations API and GTFS Service alerts. It will stop working on 2024-03-31
TL2_URL = SL_DEVIATIONS_URL  # Updated to new deviations API
# This API will be shut down at the end of March 2024. It is replaced by SL’s new transport API.
RI4_URL = DEPARTURES_URL  # Updated to new transport API
PU1_URL = STOP_FINDER_URL  # Updated to new journey planner
RP3_URL = TRIPS_URL  # Updated to new journey planner

USER_AGENT = "hasl-slapi/" + __version__

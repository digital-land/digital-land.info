import hashlib
import json
from functools import wraps
from time import perf_counter

import sentry_sdk


def measure_entity_search(function):
    """Record search duration with a stable group for equivalent parameters."""

    @wraps(function)
    def measured(session, parameters, extension=None):
        # Match the search's omission of empty parameters. Sort only filters
        # whose list order does not affect the results.
        params = {key: value for key, value in parameters.items() if value}
        for key in (
            "typology",
            "dataset",
            "entity",
            "prefix",
            "reference",
            "organisation_entity",
            "geometry_curie",
            "geometry_entity",
            "geometry_reference",
            "period",
        ):
            if isinstance(params.get(key), list):
                params[key] = sorted(set(value for value in params[key] if value))

        canonical = json.dumps(
            {"params": params, "extension": extension},
            sort_keys=True,
            separators=(",", ":"),
            default=str,
        )
        attributes = {
            "search.group": hashlib.sha256(canonical.encode()).hexdigest(),
            "search.geometry_curie": ",".join(params.get("geometry_curie", [])),
            "extension": extension.value if extension is not None else "html",
        }
        started = perf_counter()
        outcome = "error"
        try:
            result = function(session, parameters, extension)
            outcome = "success"
            return result
        finally:
            sentry_sdk.metrics.distribution(
                "entity.search.duration",
                (perf_counter() - started) * 1000,
                unit="millisecond",
                attributes={**attributes, "outcome": outcome},
            )

    return measured

"""Correlated spans and stage logs for both entity search implementations."""

import hashlib
import json
import logging
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps
from time import perf_counter
from uuid import uuid4

import sentry_sdk
from sentry_sdk.integrations.logging import SentryLogsHandler

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(SentryLogsHandler(level=logging.INFO))
_context = ContextVar("entity_search_trace", default=None)


def search_variant():
    return (_context.get() or {}).get("search_variant", "optimized")


def record_search_results(data):
    context = _context.get()
    if context is not None:
        context.update(total_matches=data["count"], returned_rows=len(data["entities"]))


def _record_response(result):
    from fastapi.encoders import jsonable_encoder
    from application.core.utils import DigitalLandJSONResponse

    context = _context.get()
    if isinstance(result, dict):
        # Use the same encoder as the route; measure uncompressed UTF-8 bytes.
        body = DigitalLandJSONResponse(jsonable_encoder(result)).body
        payload = json.loads(body)
        records = payload.get("entities", payload.get("features"))
        if records is not None:
            canonical = json.dumps(
                records, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode("utf-8")
            context.update(
                results_bytes=len(canonical),
                results_sha256=hashlib.sha256(canonical).hexdigest(),
            )
    else:
        body = result.body
    context["response_body_bytes"] = len(body)


@contextmanager
def search_stage(stage):
    context = _context.get() or {}
    started = perf_counter()
    outcome = "error"
    verbose = context.get("verbose", False)
    with sentry_sdk.start_span(op="entity.search", name=stage) as span:
        for key, value in context.items():
            if key != "verbose":
                span.set_data(key, value)
        if verbose:
            logger.info("entity.search.stage.start", extra={**context, "stage": stage})
        try:
            yield
            outcome = "success"
        finally:
            duration = (perf_counter() - started) * 1000
            span.set_data("outcome", outcome)
            for key, value in context.items():
                if key != "verbose":
                    span.set_data(key, value)
            if verbose:
                logger.info(
                    "entity.search.stage.end",
                    extra={
                        **context,
                        "stage": stage,
                        "duration_ms": duration,
                        "outcome": outcome,
                    },
                )


def traced_search_request(function):
    @wraps(function)
    def traced(request, *args, **kwargs):
        context = {
            "search_request_id": uuid4().hex,
            "search_variant": (
                "main"
                if getattr(request.state, "search_variant", None) == "main"
                else "optimized"
            ),
            "search_parameters_hash": hashlib.sha256(
                json.dumps(sorted(request.query_params.multi_items())).encode()
            ).hexdigest(),
            "verbose": True,
        }
        token = _context.set(context)
        try:
            with search_stage("request.total"):
                result = function(request, *args, **kwargs)
                try:
                    with search_stage("response.measure"):
                        _record_response(result)
                except Exception:
                    # Diagnostics must not turn a successful response into an error.
                    logger.warning("Unable to measure search response", exc_info=True)
                return result
        finally:
            _context.reset(token)

    return traced

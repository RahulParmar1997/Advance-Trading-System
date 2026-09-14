import json
import logging

from advance_system.observability.logging import StructuredFormatter, log_event


def test_structured_formatter_emits_json_and_context() -> None:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "order accepted", (), None)
    record.context = {"instrument": "NSE_EQ|INE123", "quantity": 5}

    payload = json.loads(StructuredFormatter().format(record))

    assert payload["level"] == "INFO"
    assert payload["message"] == "order accepted"
    assert payload["context"]["quantity"] == 5


def test_structured_formatter_redacts_sensitive_context() -> None:
    record = logging.LogRecord("test", logging.INFO, __file__, 1, "token refreshed", (), None)
    record.context = {
        "access_token": "do-not-log",
        "nested": {"client_secret": "also-do-not-log"},
    }

    payload = json.loads(StructuredFormatter().format(record))

    assert payload["context"]["access_token"] == "[REDACTED]"
    assert payload["context"]["nested"]["client_secret"] == "[REDACTED]"
    assert "do-not-log" not in json.dumps(payload)


def test_log_event_uses_structured_context(caplog) -> None:
    logger = logging.getLogger("advance_system.test")

    with caplog.at_level(logging.INFO, logger=logger.name):
        log_event(logger, "risk decision", instrument="NSE_EQ|INE123", secret="hidden")

    assert caplog.records
    assert caplog.records[-1].context["instrument"] == "NSE_EQ|INE123"
    assert caplog.records[-1].context["secret"] == "[REDACTED]"

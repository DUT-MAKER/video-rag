from video_crawler.worker import retry_delay, should_retry


def test_transient_error_retries_with_exponential_delay() -> None:
    assert should_retry(RuntimeError("PARSER_BROKEN: no results"), attempt=1, max_attempts=3)
    assert retry_delay(60, attempt=1) == 60
    assert retry_delay(60, attempt=2) == 120
    assert not should_retry(RuntimeError("PARSER_BROKEN"), attempt=3, max_attempts=3)


def test_login_challenge_and_rate_limit_stop_current_slot() -> None:
    for code in ("AUTH_REQUIRED", "CHALLENGE_REQUIRED", "RATE_LIMITED", "ACCESS_DENIED"):
        assert not should_retry(RuntimeError(f"{code}: blocked"), attempt=1, max_attempts=3)

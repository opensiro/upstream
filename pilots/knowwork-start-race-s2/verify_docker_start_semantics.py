#!/usr/bin/env python3
"""Check real docker-py APIClient.start response handling without a Docker daemon.

This test replaces only the HTTP transport response. It executes the installed
docker SDK's actual start() and _raise_for_status() paths; FakeDocker and
product-level APIError injection are deliberately not used.
"""
from __future__ import annotations

import json

import docker
from docker import APIClient
from docker.errors import APIError
from requests import Response


def observe(status: int) -> str:
    """Invoke the actual docker API method with a controlled HTTP status."""
    client = APIClient.__new__(APIClient)
    client._url = lambda *args, **kwargs: "http://localhost/containers/example/start"
    response = Response()
    response.status_code = status
    response.url = "http://localhost/containers/example/start"
    response._content = b"controlled HTTP response"
    client._post = lambda *args, **kwargs: response
    try:
        result = client.start("example")
    except APIError as exc:
        return f"APIError({exc.status_code})"
    if result is not None:
        raise AssertionError(f"Expected None for HTTP {status}, got {result!r}")
    return "NO_EXCEPTION"


def main() -> None:
    observed = {str(code): observe(code) for code in (304, 409, 500)}
    expected = {
        "304": "NO_EXCEPTION",
        "409": "APIError(409)",
        "500": "APIError(500)",
    }
    print(json.dumps(
        {"dependency": "docker", "version": docker.__version__,
         "api": "docker.APIClient.start", "observed": observed},
        indent=2,
    ))
    if observed != expected:
        raise AssertionError(f"SDK behavior changed: {observed!r} != {expected!r}")


if __name__ == "__main__":
    main()

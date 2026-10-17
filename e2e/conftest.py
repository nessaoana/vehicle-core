"""Fixtures for the end-to-end tests against running vehicle-core and vehicle-sales.

As URLs vêm do ambiente:
- E2E_BASE_URL: URL única que roteia os dois serviços (API Gateway ou o
  Traefik do cluster). Padrão: http://localhost:8081.
- E2E_CORE_URL / E2E_SALES_URL: sobrescrevem a URL de cada serviço, para rodar
  contra os containers locais (ex.: core em :8001 e sales em :8000).
"""

import os
import random
import string
import uuid
from collections.abc import Iterator

import httpx2
import pytest


BASE_URL = os.getenv("E2E_BASE_URL", "http://localhost:8081").rstrip("/")


def _client(url: str) -> httpx2.Client:
    return httpx2.Client(
        base_url=url.rstrip("/"),
        timeout=15,
        transport=httpx2.HTTPTransport(retries=3),
    )


@pytest.fixture(scope="session")
def core() -> Iterator[httpx2.Client]:
    with _client(os.getenv("E2E_CORE_URL", BASE_URL)) as client:
        yield client


@pytest.fixture(scope="session")
def sales() -> Iterator[httpx2.Client]:
    with _client(os.getenv("E2E_SALES_URL", BASE_URL)) as client:
        yield client


@pytest.fixture
def brand() -> str:
    """Marca única por teste, para isolar as buscas dos dados de outras execuções."""

    return f"E2E{uuid.uuid4().hex[:8]}"


@pytest.fixture
def new_plate():
    """Gera placas Mercosul (ABC1D23) aleatórias."""

    def generate() -> str:
        letters = random.choices(string.ascii_uppercase, k=4)
        digits = random.choices(string.digits, k=3)
        return f"{''.join(letters[:3])}{digits[0]}{letters[3]}{digits[1]}{digits[2]}"

    return generate

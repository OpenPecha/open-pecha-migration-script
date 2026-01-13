import os
import time
from dotenv import load_dotenv
import requests
from scripts.exceptions import (
    OldPechaBackendError,
    NewPechaBackendError
)

load_dotenv()

OLD_PECHA_API_URL = os.getenv("OLD_PECHA_API_URL")
NEW_PECHA_API_URL = os.getenv("NEW_PECHA_API_URL")


def migrate_person():
    """
    Migration script from old pecha-backend api to new open-pecha backend api
    """
    skip = 0
    limit = 20
    while True:
        data = _fetch_persons_from_old_pecha_backend(skip, limit)
        if len(data) == 0:
            break
        person_created_count = 0
        for person in data:
            _create_person_in_new_pecha_backend(
                person=person,
                skip=skip,
                limit=limit,
                person_created_count=person_created_count,
            )
            time.sleep(5)
            person_created_count += 1
        skip += limit


def _fetch_persons_from_old_pecha_backend(skip: int, limit: int):
    """
    Fetches persons from old pecha-backend api
    """
    try:
        response = requests.get(
            f"{OLD_PECHA_API_URL}/v2/persons?limit={limit}&skip={skip}",
            timeout=30,
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        raise OldPechaBackendError(
            f"Error: {e},\nSkip: {skip},\nLimit: {limit}"
        ) from e


def _create_person_in_new_pecha_backend(
    person: dict,
    skip: int,
    limit: int,
    person_created_count: int
):
    """
    Creates new person at new pecha backend api
    """
    try:
        response = requests.post(
            f"{NEW_PECHA_API_URL}/v2/persons",
            json=person,
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        raise NewPechaBackendError(
            f"Error: {e},\nPerson: {person},\nSkip: {skip},\nLimit: {limit},\nPerson Created Count: {person_created_count}"
        ) from e

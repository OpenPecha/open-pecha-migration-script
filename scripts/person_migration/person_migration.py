import os
import time
from dotenv import load_dotenv
import requests
from scripts.db.session import get_session
from scripts.db.models import PersonMigration
from scripts.exceptions import (
    OldPechaBackendError,
    NewPechaBackendError,
    DatabaseError
)

load_dotenv()

OLD_PECHA_API_URL = os.getenv("OLD_PECHA_API_URL")
NEW_PECHA_API_URL = os.getenv("NEW_PECHA_API_URL")


def migrate_person():
    """
    Migration script from old pecha-backend api to new open-pecha backend api
    """
    skip = 0
    limit = 5
    while True:
        print("Fetching persons from old pecha-backend api")
        data = _fetch_persons_from_old_pecha_backend(skip, limit)
        print(f"Fetched {len(data)} persons from old pecha-backend api")
        if len(data) == 0:
            break
        old_person_ids = [person["id"] for person in data]

        print("Fetching migrated persons from old person ids from database")
        migrated_persons = _fetch_migrated_persons_from_old_person_ids(
            old_person_ids=old_person_ids
        )
        print(f"Fetched {len(migrated_persons)} migrated persons from old person ids from database")
        
        print("Filtering out migrated persons from old person ids")
        data = _filter_migrated_persons(
            data=data,
            migrated_persons=migrated_persons
        )
        print(f"Filtered out {len(data)} persons from old person ids")
        person_created_count = 0
        for person in data:
            print(f"Creating person in new pecha backend api: {person['id']}")
            response = _create_person_in_new_pecha_backend(
                person=person,
                skip=skip,
                limit=limit,
                person_created_count=person_created_count,
            )
            print("Response from new pecha backend api", response)
            _save_migrated_person_to_database(
                old_person_id=person["id"],
                old_person_bdrc_id=person["bdrc"],
                new_person_id=response["id"]
            )
            print(f"Saved migrated person to database: {person['id']}")
            time.sleep(5)
            person_created_count += 1
        skip += limit

        # Remove this break if you're not testing it
        break


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
        person_payload = person.copy()
        if person_payload.get("id", None) is not None:
            person_payload.pop("id")
        response = requests.post(
            f"{NEW_PECHA_API_URL}/v2/persons",
            json=person_payload,
            timeout=30
        )
        return response.json()
    except requests.exceptions.RequestException as e:
        raise NewPechaBackendError(
            f"Error: {e},\nPerson: {person},\nSkip: {skip},\nLimit: {limit},\nPerson Created Count: {person_created_count}"
        ) from e


def _filter_migrated_persons(
    data: list[dict],
    migrated_persons: list[dict]
) -> list[dict]:
    """
    Filters out migrated persons from old person ids
    """
    migrated_person_ids = [
        person["old_person_id"] for person in migrated_persons
    ]
    return [
        person for person in data if person["id"] not in migrated_person_ids
    ]


def _fetch_migrated_persons_from_old_person_ids(
    old_person_ids: list[str]
) -> list[dict]:
    """
    Fetches migrated persons from old person ids from database
    """
    try:
        with get_session() as session:
            rows = session.query(PersonMigration).filter(
                PersonMigration.old_person_id.in_(old_person_ids)
            ).all()
            return [r.to_dict() for r in rows]
    except Exception as e:
        raise DatabaseError(
            f"Error: {e},\nOld Person IDs: {old_person_ids}"
        ) from e


def _save_migrated_person_to_database(
    old_person_id: str,
    old_person_bdrc_id: str,
    new_person_id: str
):
    """
    Saves migrated person to database
    """
    try:
        with get_session() as session:
            session.add(PersonMigration(
                old_person_id=old_person_id,
                old_person_bdrc_id=old_person_bdrc_id,
                new_person_id=new_person_id
            ))
    except Exception as e:
        raise DatabaseError(
            f"Error: {e},\nOld Person ID: {old_person_id},\nOld Person BDRC ID: {old_person_bdrc_id},\nNew Person ID: {new_person_id}"
        ) from e


if __name__ == "__main__":
    print("Starting person migration")
    migrate_person()
    print("Person migration ended")

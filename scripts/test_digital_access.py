
import sys
import os
import json
import urllib.request
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

os.environ.setdefault("FIRESTORE_EMULATOR_HOST", "localhost:4588")
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "floci-local")

BASE_URL = "http://127.0.0.1:8000"

STUDENT_ID = "STU001"
BOOK_ID = "M5utpk6P4Sh1GiK4YIt4"


def api_request(path, method="GET", data=None):
    body = None

    headers = {}

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        headers["Content-Type"] = "application/json"

    request = urllib.request.Request(
        BASE_URL + path,
        data=body,
        headers=headers,
        method=method
    )

    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


print("\n1. Granting permanent digital access...")

grant = api_request(
    "/digital-access/grant",
    "POST",
    {
        "student_id": STUDENT_ID,
        "book_id": BOOK_ID,
        "granted_by": "LIBRARIAN001"
    }
)

print(json.dumps(grant, indent=4))

assert grant["status"] == "active"
assert grant["expires_at"] is None


print("\n2. Checking student's digital books...")

access = api_request(
    f"/digital-access/{STUDENT_ID}"
)

print(json.dumps(access, indent=4))

assert any(
    book["book_id"] == BOOK_ID
    for book in access["digital_books"]
)


print("\n3. Revoking digital access...")

revoke = api_request(
    f"/digital-access/{STUDENT_ID}/{BOOK_ID}/revoke",
    "POST"
)

print(json.dumps(revoke, indent=4))

assert revoke["status"] == "revoked"


print("\n4. Verifying revoked access...")

final_access = api_request(
    f"/digital-access/{STUDENT_ID}"
)

assert not any(
    book["book_id"] == BOOK_ID
    for book in final_access["digital_books"]
)

print("\nSUCCESS: Digital access workflow passed!")

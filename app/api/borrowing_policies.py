
from fastapi import APIRouter, HTTPException
from app.core.firestore import db
from app.models.borrowing_policy import BorrowingPolicyCreate

router = APIRouter(
    prefix="/borrowing-policies",
    tags=["Borrowing Policies"]
)


@router.post("/")
def create_policy(policy: BorrowingPolicyCreate):
    existing = db.collection("borrowing_policies").where(
        "book_category", "==", policy.book_category
    ).where("status", "==", "active").stream()

    if any(True for _ in existing):
        raise HTTPException(
            status_code=409,
            detail="An active policy already exists for this category."
        )

    ref = db.collection("borrowing_policies").document()

    data = policy.model_dump()
    data["policy_id"] = ref.id

    ref.set(data)

    return {
        "message": "Borrowing policy created successfully.",
        **data
    }


@router.get("/")
def list_policies():
    records = db.collection("borrowing_policies").stream()

    result = []

    for record in records:
        data = record.to_dict()
        data["policy_id"] = record.id
        result.append(data)

    return {"total": len(result), "policies": result}


@router.put("/{policy_id}")
def update_policy(policy_id: str, policy: BorrowingPolicyCreate):
    ref = db.collection("borrowing_policies").document(policy_id)

    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Policy not found.")

    data = policy.model_dump()
    data["policy_id"] = policy_id

    ref.set(data)

    return {
        "message": "Borrowing policy updated successfully.",
        **data
    }


@router.post("/{policy_id}/deactivate")
def deactivate_policy(policy_id: str):
    ref = db.collection("borrowing_policies").document(policy_id)

    if not ref.get().exists:
        raise HTTPException(status_code=404, detail="Policy not found.")

    ref.update({"status": "inactive"})

    return {
        "message": "Borrowing policy deactivated successfully.",
        "policy_id": policy_id
    }

from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.core.firestore import db


router = APIRouter(
    prefix="/fines",
    tags=["Fine Management"]
)


class FinePaymentRequest(BaseModel):
    payment_method: str = "cash"
    received_by: str = "LIBRARIAN001"


class FineWaiverRequest(BaseModel):
    waived_by: str = "LIBRARIAN001"
    reason: str = "Approved by librarian"


@router.post("/{fine_id}/pay")
def pay_fine(fine_id: str, request: FinePaymentRequest):

    fine_ref = db.collection("fines").document(fine_id)
    fine = fine_ref.get()

    if not fine.exists:
        raise HTTPException(
            status_code=404,
            detail="Fine record not found."
        )

    data = fine.to_dict()

    if data.get("payment_status") != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending fines can be paid."
        )

    paid_at = datetime.now(timezone.utc)

    fine_ref.update({
        "payment_status": "paid",
        "paid_at": paid_at,
        "payment_method": request.payment_method,
        "received_by": request.received_by
    })

    return {
        "message": "Fine payment recorded successfully.",
        "fine_id": fine_id,
        "amount_paise": data.get("fine_amount_paise", 0),
        "amount_rupees": data.get("fine_amount_paise", 0) / 100,
        "payment_status": "paid",
        "paid_at": paid_at,
        "payment_method": request.payment_method
    }


@router.post("/{fine_id}/waive")
def waive_fine(fine_id: str, request: FineWaiverRequest):

    fine_ref = db.collection("fines").document(fine_id)
    fine = fine_ref.get()

    if not fine.exists:
        raise HTTPException(
            status_code=404,
            detail="Fine record not found."
        )

    data = fine.to_dict()

    if data.get("payment_status") != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending fines can be waived."
        )

    waived_at = datetime.now(timezone.utc)

    fine_ref.update({
        "payment_status": "waived",
        "waived_at": waived_at,
        "waived_by": request.waived_by,
        "waiver_reason": request.reason
    })

    return {
        "message": "Fine waived successfully.",
        "fine_id": fine_id,
        "payment_status": "waived",
        "waived_at": waived_at,
        "reason": request.reason
    }


from fastapi import FastAPI

from app.api.borrowing_policies import router as borrowing_policy_router
from app.api.fines import router as fines_router
from app.api.books import router as book_router
from app.api.students import router as student_router
from app.api.borrowings import router as borrowing_router
from app.api.digital_access import router as digital_access_router
from app.api.digital_books import router as digital_books_router
from app.api.auth import router as auth_router


app = FastAPI(
    title="Library360 API",
    description="Backend API for the Library360 Library Management System",
    version="1.0.0"
)


# Register API routers
app.include_router(auth_router)
app.include_router(student_router)
app.include_router(book_router)
app.include_router(borrowing_router)
app.include_router(digital_access_router)
app.include_router(digital_books_router)
app.include_router(fines_router)
app.include_router(borrowing_policy_router)


@app.get("/")
def home():
    return {
        "message": "Welcome to Library360!",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "application": "Library360",
        "status": "healthy"
    }

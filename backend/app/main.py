from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .database import engine, Base
from .routers import job_type, wage, expense, report, expense_category, investment, cycle, grape_grade, income, grape_bunch, auth, admin

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Finance System API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(cycle.router, prefix="/api", tags=["cycles"])
app.include_router(job_type.router, prefix="/api", tags=["job-types"])
app.include_router(wage.router, prefix="/api", tags=["wages"])
app.include_router(expense.router, prefix="/api", tags=["expenses"])
app.include_router(expense_category.router, prefix="/api", tags=["expense-categories"])
app.include_router(investment.router, prefix="/api", tags=["investments"])
app.include_router(grape_grade.router, prefix="/api", tags=["grape-grades"])
app.include_router(income.router, prefix="/api", tags=["incomes"])
app.include_router(report.router, prefix="/api", tags=["reports"])
app.include_router(grape_bunch.router, prefix="/api", tags=["grape-bunches"])


@app.get("/")
def root():
    return {"message": "Finance System API", "version": "1.0.0"}

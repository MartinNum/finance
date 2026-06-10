from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional


# ---- Auth Schemas ----

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user: dict


class UserInfo(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    park_id: Optional[int] = None
    park_name: Optional[str] = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str


class PasswordReset(BaseModel):
    new_password: str


# ---- Park Schemas ----

class ParkCreate(BaseModel):
    name: str


class ParkUpdate(BaseModel):
    name: Optional[str] = None
    is_active: Optional[bool] = None


class ParkResponse(BaseModel):
    id: int
    name: str
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- User Management Schemas ----

class UserCreate(BaseModel):
    username: str
    password: str
    display_name: str
    role: str = "user"
    park_id: Optional[int] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    is_active: Optional[bool] = None
    park_id: Optional[int] = None


class UserResponse(BaseModel):
    id: int
    username: str
    display_name: str
    role: str
    park_id: Optional[int] = None
    is_active: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- Cycle Schemas ----

class CycleBase(BaseModel):
    name: str
    start_date: date
    end_date: date


class CycleCreate(CycleBase):
    pass


class CycleUpdate(BaseModel):
    name: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None


class CycleResponse(CycleBase):
    id: int
    is_current: bool

    class Config:
        from_attributes = True


# ---- Job Type Schemas ----

class JobTypeBase(BaseModel):
    name: str
    billing_type: str
    default_price: float = 0
    is_active: bool = True


class JobTypeCreate(JobTypeBase):
    pass


class JobTypeUpdate(BaseModel):
    name: Optional[str] = None
    billing_type: Optional[str] = None
    default_price: Optional[float] = None
    is_active: Optional[bool] = None


class JobTypeResponse(JobTypeBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- Wage Schemas ----

class WageBase(BaseModel):
    cycle_id: int
    job_type_id: int
    unit_price: float
    headcount: int
    days: float
    expense_date: date
    remark: Optional[str] = None


class WageCreate(WageBase):
    pass


class WageUpdate(BaseModel):
    job_type_id: Optional[int] = None
    unit_price: Optional[float] = None
    headcount: Optional[int] = None
    days: Optional[float] = None
    expense_date: Optional[date] = None
    remark: Optional[str] = None


class WageResponse(WageBase):
    id: int
    amount: float
    job_type: JobTypeResponse

    class Config:
        from_attributes = True


# ---- Expense Schemas ----

class ExpenseBase(BaseModel):
    cycle_id: int
    category: str
    sub_category: str
    amount: float
    expense_date: date
    remark: Optional[str] = None


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    category: Optional[str] = None
    sub_category: Optional[str] = None
    amount: Optional[float] = None
    expense_date: Optional[date] = None
    remark: Optional[str] = None


class ExpenseResponse(ExpenseBase):
    id: int

    class Config:
        from_attributes = True


# ---- Report Schemas ----

class CategorySummary(BaseModel):
    name: str
    amount: float
    ratio: float


class ReportSummary(BaseModel):
    total: float
    period: dict
    categories: list[CategorySummary]


# ---- Expense Category Schemas ----

class ExpenseCategoryBase(BaseModel):
    category: str
    sub_category: str
    is_active: bool = True
    sort_order: int = 0


class ExpenseCategoryCreate(BaseModel):
    category: str
    sub_category: str
    sort_order: int = 0


class ExpenseCategoryResponse(ExpenseCategoryBase):
    id: int

    class Config:
        from_attributes = True


# ---- Investment Schemas ----

class InvestmentBase(BaseModel):
    cycle_id: int
    investor_name: str
    amount: float
    invest_date: date
    remark: Optional[str] = None


class InvestmentCreate(InvestmentBase):
    pass


class InvestmentResponse(InvestmentBase):
    id: int

    class Config:
        from_attributes = True


class BalanceSummary(BaseModel):
    total_investment: float
    total_expense: float
    balance: float


# ---- Grape Bunch Config Schemas ----

class GrapeBunchConfigUpdate(BaseModel):
    bunch_count: int = 0
    bunch_weight: float = 0
    total_weight: float = 0
    calc_mode: str = "by_weight"


class GrapeBunchConfigResponse(BaseModel):
    id: int
    cycle_id: int
    bunch_count: int
    bunch_weight: float
    total_weight: float
    calc_mode: str
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- Grape Grade Schemas ----

class GrapeGradeBase(BaseModel):
    name: str
    default_price: float = 0
    is_active: bool = True


class GrapeGradeCreate(GrapeGradeBase):
    pass


class GrapeGradeUpdate(BaseModel):
    name: Optional[str] = None
    default_price: Optional[float] = None
    is_active: Optional[bool] = None


class GrapeGradeResponse(GrapeGradeBase):
    id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ---- Income Schemas ----

class IncomeBase(BaseModel):
    cycle_id: int
    grade_id: int
    quantity_kg: float
    unit_price: float
    income_date: date
    remark: Optional[str] = None


class IncomeCreate(IncomeBase):
    pass


class IncomeResponse(IncomeBase):
    id: int
    amount: float
    grade: GrapeGradeResponse

    class Config:
        from_attributes = True


# ---- Dividend Schemas ----

class DividendResponse(BaseModel):
    id: int
    income_id: int
    cycle_id: int
    investor_name: str
    amount: float
    ratio: float
    income_date: date

    class Config:
        from_attributes = True


class InvestorDividendSummary(BaseModel):
    investor_name: str
    total_investment: float
    total_dividend: float
    ratio: float
    pending: float

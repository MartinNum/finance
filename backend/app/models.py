from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from .database import Base


class Park(Base):
    __tablename__ = "parks"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    users = relationship("User", back_populates="park")
    cycles = relationship("Cycle", back_populates="park")
    job_types = relationship("JobType", back_populates="park")
    expense_categories = relationship("ExpenseCategory", back_populates="park")
    grape_grades = relationship("GrapeGrade", back_populates="park")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    display_name = Column(String, nullable=False)
    role = Column(String, nullable=False, default="user")
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())

    park = relationship("Park", back_populates="users")


class GrapeGrade(Base):
    __tablename__ = "grape_grades"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    default_price = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=False)

    park = relationship("Park", back_populates="grape_grades")
    incomes = relationship("Income", back_populates="grade")

    __table_args__ = (
        UniqueConstraint("name", "park_id", name="uq_grape_grade_name_park"),
    )


class Cycle(Base):
    __tablename__ = "cycles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    is_current = Column(Boolean, default=False)
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=False)

    park = relationship("Park", back_populates="cycles")
    wages = relationship("Wage", back_populates="cycle")
    expenses = relationship("Expense", back_populates="cycle")
    investments = relationship("Investment", back_populates="cycle")

    __table_args__ = (
        UniqueConstraint("name", "park_id", name="uq_cycle_name_park"),
    )


class JobType(Base):
    __tablename__ = "job_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    billing_type = Column(String, nullable=False)
    default_price = Column(Float, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=False)

    park = relationship("Park", back_populates="job_types")
    wages = relationship("Wage", back_populates="job_type")

    __table_args__ = (
        UniqueConstraint("name", "park_id", name="uq_job_type_name_park"),
    )


class Wage(Base):
    __tablename__ = "wages"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("cycles.id"), nullable=False)
    job_type_id = Column(Integer, ForeignKey("job_types.id"), nullable=False)
    unit_price = Column(Float, nullable=False)
    headcount = Column(Integer, nullable=False)
    days = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, nullable=False)
    remark = Column(String, nullable=True)

    cycle = relationship("Cycle", back_populates="wages")
    job_type = relationship("JobType", back_populates="wages")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("cycles.id"), nullable=False)
    category = Column(String, nullable=False)
    sub_category = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    expense_date = Column(Date, nullable=False)
    remark = Column(String, nullable=True)

    cycle = relationship("Cycle", back_populates="expenses")


class ExpenseCategory(Base):
    __tablename__ = "expense_categories"

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String, nullable=False)
    sub_category = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    sort_order = Column(Integer, default=0)
    park_id = Column(Integer, ForeignKey("parks.id"), nullable=False)

    park = relationship("Park", back_populates="expense_categories")

    __table_args__ = (
        UniqueConstraint("category", "sub_category", "park_id", name="uq_expense_cat_park"),
    )


class GrapeBunchConfig(Base):
    __tablename__ = "grape_bunch_config"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("cycles.id"), nullable=False, unique=True)
    bunch_count = Column(Integer, nullable=False, default=0)
    bunch_weight = Column(Float, nullable=False, default=0)
    total_weight = Column(Float, nullable=False, default=0)
    calc_mode = Column(String, nullable=False, default="by_weight")
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    cycle = relationship("Cycle")


class Investment(Base):
    __tablename__ = "investments"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("cycles.id"), nullable=False)
    investor_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    invest_date = Column(Date, nullable=False)
    remark = Column(String, nullable=True)

    cycle = relationship("Cycle", back_populates="investments")


class Income(Base):
    __tablename__ = "incomes"

    id = Column(Integer, primary_key=True, index=True)
    cycle_id = Column(Integer, ForeignKey("cycles.id"), nullable=False)
    grade_id = Column(Integer, ForeignKey("grape_grades.id"), nullable=False)
    quantity_kg = Column(Float, nullable=False)
    unit_price = Column(Float, nullable=False)
    amount = Column(Float, nullable=False)
    income_date = Column(Date, nullable=False)
    remark = Column(String, nullable=True)

    cycle = relationship("Cycle")
    grade = relationship("GrapeGrade", back_populates="incomes")
    dividends = relationship("Dividend", back_populates="income", cascade="all, delete-orphan")


class Dividend(Base):
    __tablename__ = "dividends"

    id = Column(Integer, primary_key=True, index=True)
    income_id = Column(Integer, ForeignKey("incomes.id"), nullable=False)
    cycle_id = Column(Integer, ForeignKey("cycles.id"), nullable=False)
    investor_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    ratio = Column(Float, nullable=False)
    income_date = Column(Date, nullable=False)

    income = relationship("Income", back_populates="dividends")
    cycle = relationship("Cycle")

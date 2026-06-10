from datetime import date

from sqlalchemy.orm import Session

from ..models import Cycle, JobType, ExpenseCategory, GrapeGrade


def create_park_seed_data(db: Session, park_id: int):
    current_year = date.today().year

    db.add(Cycle(
        name=f"{current_year}年周期",
        start_date=date(current_year, 1, 1),
        end_date=date(current_year, 12, 31),
        is_current=True,
        park_id=park_id,
    ))

    for name, billing_type, price in [
        ("梳果工", "daily", 150),
        ("管理工", "daily", 200),
        ("长工", "monthly", 5000),
        ("绑枝工", "daily", 120),
        ("杂工", "daily", 100),
    ]:
        db.add(JobType(name=name, billing_type=billing_type, default_price=price, park_id=park_id))

    for i, (cat, sub) in enumerate([
        ("物料", "化肥"),
        ("电费", "电费"),
        ("交通", "油费"),
        ("交通", "路费"),
        ("租金", "场地租金"),
        ("其他", "伙食"),
    ]):
        db.add(ExpenseCategory(category=cat, sub_category=sub, sort_order=i, park_id=park_id))

    for name, price in [("特级", 30), ("一级", 20), ("二级", 12), ("次果", 5)]:
        db.add(GrapeGrade(name=name, default_price=price, park_id=park_id))

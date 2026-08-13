from datetime import datetime
from sqlalchemy import BigInteger, String, DateTime, ForeignKey, Integer, Float, Text, Boolean
from sqlalchemy.orm import Mapped, mapped_column
from database.engine import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    full_name: Mapped[str] = mapped_column(String(255), default="")
    coins: Mapped[int] = mapped_column(BigInteger, default=0)
    referrer_id: Mapped[int | None] = mapped_column(BigInteger, ForeignKey("users.id"), nullable=True)
    referred_count: Mapped[int] = mapped_column(Integer, default=0)
    last_daily_bonus: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(BigInteger)  # musbat yoki manfiy bo'lishi mumkin
    description: Mapped[str] = mapped_column(String(255), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Service(Base):
    __tablename__ = "services"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    service_code: Mapped[str] = mapped_column(String(100), unique=True)  # SMM paneldagi xizmat kodi
    name: Mapped[str] = mapped_column(String(255))
    category: Mapped[str] = mapped_column(String(100), default="Umumiy")
    price_per_1000: Mapped[float] = mapped_column(Float)  # 1000 dona uchun panel narxi (Coin/so'm)
    min_quantity: Mapped[int] = mapped_column(Integer, default=10)
    max_quantity: Mapped[int] = mapped_column(Integer, default=1000000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    service_id: Mapped[int] = mapped_column(Integer, ForeignKey("services.id"))
    link: Mapped[str] = mapped_column(Text)
    quantity: Mapped[int] = mapped_column(Integer)
    price: Mapped[int] = mapped_column(BigInteger)  # Coin
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/processing/error/completed
    api_order_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class WithdrawalRequest(Base):
    __tablename__ = "withdrawal_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    amount: Mapped[int] = mapped_column(BigInteger)
    status: Mapped[str] = mapped_column(String(50), default="pending")  # pending/approved/rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Setting(Base):
    __tablename__ = "settings"

    key: Mapped[str] = mapped_column(String(100), primary_key=True)
    value: Mapped[str] = mapped_column(Text, default="")
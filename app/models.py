from datetime import datetime
from sqlalchemy import String, Integer, DateTime, ForeignKey, Text, Boolean, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base
class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(primary_key=True)
    name:Mapped[str]=mapped_column(String(120))
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    role:Mapped[str]=mapped_column(String(20),default="patient")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Doctor(Base):
    __tablename__="doctors"
    id:Mapped[int]=mapped_column(primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id"),unique=True)
    specialty:Mapped[str]=mapped_column(String(120),index=True)
    city:Mapped[str]=mapped_column(String(120),index=True)
    is_active:Mapped[bool]=mapped_column(Boolean,default=True)
class AvailabilitySlot(Base):
    __tablename__="availability_slots"
    __table_args__=(UniqueConstraint("doctor_id","start_at",name="uq_doctor_start"),)
    id:Mapped[int]=mapped_column(primary_key=True)
    doctor_id:Mapped[int]=mapped_column(ForeignKey("doctors.id"),index=True)
    start_at:Mapped[datetime]=mapped_column(DateTime,index=True)
    end_at:Mapped[datetime]=mapped_column(DateTime)
    is_booked:Mapped[bool]=mapped_column(Boolean,default=False)
class Consultation(Base):
    __tablename__="consultations"
    id:Mapped[int]=mapped_column(primary_key=True)
    patient_id:Mapped[int]=mapped_column(ForeignKey("users.id"),index=True)
    doctor_id:Mapped[int]=mapped_column(ForeignKey("doctors.id"),index=True)
    slot_id:Mapped[int]=mapped_column(ForeignKey("availability_slots.id"),unique=True)
    status:Mapped[str]=mapped_column(String(30),default="booked",index=True)
    idempotency_key:Mapped[str]=mapped_column(String(120),unique=True)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Prescription(Base):
    __tablename__="prescriptions"
    id:Mapped[int]=mapped_column(primary_key=True)
    consultation_id:Mapped[int]=mapped_column(ForeignKey("consultations.id"),index=True)
    doctor_id:Mapped[int]=mapped_column(ForeignKey("doctors.id"))
    details:Mapped[str]=mapped_column(Text)
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow)
class Payment(Base):
    __tablename__="payments"
    id:Mapped[int]=mapped_column(primary_key=True)
    consultation_id:Mapped[int]=mapped_column(ForeignKey("consultations.id"),index=True)
    amount_paise:Mapped[int]=mapped_column(Integer)
    currency:Mapped[str]=mapped_column(String(3),default="INR")
    status:Mapped[str]=mapped_column(String(20),default="pending")
class AuditLog(Base):
    __tablename__="audit_logs"
    id:Mapped[int]=mapped_column(primary_key=True)
    actor_user_id:Mapped[int|None]=mapped_column(ForeignKey("users.id"),nullable=True)
    action:Mapped[str]=mapped_column(String(100),index=True)
    resource_type:Mapped[str]=mapped_column(String(80))
    resource_id:Mapped[str]=mapped_column(String(80))
    details:Mapped[str]=mapped_column(Text,default="")
    created_at:Mapped[datetime]=mapped_column(DateTime,default=datetime.utcnow,index=True)

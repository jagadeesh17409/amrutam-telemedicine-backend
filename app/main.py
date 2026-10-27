import logging,time,datetime
from fastapi import FastAPI,Depends,HTTPException,Header,Request
from pydantic import BaseModel,EmailStr,Field
from sqlalchemy.orm import Session
from sqlalchemy import text,func
from .database import Base,engine,get_db
from .models import User,Doctor,AvailabilitySlot,Consultation,Prescription,AuditLog
logging.basicConfig(level=logging.INFO); log=logging.getLogger("amrutam")
app=FastAPI(title="Amrutam Telemedicine Backend",version="0.1.0")
Base.metadata.create_all(bind=engine)
class UserIn(BaseModel):
    name:str=Field(min_length=1,max_length=120); email:EmailStr; role:str="patient"
class SlotIn(BaseModel):
    start_at:datetime.datetime; end_at:datetime.datetime
class BookingIn(BaseModel):
    patient_id:int; doctor_id:int; slot_id:int
class StatusIn(BaseModel): status:str
class PrescriptionIn(BaseModel):
    doctor_id:int; details:str=Field(min_length=1,max_length=10000)
def audit(db,action,kind,rid,actor=None,details=""):
    db.add(AuditLog(actor_user_id=actor,action=action,resource_type=kind,resource_id=str(rid),details=details)); db.commit()
@app.middleware("http")
async def reqlog(request:Request,call_next):
    start=time.perf_counter(); response=await call_next(request); ms=round((time.perf_counter()-start)*1000,2)
    log.info("method=%s path=%s status=%s duration_ms=%s",request.method,request.url.path,response.status_code,ms)
    response.headers["X-Response-Time-ms"]=str(ms); return response
@app.get("/health")
def health(): return {"status":"ok"}
@app.get("/ready")
def ready(db:Session=Depends(get_db)):
    try: db.execute(text("SELECT 1")); return {"status":"ready","database":"connected"}
    except Exception: raise HTTPException(503,"Database unavailable")
@app.post("/users",status_code=201)
def create_user(p:UserIn,db:Session=Depends(get_db)):
    if p.role not in {"patient","doctor","admin"}: raise HTTPException(400,"Invalid role")
    u=User(name=p.name,email=p.email,role=p.role); db.add(u)
    try: db.commit(); db.refresh(u)
    except Exception: db.rollback(); raise HTTPException(409,"Email already exists or data conflict")
    if u.role=="doctor":
        db.add(Doctor(user_id=u.id,specialty="General Medicine",city="Hyderabad")); db.commit()
    audit(db,"user.created","user",u.id,u.id,"PII omitted")
    return {"id":u.id,"name":u.name,"email":u.email,"role":u.role}
@app.get("/doctors")
def doctors(specialty:str|None=None,city:str|None=None,db:Session=Depends(get_db)):
    q=db.query(Doctor).filter(Doctor.is_active.is_(True))
    if specialty:q=q.filter(Doctor.specialty.ilike(f"%{specialty}%"))
    if city:q=q.filter(Doctor.city.ilike(f"%{city}%"))
    return [{"id":d.id,"user_id":d.user_id,"specialty":d.specialty,"city":d.city} for d in q.limit(100).all()]
@app.post("/doctors/{doctor_id}/availability",status_code=201)
def add_slot(doctor_id:int,p:SlotIn,db:Session=Depends(get_db)):
    if p.end_at<=p.start_at: raise HTTPException(400,"end_at must be after start_at")
    if not db.get(Doctor,doctor_id): raise HTTPException(404,"Doctor not found")
    s=AvailabilitySlot(doctor_id=doctor_id,start_at=p.start_at,end_at=p.end_at); db.add(s)
    try: db.commit(); db.refresh(s)
    except Exception: db.rollback(); raise HTTPException(409,"Conflicting slot")
    audit(db,"availability.created","slot",s.id,details="slot created")
    return {"id":s.id,"doctor_id":s.doctor_id,"start_at":s.start_at,"end_at":s.end_at,"is_booked":s.is_booked}
@app.post("/bookings",status_code=201)
def book(p:BookingIn,idempotency_key:str=Header(alias="Idempotency-Key"),db:Session=Depends(get_db)):
    if not idempotency_key.strip() or len(idempotency_key)>120: raise HTTPException(400,"Invalid Idempotency-Key")
    old=db.query(Consultation).filter_by(idempotency_key=idempotency_key).first()
    if old:return {"id":old.id,"patient_id":old.patient_id,"doctor_id":old.doctor_id,"slot_id":old.slot_id,"status":old.status}
    patient=db.get(User,p.patient_id); doctor=db.get(Doctor,p.doctor_id)
    q=db.query(AvailabilitySlot).filter_by(id=p.slot_id,doctor_id=p.doctor_id)
    if engine.dialect.name=="postgresql":q=q.with_for_update()
    slot=q.first()
    if not patient or patient.role!="patient":raise HTTPException(404,"Patient not found")
    if not doctor or not doctor.is_active:raise HTTPException(404,"Active doctor not found")
    if not slot:raise HTTPException(404,"Slot not found")
    if slot.is_booked:raise HTTPException(409,"Slot already booked")
    slot.is_booked=True; c=Consultation(patient_id=p.patient_id,doctor_id=p.doctor_id,slot_id=p.slot_id,idempotency_key=idempotency_key)
    db.add(c); db.flush()
    db.add(AuditLog(actor_user_id=p.patient_id,action="booking.created",resource_type="consultation",resource_id=str(c.id),details="PII omitted"))
    try:db.commit();db.refresh(c)
    except Exception:db.rollback();raise HTTPException(409,"Booking conflict; retry with same key")
    return {"id":c.id,"patient_id":c.patient_id,"doctor_id":c.doctor_id,"slot_id":c.slot_id,"status":c.status,"created_at":c.created_at}
@app.get("/bookings/{booking_id}")
def get_booking(booking_id:int,db:Session=Depends(get_db)):
    c=db.get(Consultation,booking_id)
    if not c:raise HTTPException(404,"Booking not found")
    return {"id":c.id,"patient_id":c.patient_id,"doctor_id":c.doctor_id,"slot_id":c.slot_id,"status":c.status,"created_at":c.created_at}
@app.patch("/consultations/{consultation_id}/status")
def update_status(consultation_id:int,p:StatusIn,x_user_id:int=Header(alias="X-User-Id"),db:Session=Depends(get_db)):
    if p.status not in {"booked","confirmed","in_progress","completed","cancelled"}:raise HTTPException(400,"Invalid status")
    actor=db.get(User,x_user_id); c=db.get(Consultation,consultation_id)
    if not actor or not c:raise HTTPException(404,"User or consultation not found")
    if actor.role not in {"doctor","admin"}:raise HTTPException(403,"Doctor/admin role required")
    c.status=p.status;db.commit();audit(db,"consultation.status","consultation",c.id,actor.id,p.status)
    return {"id":c.id,"status":c.status}
@app.post("/consultations/{consultation_id}/prescriptions",status_code=201)
def create_prescription(consultation_id:int,p:PrescriptionIn,x_user_id:int=Header(alias="X-User-Id"),db:Session=Depends(get_db)):
    actor=db.get(User,x_user_id); c=db.get(Consultation,consultation_id)
    if not actor or actor.role not in {"doctor","admin"}:raise HTTPException(403,"Doctor/admin role required")
    if not c:raise HTTPException(404,"Consultation not found")
    d=db.query(Doctor).filter_by(id=p.doctor_id,user_id=actor.id).first()
    if actor.role!="admin" and not d:raise HTTPException(403,"Doctor profile ownership required")
    if c.status not in {"in_progress","completed"}:raise HTTPException(409,"Consultation must be in progress or completed")
    x=Prescription(consultation_id=c.id,doctor_id=p.doctor_id,details=p.details);db.add(x);db.commit();db.refresh(x)
    audit(db,"prescription.created","prescription",x.id,actor.id,"details omitted")
    return {"id":x.id,"consultation_id":x.consultation_id,"doctor_id":x.doctor_id,"created_at":x.created_at}
@app.get("/admin/analytics")
def analytics(x_user_id:int=Header(alias="X-User-Id"),db:Session=Depends(get_db)):
    actor=db.get(User,x_user_id)
    if not actor or actor.role!="admin":raise HTTPException(403,"Admin role required")
    return {"users":db.query(func.count(User.id)).scalar(),"doctors":db.query(func.count(Doctor.id)).scalar(),"consultations":db.query(func.count(Consultation.id)).scalar(),"completed":db.query(func.count(Consultation.id)).filter(Consultation.status=="completed").scalar()}

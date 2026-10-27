import os
os.environ["DATABASE_URL"]="sqlite:///./test.db"
from fastapi.testclient import TestClient
from app.database import Base,engine
from app.main import app
Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)
client=TestClient(app)
def test_health():
    assert client.get("/health").json()=={"status":"ok"}
    assert client.get("/ready").status_code==200
def test_booking_idempotency():
    p=client.post("/users",json={"name":"Patient","email":"patient@example.com","role":"patient"}).json()
    duser=client.post("/users",json={"name":"Doctor","email":"doctor@example.com","role":"doctor"}).json()
    d=[x for x in client.get("/doctors").json() if x["user_id"]==duser["id"]][0]
    s=client.post(f"/doctors/{d['id']}/availability",json={"start_at":"2030-01-01T10:00:00","end_at":"2030-01-01T10:30:00"})
    assert s.status_code==201
    data={"patient_id":p["id"],"doctor_id":d["id"],"slot_id":s.json()["id"]}
    h={"Idempotency-Key":"test-booking-001"}
    a=client.post("/bookings",json=data,headers=h); b=client.post("/bookings",json=data,headers=h)
    assert a.status_code==201 and b.status_code==201 and a.json()["id"]==b.json()["id"]
def test_invalid_slot():
    du=client.post("/users",json={"name":"Doc2","email":"doc2@example.com","role":"doctor"}).json()
    d=[x for x in client.get("/doctors").json() if x["user_id"]==du["id"]][0]
    r=client.post(f"/doctors/{d['id']}/availability",json={"start_at":"2030-01-01T10:30:00","end_at":"2030-01-01T10:00:00"})
    assert r.status_code==400

# API examples
Use http://localhost:8000/docs.

1. POST /users: `{"name":"Patient","email":"patient@example.com","role":"patient"}`
2. POST /users: `{"name":"Doctor","email":"doctor@example.com","role":"doctor"}` (demo doctor profile is created).
3. GET /doctors to find doctor ID.
4. POST /doctors/{id}/availability: `{"start_at":"2030-01-01T10:00:00","end_at":"2030-01-01T10:30:00"}`
5. POST /bookings with header `Idempotency-Key: booking-demo-1` and JSON `{"patient_id":1,"doctor_id":1,"slot_id":1}`.
6. PATCH /consultations/1/status with header `X-User-Id: 2`, JSON `{"status":"in_progress"}`.
7. POST /consultations/1/prescriptions with header `X-User-Id: 2`, JSON `{"doctor_id":1,"details":"Demo only"}`.
8. GET /admin/analytics with `X-User-Id` set to an admin user's ID.

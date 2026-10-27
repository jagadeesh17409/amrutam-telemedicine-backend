# Amrutam Telemedicine Backend

## 1. Project Overview

This project is a REST API backend for a telemedicine application. It was developed as part of a Backend Developer assignment for Amrutam Pharmaceuticals.

The main purpose of this project is to manage patients, doctors, doctor availability, appointment bookings, consultation status, prescriptions, and basic administrative analytics.

I built this project to learn and demonstrate how a backend application works using Python, FastAPI, SQLAlchemy, and PostgreSQL.

## 2. Technologies Used

- **Programming Language:** Python
- **Backend Framework:** FastAPI
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **API Documentation:** Swagger UI / OpenAPI
- **Containerization:** Docker and Docker Compose
- **Testing:** Pytest
- **Continuous Integration:** GitHub Actions
- **Version Control:** Git and GitHub

## 3. Main Features

### User Management

- Create users with patient, doctor, or admin roles.
- Validate email addresses and prevent duplicate email addresses.

### Doctor Management

- View active doctors.
- Filter doctors by specialty and city.
- Add doctor availability slots.

### Appointment Booking

- Create an appointment using a patient's ID, doctor's ID, and availability slot ID.
- Prevent booking an already-booked slot.
- Use an idempotency key to help prevent duplicate bookings when a request is retried.

### Consultation Management

- Retrieve booking details.
- Update consultation status.
- Support booked, confirmed, in-progress, completed, and cancelled statuses.

### Prescriptions

- Create a prescription for an eligible consultation.
- Validate the requesting user's role and doctor profile ownership.

### Admin Analytics

- View basic counts of users, doctors, consultations, and completed consultations.

### Logging and Health Checks

- Record basic request method, path, status code, and response time.
- Provide health and database readiness endpoints.
- Record basic audit events for selected operations.

## 4. Project Structure

```text
amrutam_backend_assignment/
├── app/
│   ├── __init__.py
│   ├── database.py
│   ├── main.py
│   └── models.py
├── docs/
│   ├── api-examples.md
│   ├── architecture.md
│   ├── booking-flow.mmd
│   ├── er-diagram.mmd
│   └── security-threat-model.md
├── tests/
│   └── test_api.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── .env
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 5. Prerequisites

Install the following software before running the project:

- Python 3.11 or newer
- Docker Desktop
- Git
- Visual Studio Code (recommended)

For the Docker setup, PostgreSQL runs in a container, so a separate local PostgreSQL installation is not required.

## 6. How to Run the Project

### Step 1: Open the project folder

Extract the project ZIP file and open the folder containing `docker-compose.yml` in Visual Studio Code.

Open the VS Code terminal using **Terminal → New Terminal**.

### Step 2: Configure environment variables

The `.env` file contains the database connection string used by the application.

For the current local Docker configuration, it should match the database username and password in `docker-compose.yml`.

Example:

```dotenv
DATABASE_URL=postgresql+psycopg://postgres:postgres@db:5432/amrutam
```

These are local demonstration credentials only. They must not be used for a public production deployment.

### Step 3: Validate the Docker configuration

Run:

```bash
docker compose config
```

If the configuration is valid, Docker displays the resolved service configuration.

### Step 4: Build and start the application

Run:

```bash
docker compose up --build
```

Docker builds the API image, starts PostgreSQL, waits for the database health check, and starts the API service.

Keep the terminal running while testing the application.

### Step 5: Open the API documentation

Open the following URL in your browser:

**Swagger UI:** http://localhost:8001/docs

Other useful endpoints:

- Health check: http://localhost:8001/health
- Database readiness: http://localhost:8001/ready
- OpenAPI schema: http://localhost:8001/openapi.json

The port `8001` is the host port in my current Docker configuration. If the port mapping changes, update these URLs accordingly.

### Step 6: Stop the application

Press `Ctrl + C` in the terminal running Docker Compose.

Then run:

```bash
docker compose down
```

This stops and removes the containers while normally preserving the database volume.

To delete the project's local database volume as well, use `docker compose down -v` only when you are certain that you do not need its data.

## 7. How to Test the API

Open Swagger UI at http://localhost:8001/docs.

For each endpoint, expand the operation, click **Try it out**, enter the required values, and click **Execute**.

Recommended testing order:

1. `GET /health` — verify that the API responds.
2. `GET /ready` — verify that the database is connected.
3. `POST /users` — create a test patient.
4. `POST /users` — create a test doctor.
5. `GET /doctors` — find the doctor's ID.
6. `POST /doctors/{doctor_id}/availability` — add an available time slot.
7. `POST /bookings` — create a booking using the actual IDs returned by the API.
8. `GET /bookings/{booking_id}` — retrieve the booking.
9. `PATCH /consultations/{consultation_id}/status` — update the consultation status.
10. `POST /consultations/{consultation_id}/prescriptions` — create a prescription when the consultation and user permissions allow it.
11. `POST /users` — create an admin test user.
12. `GET /admin/analytics` — check the basic analytics using the required demo user header.

For booking creation, include the `Idempotency-Key` header. Use a unique test value, such as `demo-booking-001`, and replace example IDs with the actual IDs returned by your API.

Some operations require an `X-User-Id` header. Use the appropriate test user's ID as shown in the Swagger endpoint definition.

Use fictional test data only.

## 8. Database Design

The application uses SQLAlchemy models for the following tables:

- **users:** Stores basic user information and role.
- **doctors:** Stores doctor profile information, specialty, city, and active status.
- **availability_slots:** Stores doctor availability and booking status.
- **consultations:** Stores appointment details and consultation status.
- **prescriptions:** Stores prescription details associated with a consultation and doctor.
- **payments:** Defines a basic payment data model.
- **audit_logs:** Stores selected audit events.

The main relationships connect users to doctor profiles, doctors to availability slots, and consultations to patients, doctors, slots, and prescriptions.

The current application creates database tables through SQLAlchemy when the API starts. A production deployment should use a proper database migration tool such as Alembic.

## 9. API Design

The application follows a REST API approach and uses JSON request and response bodies.

| Method | Endpoint                                         | Purpose                        |
| ------ | ------------------------------------------------ | ------------------------------ |
| GET    | `/health`                                        | API health check               |
| GET    | `/ready`                                         | Database readiness check       |
| POST   | `/users`                                         | Create a user                  |
| GET    | `/doctors`                                       | List and filter doctors        |
| POST   | `/doctors/{doctor_id}/availability`              | Add doctor availability        |
| POST   | `/bookings`                                      | Create an appointment booking  |
| GET    | `/bookings/{booking_id}`                         | Retrieve a booking             |
| PATCH  | `/consultations/{consultation_id}/status`        | Update consultation status     |
| POST   | `/consultations/{consultation_id}/prescriptions` | Create a prescription          |
| GET    | `/admin/analytics`                               | Retrieve basic admin analytics |

For complete request schemas, parameters, and response details, refer to Swagger UI.

## 10. Security and Access Control

The prototype includes basic role checks for selected operations and records selected audit events.

The current implementation uses an `X-User-Id` header as a demonstration identity mechanism for certain endpoints. This is not secure authentication and must not be used as a production identity system.

Before a real deployment, the application needs:

- Secure authentication using an appropriate token or identity provider.
- Strong authorization checks for every protected resource.
- HTTPS and secure secret management.
- Rate limiting and abuse protection.
- Database migrations and tested backup/restore procedures.
- Security testing and privacy review.
- Monitoring, alerting, and production deployment configuration.

This project must not be used to store or process real patient information in its current form.

## 11. Automated Tests

The project includes automated tests using Pytest and FastAPI's test client.

The tests cover basic health and readiness checks, booking idempotency, and validation of an invalid availability slot.

To run the tests locally on Windows, open a terminal in the project root and run:

```bash
python -m venv .venv
```

Activate the environment in Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Or, in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install the dependencies:

```bash
python -m pip install -r requirements.txt
```

Run the tests:

```bash
python -m pytest -q
```

Record the actual test result when running the project. Do not report the tests as passed unless the command completes successfully.

## 12. Continuous Integration

The project includes a GitHub Actions workflow at `.github/workflows/ci.yml`.

The workflow installs Python dependencies and runs the automated tests when configured push or pull-request events occur.

After pushing the repository to GitHub, check the **Actions** tab to confirm whether the workflow passes.

## 13. Architecture and Design Documents

Additional project documentation is available in the `docs/` folder:

- `architecture.md` — architecture overview, design decisions, scaling considerations, and production gaps.
- `booking-flow.mmd` — booking flow diagram source.
- `er-diagram.mmd` — entity relationship diagram source.
- `security-threat-model.md` — security risks and mitigation checklist.
- `api-examples.md` — API examples.

The OpenAPI specification is also available at `/openapi.json` while the API is running.

## 14. Current Limitations

This is a learning and assignment prototype, not a complete production telemedicine platform.

It has not been load-tested against production-scale traffic or independently security-audited. The implementation does not yet provide a complete production authentication system, comprehensive object-level authorization, formal migrations, or production monitoring and recovery infrastructure.

The current scope should be evaluated based on the features implemented and tested, rather than assumed production readiness.

## 15. What I Learned

Through this project, I practiced:

- Building REST APIs with Python and FastAPI.
- Defining database models with SQLAlchemy.
- Connecting an API to PostgreSQL.
- Using Docker Compose to run multiple services.
- Testing API endpoints through Swagger UI.
- Writing automated tests with Pytest.
- Documenting API endpoints and basic system architecture.
- Understanding the importance of authentication, authorization, logging, and data protection.

## 16. Author

**Name:** Jagadeesh

**Project:** Amrutam Telemedicine Backend

**Purpose:** Backend Developer assignment and learning project.

# Privacy Ledger API

The Privacy Ledger API provides programmatic access to a centralized database of privacy-related events. It enables client apps to store, query, and analyze events that impact privacy across legal, regulatory, and technological domains.

---

## Install

### Prerequisites
s
* **PostgreSQL** (local or remote)
* **Python ≥ 3.10** (for running without Docker)
* **Docker** and **Docker Compose** (optional)

* Environment variables for PostgreSQL credentials:

  ```bash
  POSTGRES_USER
  POSTGRES_PASSWORD
  POSTGRES_DB
  ```

---

## Setup (Local PostgreSQL)

For local development, you can use the provided `db.sh` script to initialize your database.

**Usage**:

```bash
# Setup database
./db.sh setup <db_name> [db_user] [db_password]

# Remove database and user
./db.sh rm <db_name> [db_user]
```

**Notes**:

* If `db_user` is not provided, the script uses your current OS user.
* `db_password` is required only if you want to create a new PostgreSQL user.
* The script automatically:

  * Creates the database if missing.
  * Creates the user/role if missing.
  * Grants privileges and ownership.
  * Creates the `pgvector` extension for vector embeddings (requires superuser).
* Currently tailored for Fedora; adjustments may be needed for other OSes.

After setup, the script outputs the connection URL you can use in the `.env` file:

```text
postgresql://<user>:<password>@localhost:5432/<db_name>
```

---

## Deploy

### Using Docker

```bash
docker-compose up --build
```

* Builds the Privacy Ledger API container.
* Runs PostgreSQL with `pgvector` support.
* Mounts `/data` for persistent storage.
* Exposes the API at `http://127.0.0.1:8002`.

### Without Docker (Pure Python)

```bash
python -m api.cli
```

* Connects to a local or remote PostgreSQL instance using credentials in `.env`.
* Only `POSTGRES_DB` is required; the script will use the OS user by default if `POSTGRES_USER` is not set.
* No additional setup is needed beyond a working PostgreSQL database.

---

## Available API Endpoints

| Endpoint           | Method | Description                                                                                                 |
| ------------------ | ------ | ----------------------------------------------------------------------------------------------------------- |
| `/add_event`       | POST   | Add new privacy events. Accepts a list of events in `AddEventsRequest`. Returns the number of events added. |
| `/search_events`   | POST   | Search events with filters, pagination, and sorting. Returns matching events in `SearchEventsResponse`.     |
| `/count_events`    | POST   | Count events based on filter criteria. Returns total count in `CountEventsResponse`.                        |
| `/events_overview` | GET    | Get a summary of top privacy events. Returns an overview in `EventsOverviewResponse`.                       |

---

### Notes

* API supports CORS; can be accessed from any origin.
* Event embeddings use 768-dimensional vectors for similarity search.
* Running without Docker only requires a PostgreSQL instance and environment variables; no other setup is needed.

---

# Database Management Commands

This directory contains custom Django management commands designed to help with local development and database management.

## Available Commands

### `seed_db`

Populates the local database with realistic demo data, allowing you to instantly begin testing and frontend development without manually configuring restaurants or users.

**Usage:**
```bash
python manage.py seed_db
```

**Features:**
- **Idempotent:** It is 100% safe to run this command multiple times. It checks for existing data before creation and will not duplicate any rows if the database is already seeded.
- **Transactional:** The entire operation is wrapped in a database transaction (`@transaction.atomic`). If the script crashes unexpectedly, the database rolls back to prevent a partially-seeded, corrupted state.
- **Demo Users:** Automatically provisions the following test accounts:
  - `admin@example.com` (Role: Admin)
  - `courier@example.com` (Role: Courier)
  - `client@example.com` (Role: Client)
  - *Password for all test accounts:* `password123`

---
*Note: In the future, this command may be expanded to accept CLI arguments (e.g., `--restaurants=50`) and utilize `Faker` for randomized, dynamic data generation.*

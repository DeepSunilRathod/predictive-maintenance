# MySQL Database Setup

## 1. Install MySQL (if not already installed)

- **Windows**: install MySQL Community Server from https://dev.mysql.com/downloads/mysql/
- **macOS**: `brew install mysql && brew services start mysql`
- **Linux (Debian/Ubuntu)**: `sudo apt install mysql-server && sudo systemctl start mysql`

## 2. Create the database and a user (optional but recommended)

```sql
mysql -u root -p

CREATE DATABASE predictive_maintenance CHARACTER SET utf8mb4;
CREATE USER 'pm_user'@'localhost' IDENTIFIED BY 'change_me';
GRANT ALL PRIVILEGES ON predictive_maintenance.* TO 'pm_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

## 3. Configure the backend

Copy `backend/.env.example` to `backend/.env` and fill in your real
`DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`.

## 4. Create tables

You have two equivalent options:

**Option A - let the backend do it automatically (recommended)**
Tables are created automatically on first `uvicorn` startup via
`database/init_db.py`, which also seeds placeholder thresholds and a
default motor row. Nothing else to do.

**Option B - run the raw SQL schema yourself**
```bash
mysql -u root -p < backend/database/schema.sql
```

Either way, running `python -m database.init_db` again later is always safe
- it only creates missing tables and seeds thresholds if the table is empty,
never overwriting tuned values.

## 5. Verify

```bash
mysql -u root -p predictive_maintenance -e "SHOW TABLES;"
```
Expected tables: `sensor_data`, `alerts`, `thresholds`, `motor_info`, `system_settings`.

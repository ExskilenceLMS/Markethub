# MarketHub (E-commerce backend)

## Run the app

From `exskilence_project` (with venv activated and dependencies installed):

```bash
python app.py
```

The server listens on **`http://127.0.0.1:5001`** by default (`PORT` in the environment overrides this, e.g. `PORT=5000 python app.py`).

A log line **“Database unavailable or access denied”** only means `db.create_all()` could not connect; the process can still serve HTTP. Fix `.env` (see below) so auth and other DB routes work.

## Database: apply schema and seed data

Use the same values as in `.env` (`DB_USER`, `DB_PASSWORD`, `DB_NAME`, `DB_HOST`). Run these from the **`exskilence_project`** directory (where `database/` lives).

### 1. Create the database (first time only)

```bash
mysql -h 127.0.0.1 -u YOUR_DB_USER -p -e "CREATE DATABASE IF NOT EXISTS YOUR_DB_NAME CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### 2. Apply tables (`database/schema.sql`)

```bash
mysql -h 127.0.0.1 -u YOUR_DB_USER -p YOUR_DB_NAME < database/schema.sql
```

### 3. Load dummy data (`database/seed_data.sql`)

```bash
mysql -h 127.0.0.1 -u YOUR_DB_USER -p YOUR_DB_NAME < database/seed_data.sql
```

### Example (local MySQL, user `root`, database `markethub`)

```bash
cd "/path/to/exskilence_project"

mysql -h 127.0.0.1 -u root -p -e "CREATE DATABASE IF NOT EXISTS markethub CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"

mysql -h 127.0.0.1 -u root -p markethub < database/schema.sql

mysql -h 127.0.0.1 -u root -p markethub < database/seed_data.sql
```

After a successful connection, restart the Flask app so it can run `db.create_all()` without errors, or rely on the SQL schema alone if tables already exist.

Seed users use password **`user123`** (see comments in `database/seed_data.sql`).

## MySQL 1045 “Access denied” (using password: YES)

That message means **the user and password in `.env` do not match what MySQL expects** for that host.

1. **Set the real password** — In `.env`, `DB_PASSWORD` must be the same password you use for `mysql -u root -p` (or your `DB_USER`). If `root` has **no** password, use an empty value: `DB_PASSWORD=` (nothing after `=`).
2. **Confirm the database exists** — Create `DB_NAME` (e.g. `markethub`) with the SQL in the section above.
3. **`localhost` vs `127.0.0.1`** — Some setups authenticate differently. If problems persist, try `DB_HOST=127.0.0.1` in `.env`.

After fixing credentials, restart the app so `db.create_all()` can connect. You can also apply `database/schema.sql` with the `mysql` client and set `SKIP_DB_CREATE_ALL=1` if you manage schema only via SQL files.

# Oracle Timesheet Data Warehouse

This project defines the schema and setup logic for a **Timesheet Data Warehouse** using Oracle. It includes scripts to create both **source tables** (raw input data) and **dimension/fact tables** (transformed, analysis-ready structures).

---

## 📦 Source Tables

The source tables are meant to store raw, unprocessed data coming from timesheet applications, calendars, or imports such as Excel/CSV files.

### Tables:

- **`src_timesheet_pontaj`**
  - Captures work log entries.
  - **Columns**:
    - `pontaj_id` – primary key
    - `first_name`, `last_name`, `email`
    - `project_name`
    - `pontaj_date`
    - `quantity` – hours worked

- **`src_timesheet_absences`**
  - Captures leave or absence entries.
  - **Columns**:
    - `absence_id` – primary key
    - `first_name`, `last_name`, `email`
    - `absence_type` – e.g., `UL`, `AL`, `SL`, etc.
    - `absence_date`
    - `quantity` – duration of absence

Scripts automatically create and commit these tables using the `SourceTables` class.

---

## 🧱 Dimension and Fact Tables

These are cleaned and structured tables for analytics and reporting purposes.

### Created via the `DimTables` class:

- **`dim_employees`**
  - Employee master data
  - Columns: `employee_id`, `first_name`, `last_name`, `email`

- **`dim_projects`**
  - Projects being worked on
  - Columns: `project_id`, `project_name` (default: `'DavaX'`)

- **`dim_dates`**
  - Date dimension, auto-populated
  - Columns: `date_id`, `year`, `month`, `quarter`, `day`

- **`dim_events`**
  - Events like meetings or absences
  - Columns: `event_id`, `event_name`, `event_type`, `event_date`

- **`fact_timesheets`**
  - Central fact table that joins all dimensions
  - Columns:
    - `timesheet_id`, `employee_id`, `event_id`, `date_id`, `project_id`, `quantity`
  - Constraints:
    - Unique (`employee_id`, `event_id`, `date_id`, `project_id`)
    - Foreign keys to all dimension tables

---

## 🧠 Schema Design Overview

The warehouse follows a **star schema**:

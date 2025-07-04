# 🛠️ DavaX ETL Project

This project builds a star-schema Data Warehouse for timesheet data using Oracle. It reads raw CSV data, creates source and dimension tables, and populates a central fact table using a Python-based ETL pipeline.

---

## 📁 Project Structure

```
ETL_HOMEWORK/
│
├── DavaX/
│   └── ETL/
│       ├── files/                   # CSV files used as raw input
│       ├── scripts/                 # Manual insert scripts (optional)
│       ├── tables_structure/       # Core classes to build & populate tables
│       ├── utils/                  # Reusable utility functions
│       ├── structure.py            # 🔥 Main entrypoint for executing ETL
│       └── requirements.txt        # Python dependencies
```

---

## ⚙️ Setup Instructions

### 1. 📦 Create & Activate Virtual Environment

```bash
# Create environment
python -m venv etl_virtualenv

# Activate (Windows)
etl_virtualenv\Scripts\activate

# Or activate (Linux/Mac)
source etl_virtualenv/bin/activate
```

---

### 2. 📥 Install Dependencies

Make sure you have Oracle Client or `oracledb` access configured, then run using your credentials to connect to the database:

```bash
pip install -r requirements.txt
```

---

### 3. 🚀 Run the ETL Pipeline

The main script is `structure.py`. It creates all necessary tables and populates them.

```bash
python structure.py
```

This script will:

- Create and populate:
  - `src_timesheet_pontaj`
  - `src_timesheet_absences`
  - `src_confluence_absences`
- Create and populate dimension tables:
  - `dim_employees`, `dim_dates`, `dim_projects`, `dim_events`
- Insert calculated facts into:
  - `fact_timesheets`

---

## 📊 Output

After running, your Oracle database will contain a fully built schema with:

- **Source tables** for raw input
- **Dimension tables** for cleaned metadata
- **Fact table** with cross-linked quantities per employee, project, date, and event

---

## 🧪 Notes

- Make sure your Oracle DB is running and accessible.
- Set environment variables or edit connection logic if needed.
- Source CSVs must match expected formats (see `files/` directory).

---

## 📬 Contributors

Dan-Teodor Buzoianu  
Andrei-Madalin Diaconu
Mihai-Alexandru Ionel
Darius Dinu

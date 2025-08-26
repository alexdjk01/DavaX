# Python Microservice Dashboard

##  Overview
This project is a FastAPI-based math microservice with a modern, interactive dashboard for triggering operations and viewing results in real-time.  
It supports persisting requests to both:
- SQLite database (primary storage)
- Streaming framework (JSONL file by default, or Redis Streams if enabled)

Operations available:
- Power 
- Factorial
- Fibonacci
- GCD (Greatest Common Divisor)
- LCM (Least Common Multiple)
- Square Root
- Natural Logarithm

---

## Project Structure

```
Python_Microserv/
│
├── application/                  # FastAPI backend
│   ├── api/                       # Route definitions for each operation
│   ├── db/                        # Database session handling
│   ├── middlewares/               # Custom logging middleware
│   ├── models/                    # SQLAlchemy models
│   ├── services/                  # Business logic for each operation
│   ├── utils/                      # Streaming utilities (file/Redis)
│   └── main.py                    # FastAPI app entry point
│
├── dashboard/                     # Frontend dashboard
│   ├── index.html                 # UI layout
│   ├── style.css                  # Styling (dark mode, split layout)
│   └── script.js                  # Frontend logic + API calls
│
├── scripts/                       # Helper scripts
│   ├── run_all.ps1                # One-click start: Redis + API + Consumer + Dashboard (Windows)
│   ├── run_api_only.ps1           # Start only the API (Windows)
│   ├── run_consumer.ps1           # Start only the Redis stream consumer (Windows)
│   └── run_all.sh                 # One-click start for Linux/macOS
│
├── python_operations.db           # SQLite database (created at runtime)
├── stream.jsonl                   # File stream log (if FILE backend)
├── requirements.txt               # Project dependencies
└── README.md                      # Project documentation
```

---

##  Features
- Interactive Dashboard  
  - Left panel: Input forms for all math operations.
  - Right panel: Live operations console (DB history first, new ops at the top).
- Streaming Support* 
  - Default: Append operations to `stream.jsonl`.
  - Optional: Publish to Redis Streams (`STREAM_BACKEND=REDIS`).
- Logging Middleware 
  - Shows only the current operation in the backend console when triggered from the dashboard.
- Export Operations 
  - Download operation history as CSV via the dashboard.

---

##  Prerequisites
- Python 3.9+ (Python 3.13 tested)
- Docker (for Redis option)
- pip for dependency management
- Modern browser (for dashboard)

---

##  Installation
1. **Clone / Download** the repository.
2. Open a terminal in the project root (`Python_Microserv`).
3. Install dependencies:
   ```powershell
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

---

##  Running the Project

### Option 1: Windows — One Click
Run:
```powershell
.\scripts
run_all.ps1
```
This will:
- Start Redis in Docker if not running.
- Set environment variables for Redis streaming.
- Install dependencies.
- Start FastAPI server in a new PowerShell window.
- Start Redis consumer in another PowerShell window.
- Open the dashboard in your default browser.

---

### Option 3: Manual Run (without scripts)
Start backend:
```bash
export STREAM_BACKEND=FILE  # or REDIS
export REDIS_URL=redis://localhost:6379/0  # if using Redis
uvicorn application.main:app --reload
```

Open dashboard:  
Open `dashboard/index.html` in your browser.

---

##  API Endpoints
| Method | Endpoint    | Body Example                    | Description |
|--------|------------|----------------------------------|-------------|
| POST   | `/pow`     | `{ "base": 2, "exponent": 3 }`   | Calculate power |
| POST   | `/factorial`| `{ "number": 5 }`               | Calculate factorial |
| POST   | `/fibonacci`| `{ "number": 7 }`               | Calculate nth Fibonacci number |
| POST   | `/gcd`     | `{ "a": 12, "b": 18 }`           | Calculate GCD |
| POST   | `/lcm`     | `{ "a": 4, "b": 5 }`             | Calculate LCM |
| POST   | `/sqrt`    | `{ "number": 16 }`               | Calculate square root |
| POST   | `/log`     | `{ "number": 10 }`               | Calculate natural log |
| GET    | `/export`  | *none*                           | Export DB operations to CSV |

---

##  Streaming
- File Backend (default):  
  Operations are appended to `stream.jsonl`.
- Redis Backend:
  1. Start Redis:
     ```bash
     docker run -p 6379:6379 --name pm_redis redis:7
     ```
  2. Set environment variables:
     ```bash
     export STREAM_BACKEND=REDIS
     export REDIS_URL=redis://localhost:6379/0
     ```
  3. Run the Redis consumer:
     ```bash
     python -m application.utils.stream_consumer_redis
     ```
!!! THE RUN_ALL.PS1 SCRIPT DOES EVERYTHING AUTO !!!
---

## Notes
- Dashboard uses `/export` to load DB history on startup.
- Logging middleware ignores `/export` requests so backend console only shows new operations.
- Optional: Add `--no-access-log --log-level warning` to `uvicorn` to reduce access log noise.

---

##  License
This project is for learning purposes as part of the DAVAX Academy - Python OOP Homework.

Author: Ionel Mihai Alexandru , Data Engineer DavaX, Endava BHD

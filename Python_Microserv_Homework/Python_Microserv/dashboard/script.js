// URL for FastAPI
const BASE_URL = "http://127.0.0.1:8000";
document.getElementById("base-url-text").textContent = BASE_URL;

// Load the DB history once without auto-refresh.
let historyLoaded = false;
document.addEventListener("DOMContentLoaded", async () => {
  await refreshHistory();   // one-time load from /export
  historyLoaded = true;
});

// when start a new operation, the console is cleared
const CLEAR_CONSOLE_ON_ACTION = true;

function clearConsole() {
  const consoleEl = document.getElementById("console");
  consoleEl.innerHTML = "";
}

// Console management
let pendingId = 0;
const localPending = new Map(); // id -> entry element

function renderEntry({ id, operation, input_data, result, status, created_at }, isLocal=false) {
  const el = document.createElement("div");
  el.className = "console-entry";
  const statusClass = status === "success" ? "success" : status === "error" ? "error" : "pending";
  const when = created_at ? new Date(created_at).toLocaleString() : new Date().toLocaleTimeString();
  el.innerHTML = `[${when}] <span class="tag ${statusClass}">${status}</span><strong>${operation}</strong>  input=${input_data}  result=${String(result)}`;
  if (isLocal) el.dataset.local = "true";
  return el;
}

function appendPending(operation, inputObj) {
// clear previous content, only shows current operation
  if (historyLoaded && CLEAR_CONSOLE_ON_ACTION) {
    clearConsole();
  }

  const id = ++pendingId;
  const entry = {
    id,
    operation,
    input_data: JSON.stringify(inputObj),
    result: "pending...",
    status: "pending",
    created_at: new Date().toISOString(),
  };
  const el = renderEntry(entry, true);
  document.getElementById("console").prepend(el);
  localPending.set(id, el);
  return id;
}

function finalizePending(id, result, status="success") {
  const el = localPending.get(id);
  if (!el) return;
  const tag = el.querySelector(".tag");
  tag.textContent = status;
  tag.className = `tag ${status}`;
  el.innerHTML = el.innerHTML.replace("pending...", JSON.stringify(result));
  localPending.delete(id);
}

// CSV parsing
function parseCSV(text) {
  const lines = text.trim().split(/\r?\n/);
  if (lines.length <= 1) return [];
  const header = lines[0].split(",");
  return lines.slice(1).map(line => {
    const cols = line.split(",");
    const obj = {};
    header.forEach((h, i) => obj[h] = cols[i]);
    return obj;
  });
}

function renderHistoryToConsole(items) {
  const filterOp = document.getElementById("filter-op").value;
  const filterStatus = document.getElementById("filter-status").value;
  const consoleEl = document.getElementById("console");
  // keep local pending entries at top; then render server history below
  Array.from(consoleEl.children).forEach(child => {
    if (!child.dataset.local) child.remove();
  });
  for (const it of items) {
    if (filterOp && it.operation !== filterOp) continue;
    if (filterStatus && it.status !== filterStatus) continue;
    const el = renderEntry(it);
    consoleEl.appendChild(el);
  }
}

async function refreshHistory() {
  try {
    const res = await fetch(`${BASE_URL}/export`);
    const txt = await res.text();
    const items = parseCSV(txt);
    renderHistoryToConsole(items);
  } catch (e) {
    // nthing
  }
}


// POST JSON
async function postJSON(url, payload) {
  const res = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!res.ok) throw new Error(`HTTP ${res.status}`);
  return await res.json();
}

// Action buttons
document.getElementById("btn-pow").addEventListener("click", async () => {
  const base = parseFloat(document.getElementById("pow-base").value);
  const exponent = parseFloat(document.getElementById("pow-exp").value);
  const pid = appendPending("pow", { base, exponent });
  try {
    const data = await postJSON(`${BASE_URL}/pow`, { base, exponent });
    document.getElementById("powResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

document.getElementById("btn-fact").addEventListener("click", async () => {
  const number = parseInt(document.getElementById("fact-n").value, 10);
  const pid = appendPending("factorial", { number });
  try {
    const data = await postJSON(`${BASE_URL}/factorial`, { number });
    document.getElementById("factorialResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

document.getElementById("btn-fib").addEventListener("click", async () => {
  const number = parseInt(document.getElementById("fib-n").value, 10);
  const pid = appendPending("fibonacci", { number });
  try {
    const data = await postJSON(`${BASE_URL}/fibonacci`, { number });
    document.getElementById("fibonacciResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

document.getElementById("btn-gcd").addEventListener("click", async () => {
  const a = parseInt(document.getElementById("gcd-a").value, 10);
  const b = parseInt(document.getElementById("gcd-b").value, 10);
  const pid = appendPending("gcd", { a, b });
  try {
    const data = await postJSON(`${BASE_URL}/gcd`, { a, b });
    document.getElementById("gcdResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

document.getElementById("btn-lcm").addEventListener("click", async () => {
  const a = parseInt(document.getElementById("lcm-a").value, 10);
  const b = parseInt(document.getElementById("lcm-b").value, 10);
  const pid = appendPending("lcm", { a, b });
  try {
    const data = await postJSON(`${BASE_URL}/lcm`, { a, b });
    document.getElementById("lcmResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

document.getElementById("btn-sqrt").addEventListener("click", async () => {
  const number = parseFloat(document.getElementById("sqrt-n").value);
  const pid = appendPending("sqrt", { number });
  try {
    const data = await postJSON(`${BASE_URL}/sqrt`, { number });
    document.getElementById("sqrtResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

document.getElementById("btn-log").addEventListener("click", async () => {
  const number = parseFloat(document.getElementById("log-n").value);
  const pid = appendPending("log", { number });
  try {
    const data = await postJSON(`${BASE_URL}/log`, { number });
    document.getElementById("logResult").textContent = JSON.stringify(data, null, 2);
    finalizePending(pid, data.result, "success");
  } catch (e) {
    finalizePending(pid, e.message, "error");
  }
});

// Export CSV
document.getElementById("btn-export").addEventListener("click", () => {
  const link = document.createElement("a");
  link.href = `${BASE_URL}/export`;
  link.download = "operations_export.csv";
  link.click();
});

// Re-render on filter change
document.getElementById("filter-op").addEventListener("change", refreshHistory);
document.getElementById("filter-status").addEventListener("change", refreshHistory);

const BASE_URL = "http://127.0.0.1:8000";

async function computePow() {
  event.preventDefault();
  const base = parseFloat(document.getElementById("base").value);
  const exponent = parseFloat(document.getElementById("exponent").value);

  const response = await fetch(`${BASE_URL}/pow`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ base, exponent })
  });

  const data = await response.json();
  document.getElementById("powResult").textContent = JSON.stringify(data, null, 2);
}

async function computeFactorial() {
  event.preventDefault();
  const number = parseInt(document.getElementById("factorialInput").value);

  const response = await fetch(`${BASE_URL}/factorial`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ number })
  });

  const data = await response.json();
  document.getElementById("factorialResult").textContent = JSON.stringify(data, null, 2);
}

async function computeFibonacci() {
  event.preventDefault();
  const number = parseInt(document.getElementById("fibonacciInput").value);

  const response = await fetch(`${BASE_URL}/fibonacci`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ number })
  });

  const data = await response.json();
  document.getElementById("fibonacciResult").textContent = JSON.stringify(data, null, 2);
}

async function computeGCD() {
  event.preventDefault();
  const a = parseInt(document.getElementById("gcdA").value);
  const b = parseInt(document.getElementById("gcdB").value);

  const response = await fetch(`${BASE_URL}/gcd`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ a, b })
  });

  const data = await response.json();
  document.getElementById("gcdResult").textContent = JSON.stringify(data, null, 2);
}

async function computeLCM() {
  event.preventDefault();
  const a = parseInt(document.getElementById("lcmA").value);
  const b = parseInt(document.getElementById("lcmB").value);

  const response = await fetch(`${BASE_URL}/lcm`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ a, b })
  });

  const data = await response.json();
  document.getElementById("lcmResult").textContent = JSON.stringify(data, null, 2);
}

async function computeSqrt() {
  event.preventDefault();
  const number = parseFloat(document.getElementById("sqrtInput").value);

  const response = await fetch(`${BASE_URL}/sqrt`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ number })
  });

  const data = await response.json();
  document.getElementById("sqrtResult").textContent = JSON.stringify(data, null, 2);
}

async function computeLog() {
  event.preventDefault();
  const number = parseFloat(document.getElementById("logInput").value);

  const response = await fetch(`${BASE_URL}/log`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ number })
  });

  const data = await response.json();
  document.getElementById("logResult").textContent = JSON.stringify(data, null, 2);
}

async function exportHistory() {
  const url = `${BASE_URL}/export`;
  //invisible link to downlaod the file
  const link = document.createElement("a");
  link.href = url;
  link.download = "operations_export.csv";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}



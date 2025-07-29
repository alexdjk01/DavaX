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


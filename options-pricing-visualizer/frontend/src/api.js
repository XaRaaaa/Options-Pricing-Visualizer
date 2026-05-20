const defaultHeaders = {
  "Content-Type": "application/json"
};

async function request(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: defaultHeaders,
    body: JSON.stringify(payload)
  });

  if (!response.ok) {
    const message = await response.text();
    throw new Error(message || "Request failed");
  }

  return response.json();
}

export function fetchPrice(payload) {
  return request("/api/price", payload);
}

export function fetchCurve(payload) {
  return request("/api/curve", payload);
}

export function fetchHistory(payload) {
  return request("/api/history", payload);
}

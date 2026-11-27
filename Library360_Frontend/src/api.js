const API_ROOT = import.meta.env.VITE_API_URL || "/api";

export function saveSession(token, role) {
  localStorage.setItem("library360_token", token);
  localStorage.setItem("library360_role", role);
}
export function clearSession() {
  localStorage.removeItem("library360_token");
  localStorage.removeItem("library360_role");
}
export function getToken() {
  return localStorage.getItem("library360_token");
}
export function getRole() {
  return localStorage.getItem("library360_role");
}

export async function api(path, options = {}) {
  const token = getToken();
  const headers = { ...(options.headers || {}) };
  if (!(options.body instanceof FormData) && options.body !== undefined) {
    headers["Content-Type"] = "application/json";
  }
  if (token) headers.Authorization = `Bearer ${token}`;

  const response = await fetch(`${API_ROOT}${path}`, {
    ...options,
    headers
  });

  const contentType = response.headers.get("content-type") || "";
  let data;
  if (contentType.includes("application/json")) {
    data = await response.json();
  } else if (response.status !== 204) {
    data = await response.text();
  }

  if (!response.ok) {
    const detail = data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((item) => item.msg).join(", ")
      : typeof detail === "string" ? detail : `Request failed (${response.status})`;
    throw new Error(message || `Request failed (${response.status})`);
  }
  return data;
}

export const get = (path) => api(path);
export const post = (path, body) => api(path, {
  method: "POST",
  ...(body instanceof FormData ? { body } : { body: JSON.stringify(body ?? {}) })
});
export const put = (path, body) => api(path, {
  method: "PUT",
  body: JSON.stringify(body)
});

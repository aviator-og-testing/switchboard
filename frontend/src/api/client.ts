import { Flag, TargetingRule } from "../types";

const BASE = process.env.REACT_APP_API_BASE || "http://localhost:5000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      "X-Api-Key": localStorage.getItem("apiKey") || "",
      ...(init?.headers || {}),
    },
  });
  if (!res.ok) {
    throw new Error(`${res.status} ${res.statusText}`);
  }
  return res.json();
}

export function listFlags(): Promise<Flag[]> {
  return request<Flag[]>("/api/v1/flags");
}

export function getFlag(id: number): Promise<Flag> {
  return request<Flag>(`/api/v1/flags/${id}`);
}

export function updateFlag(id: number, patch: Partial<Flag>): Promise<Flag> {
  return request<Flag>(`/api/v1/flags/${id}`, {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function saveRule(
  flagId: number,
  rule: Partial<TargetingRule>
): Promise<TargetingRule> {
  return request<TargetingRule>(`/api/v1/flags/${flagId}/rules`, {
    method: "POST",
    body: JSON.stringify(rule),
  });
}

export function deleteRule(flagId: number, ruleId: number): Promise<void> {
  return request<void>(`/api/v1/flags/${flagId}/rules/${ruleId}`, {
    method: "DELETE",
  });
}

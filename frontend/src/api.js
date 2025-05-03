export const BASE_URL = 'http://localhost:8000';

export async function fetchPickers() {
  const res = await fetch(`${BASE_URL}/model/pickers`);
  if (!res.ok) throw new Error('Failed to fetch pickers');
  return res.json();
}

export async function fetchRiskModels() {
  const res = await fetch(`${BASE_URL}/risk/models`);
  if (!res.ok) throw new Error('Failed to fetch risk models');
  return res.json();
}

export async function optimize(model, riskModel) {
  const res = await fetch(`${BASE_URL}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, risk_model: riskModel }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Optimization failed');
  }
  return res.json();
}
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

export async function optimize(model, riskModel, endDate, capital) {
  const body = { model, risk_model: riskModel };
  if (endDate) body.end_date = endDate;
  if (capital) body.capital = capital;
  console.log(body);

  const res = await fetch(`${BASE_URL}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Optimization failed');
  }
  return res.json();
}

export async function savePortfolio(portfolioData) {
  const res = await fetch(`${BASE_URL}/portfolios`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(portfolioData),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Save failed');
  }
  return res.json();
}
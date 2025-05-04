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

export async function getPortfolios() {
  const res = await fetch(`${BASE_URL}/portfolios`);
  if (!res.ok) throw new Error('Failed to fetch portfolios');
  return res.json();
}

export async function getPortfolioById(id) {
  const res = await fetch(`${BASE_URL}/portfolios/${id}`);
  if (!res.ok) throw new Error('Failed to fetch portfolio');
  return res.json();
}

// Update user settings
export async function updateUserSettings({ telegram_id, email }) {
  const res = await fetch(`${BASE_URL}/user`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ telegram_id, email }),
  });
  if (!res.ok) {
    throw new Error('Update failed');
  }
  return res.json();
}

export async function getReminders(portfolioId) {
  const res = await fetch(`${BASE_URL}/portfolios/${portfolioId}/reminders`);
  if (!res.ok) throw new Error('Failed to fetch reminders');
  return res.json();
}

// Update a reminder's active status
export async function updateReminder(portfolioId, reminderId, active) {
  const res = await fetch(
    `${BASE_URL}/portfolios/${portfolioId}/reminders/${reminderId}`,
    {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ active }),
    }
  );
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to update reminder');
  }
  return res.json();
}

export async function updatePortfolio(portfolioId, payload) {
  const res = await fetch(`${BASE_URL}/portfolios/${portfolioId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Update portfolio failed');
  }
  return res.json();
}

export async function rebalancePortfolio(portfolioId, risk_model, capital, as_of) {
  const body = { risk_model };
  if (capital != null) body.capital = capital;
  if (as_of) body.as_of = as_of;
  const res = await fetch(`${BASE_URL}/portfolios/${portfolioId}/rebalance`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Rebalance failed');
  }
  return res.json();
}

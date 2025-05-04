import React, { useState } from 'react';
import { updateUserSettings } from '../api';
import { toast } from 'react-toastify';

export default function SettingsPage() {
  const [telegramId, setTelegramId] = useState('');
  const [email, setEmail] = useState('');

  const handleSave = async () => {
    try {
      await updateUserSettings({ telegram_id: telegramId, email });
      toast.success('Settings saved!');
    } catch (e) {
      toast.error(e.message);
    }
  };

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Settings</h1>
      <div>
        <label className="block text-sm">Telegram ID</label>
        <input className="border p-1 rounded w-full" value={telegramId} onChange={e => setTelegramId(e.target.value)} />
      </div>
      <div>
        <label className="block text-sm">Email</label>
        <input className="border p-1 rounded w-full" value={email} onChange={e => setEmail(e.target.value)} />
      </div>
      <button className="bg-blue-500 text-white px-4 py-2 rounded" onClick={handleSave}>Save Settings</button>
    </div>
  );
}
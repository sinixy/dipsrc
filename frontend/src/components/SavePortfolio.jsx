import React, { useContext, useState } from 'react';
import { PortfolioContext } from '../context/PortfolioContext';
import { toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

export default function SavePortfolio() {
  const { result, runSave } = useContext(PortfolioContext);
  const [showForm, setShowForm] = useState(false);
  const [name, setName] = useState('');
  const [notes, setNotes] = useState('');
  if (!result) return null;

  const handleSubmit = async () => {
    try {
      await runSave(name, notes);
      toast.success('Portfolio saved!');
      setShowForm(false);
      setName('');
      setNotes('');
    } catch (e) {
      toast.error(`Save failed: ${e.message}`);
    }
  };

  return (
    <div className="mt-6">
      {!showForm && (
        <button
          className="w-full bg-blue-900 text-white py-3 rounded hover:bg-blue-800"
          onClick={() => setShowForm(true)}
        >
          Save
        </button>
      )}
      {showForm && (
        <div className="border rounded p-4 bg-gray-800">
          <div className="mb-4 text-gray-400">
            <label className="block text-base">Name</label>
            <input
              type="text"
              className="w-full border p-1 rounded"
              value={name}
              onChange={e => setName(e.target.value)}
            />
          </div>
          <div className="mb-2 text-gray-400">
            <label className="block text-base">Notes</label>
            <textarea
              className="w-full border p-1 rounded"
              rows={3}
              value={notes}
              onChange={e => setNotes(e.target.value)}
            />
          </div>
          <div className="flex space-x-2">
            <button
              className="bg-blue-800 hover:bg-blue-700 text-white px-4 py-2 rounded"
              onClick={handleSubmit}
            >
              Submit
            </button>
            <button
              className="px-4 py-2 rounded border text-gray-400 hover:text-gray-300"
              onClick={() => setShowForm(false)}
            >
              Cancel
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
import test from 'node:test';
import assert from 'node:assert/strict';
import { ApiClient } from '../src/services/apiClient.js';

test('ApiClient формує URL та повертає JSON', async () => {
  const previousFetch = global.fetch;
  global.fetch = async url => ({ ok: true, status: 200, json: async () => [{ id: 1, name: 'Навчання' }] });
  const api = new ApiClient('http://localhost:3000/');
  const result = await api.getCategories();
  assert.deepEqual(result, [{ id: 1, name: 'Навчання' }]);
  global.fetch = previousFetch;
});

test('ApiClient повідомляє про помилку мережі', async () => {
  const previousFetch = global.fetch;
  global.fetch = async () => { throw new Error('offline'); };
  const api = new ApiClient('http://localhost:3000');
  await assert.rejects(api.getNotes(), /Не вдалося підключитися/);
  global.fetch = previousFetch;
});

export class ApiClient {
  constructor(baseUrl) {
    this.baseUrl = baseUrl.replace(/\/$/, '');
  }

  async request(path, options = {}) {
    let response;
    try {
      response = await fetch(`${this.baseUrl}${path}`, {
        headers: { 'Content-Type': 'application/json', ...options.headers },
        ...options
      });
    } catch {
      throw new Error('Не вдалося підключитися до сервера. Перевірте, чи запущено API.');
    }
    if (response.status === 204) return null;
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.message || 'Помилка виконання запиту');
    return data;
  }

  getNotes() { return this.request('/api/notes'); }
  getCategories() { return this.request('/api/categories'); }
  getTags() { return this.request('/api/tags'); }
  createNote(note) { return this.request('/api/notes', { method: 'POST', body: JSON.stringify(note) }); }
  deleteNote(id) { return this.request(`/api/notes/${id}`, { method: 'DELETE' }); }
  createCategory(category) { return this.request('/api/categories', { method: 'POST', body: JSON.stringify(category) }); }
  createTag(tag) { return this.request('/api/tags', { method: 'POST', body: JSON.stringify(tag) }); }
}

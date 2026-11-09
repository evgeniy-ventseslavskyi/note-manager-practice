import { useState } from 'react';

export default function CategoryForm({ onCreate, disabled }) {
  const [name, setName] = useState('');
  async function submit(event) {
    event.preventDefault();
    if (!name.trim()) return;
    await onCreate({ name: name.trim() });
    setName('');
  }
  return (
    <form className="inline-form" onSubmit={submit}>
      <label>
        Нова категорія
        <input value={name} onChange={event => setName(event.target.value)} placeholder="Наприклад, Навчання" disabled={disabled} />
      </label>
      <button type="submit" disabled={disabled}>Додати</button>
    </form>
  );
}

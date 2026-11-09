import { useState } from 'react';

export default function TagInput({ tags, selectedIds, onChange, onCreate, disabled }) {
  const [name, setName] = useState('');
  async function addTag() {
    if (!name.trim()) return;
    const tag = await onCreate({ name: name.trim() });
    onChange([...selectedIds, tag.id]);
    setName('');
  }
  function toggle(id) {
    onChange(selectedIds.includes(id) ? selectedIds.filter(value => value !== id) : [...selectedIds, id]);
  }
  return (
    <fieldset className="tag-input">
      <legend>Теги</legend>
      <div className="tag-input__items">
        {tags.map(tag => <label key={tag.id}><input type="checkbox" checked={selectedIds.includes(tag.id)} onChange={() => toggle(tag.id)} /> {tag.name}</label>)}
      </div>
      <div className="tag-input__create">
        <input value={name} onChange={event => setName(event.target.value)} placeholder="Новий тег" disabled={disabled} />
        <button type="button" onClick={addTag} disabled={disabled}>Додати тег</button>
      </div>
    </fieldset>
  );
}

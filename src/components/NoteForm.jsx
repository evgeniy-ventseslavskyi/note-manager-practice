import { useEffect, useState } from 'react';
import TagInput from './TagInput.jsx';
import './NoteForm.scss';

export default function NoteForm({ categories, tags, onCreate, onCreateTag, storage, disabled }) {
  const [title, setTitle] = useState('');
  const [content, setContent] = useState('');
  const [categoryId, setCategoryId] = useState('');
  const [tagIds, setTagIds] = useState([]);

  useEffect(() => {
    if (categories.length && !categoryId) setCategoryId(String(categories[0].id));
  }, [categories, categoryId]);
  useEffect(() => { storage.setItem('note-draft', JSON.stringify({ title, content })); }, [title, content, storage]);

  async function submit(event) {
    event.preventDefault();
    await onCreate({ title, content, categoryId: Number(categoryId), tagIds });
    setTitle(''); setContent(''); setTagIds([]); storage.removeItem('note-draft');
  }

  return (
    <form className="note-form" onSubmit={submit}>
      <h2>Нова нотатка</h2>
      <label>Заголовок<input required value={title} onChange={event => setTitle(event.target.value)} disabled={disabled || !categories.length} /></label>
      <label>Текст<textarea required rows="5" value={content} onChange={event => setContent(event.target.value)} disabled={disabled || !categories.length} /></label>
      <label>Категорія
        <select value={categoryId} onChange={event => setCategoryId(event.target.value)} disabled={disabled || !categories.length}>
          {categories.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select>
      </label>
      <TagInput tags={tags} selectedIds={tagIds} onChange={setTagIds} onCreate={onCreateTag} disabled={disabled || !categories.length} />
      <button type="submit" disabled={disabled || !categories.length}>Зберегти нотатку</button>
    </form>
  );
}

import { useEffect, useMemo, useState } from 'react';
import CategoryForm from '../components/CategoryForm.jsx';
import NoteForm from '../components/NoteForm.jsx';
import NoteList from '../components/NoteList.jsx';
import SearchBar from '../components/SearchBar.jsx';
import StatusMessage from '../components/StatusMessage.jsx';

export default function NotesPage({ api, storage }) {
  const [notes, setNotes] = useState([]);
  const [categories, setCategories] = useState([]);
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(true);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [query, setQuery] = useState('');
  const [categoryId, setCategoryId] = useState(storage.getItem('selected-category') || '');

  async function load() {
    setLoading(true); setError('');
    try {
      const [loadedNotes, loadedCategories, loadedTags] = await Promise.all([api.getNotes(), api.getCategories(), api.getTags()]);
      setNotes(loadedNotes); setCategories(loadedCategories); setTags(loadedTags);
    } catch (requestError) { setError(requestError.message); }
    finally { setLoading(false); }
  }
  useEffect(() => { load(); }, []);
  function selectCategory(value) { setCategoryId(value); storage.setItem('selected-category', value); }
  async function action(work, successText) {
    setError(''); setMessage('');
    try { await work(); await load(); setMessage(successText); }
    catch (requestError) { setError(requestError.message); throw requestError; }
  }
  const filteredNotes = useMemo(() => notes.filter(note => {
    const textMatches = `${note.title} ${note.content}`.toLowerCase().includes(query.toLowerCase());
    return textMatches && (!categoryId || String(note.categoryId) === String(categoryId));
  }), [notes, query, categoryId]);
  return (
    <>
      <section className="hero"><p className="eyebrow">Практика з програмування ч.3</p><h1>Мої нотатки</h1><p>Створюйте нотатки, використовуйте категорії та теги, знаходьте потрібне через пошук.</p></section>
      <StatusMessage type="error">{error}</StatusMessage><StatusMessage type="success">{message}</StatusMessage>
      {loading ? <StatusMessage>Завантаження даних з API...</StatusMessage> : <>
        <CategoryForm disabled={loading} onCreate={category => action(() => api.createCategory(category), 'Категорію додано.')} />
        <div className="workspace">
          <NoteForm categories={categories} tags={tags} storage={storage} disabled={loading} onCreate={note => action(() => api.createNote(note), 'Нотатку збережено.')} onCreateTag={async tag => { let created; await action(async () => { created = await api.createTag(tag); }, 'Тег додано.'); return created; }} />
          <section><SearchBar value={query} onChange={setQuery} categories={categories} categoryId={categoryId} onCategoryChange={selectCategory} /><NoteList notes={filteredNotes} disabled={loading} onDelete={id => action(() => api.deleteNote(id), 'Нотатку видалено.')} /></section>
        </div>
      </>}
    </>
  );
}

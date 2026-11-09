import './NoteList.scss';

export default function NoteList({ notes, onDelete, disabled }) {
  if (!notes.length) return <p className="empty">Нотаток за цими умовами поки немає.</p>;
  return (
    <section className="note-list" aria-label="Список нотаток">
      {notes.map(note => (
        <article className="note-card" key={note.id}>
          <div className="note-card__heading"><h3>{note.title}</h3><span>{note.Category?.name || 'Без категорії'}</span></div>
          <p>{note.content}</p>
          <div className="note-card__footer">
            <div>{note.Tags?.map(tag => <small key={tag.id}>#{tag.name}</small>)}</div>
            <button className="button--danger" onClick={() => onDelete(note.id)} disabled={disabled}>Видалити</button>
          </div>
        </article>
      ))}
    </section>
  );
}

export default function SearchBar({ value, onChange, categories, categoryId, onCategoryChange }) {
  return (
    <div className="filters">
      <label>Пошук<input value={value} onChange={event => onChange(event.target.value)} placeholder="Текст або заголовок" /></label>
      <label>Категорія
        <select value={categoryId} onChange={event => onCategoryChange(event.target.value)}>
          <option value="">Усі категорії</option>
          {categories.map(category => <option key={category.id} value={category.id}>{category.name}</option>)}
        </select>
      </label>
    </div>
  );
}

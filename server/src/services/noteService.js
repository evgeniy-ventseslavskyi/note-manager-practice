class NoteService {
  constructor({ noteRepository, categoryRepository, tagRepository }) {
    this.noteRepository = noteRepository;
    this.categoryRepository = categoryRepository;
    this.tagRepository = tagRepository;
    this.include = [{ association: 'Category' }, { association: 'Tags', through: { attributes: [] } }];
  }
  getAll() { return this.noteRepository.findAll({ include: this.include }); }
  async getById(id) {
    const note = await this.noteRepository.findById(id, { include: this.include });
    if (!note) throw Object.assign(new Error('Нотатку не знайдено'), { status: 404 });
    return note;
  }
  async create(data) { return this._save(null, data); }
  async update(id, data) { return this._save(await this.getById(id), data); }
  async _save(note, data) {
    if (!data.title?.trim() || !data.content?.trim() || !data.categoryId) {
      throw Object.assign(new Error('Потрібні title, content і categoryId'), { status: 400 });
    }
    if (!await this.categoryRepository.findById(data.categoryId)) {
      throw Object.assign(new Error('Категорію не знайдено'), { status: 400 });
    }
    const tagIds = [...new Set(data.tagIds || [])];
    const tags = await Promise.all(tagIds.map(id => this.tagRepository.findById(id)));
    if (tags.some(tag => !tag)) throw Object.assign(new Error('Один із тегів не знайдено'), { status: 400 });
    const saved = note ? await note.update(data) : await this.noteRepository.create(data);
    await saved.setTags(tags);
    return this.getById(saved.id);
  }
  async delete(id) {
    const note = await this.getById(id);
    await note.destroy();
  }
}
module.exports = { NoteService };

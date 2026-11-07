class BaseRepository {
  constructor(model) { this.model = model; }
  findAll(options = {}) { return this.model.findAll(options); }
  findById(id, options = {}) { return this.model.findByPk(id, options); }
  create(data) { return this.model.create(data); }
  async update(id, data) {
    const item = await this.findById(id);
    if (!item) return null;
    return item.update(data);
  }
  async delete(id) {
    const item = await this.findById(id);
    if (!item) return false;
    await item.destroy();
    return true;
  }
}
module.exports = { BaseRepository };

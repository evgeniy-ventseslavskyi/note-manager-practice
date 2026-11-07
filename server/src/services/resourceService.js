class ResourceService {
  constructor(repository, resourceName) {
    this.repository = repository;
    this.resourceName = resourceName;
  }
  getAll() { return this.repository.findAll(); }
  async getById(id) {
    const item = await this.repository.findById(id);
    if (!item) throw Object.assign(new Error(`${this.resourceName} не знайдено`), { status: 404 });
    return item;
  }
  create(data) { return this.repository.create(data); }
  async update(id, data) {
    const item = await this.repository.update(id, data);
    if (!item) throw Object.assign(new Error(`${this.resourceName} не знайдено`), { status: 404 });
    return item;
  }
  async delete(id) {
    if (!await this.repository.delete(id)) throw Object.assign(new Error(`${this.resourceName} не знайдено`), { status: 404 });
  }
}
module.exports = { ResourceService };

const { createContainer, asFunction, asValue } = require('awilix');
const { createDatabase } = require('./config/database');
const { defineModels } = require('./models');
const { BaseRepository } = require('./repositories/baseRepository');
const { ResourceService } = require('./services/resourceService');
const { NoteService } = require('./services/noteService');

function buildContainer() {
  const container = createContainer();
  const sequelize = createDatabase();
  const models = defineModels(sequelize);
  container.register({
    sequelize: asValue(sequelize),
    categoryRepository: asFunction(() => new BaseRepository(models.Category)).singleton(),
    tagRepository: asFunction(() => new BaseRepository(models.Tag)).singleton(),
    noteRepository: asFunction(() => new BaseRepository(models.Note)).singleton(),
    categoryService: asFunction(({ categoryRepository }) => new ResourceService(categoryRepository, 'Категорію')).singleton(),
    tagService: asFunction(({ tagRepository }) => new ResourceService(tagRepository, 'Тег')).singleton(),
    noteService: asFunction(deps => new NoteService(deps)).singleton()
  });
  return container;
}
module.exports = { buildContainer };

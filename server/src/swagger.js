const swaggerJsdoc = require('swagger-jsdoc');
const definition = {
  openapi: '3.0.0',
  info: { title: 'Note Manager API', version: '1.0.0', description: 'REST API для нотаток, категорій і тегів' },
  servers: [{ url: 'http://localhost:3000' }],
  components: { schemas: {
    Category: { type: 'object', required: ['name'], properties: { id: { type: 'integer' }, name: { type: 'string' }, description: { type: 'string' } } },
    Tag: { type: 'object', required: ['name'], properties: { id: { type: 'integer' }, name: { type: 'string' } } },
    Note: { type: 'object', required: ['title', 'content', 'categoryId'], properties: { id: { type: 'integer' }, title: { type: 'string' }, content: { type: 'string' }, categoryId: { type: 'integer' }, tagIds: { type: 'array', items: { type: 'integer' } } } }
  } },
  paths: {}
};
for (const [path, schema] of [['/api/categories', 'Category'], ['/api/tags', 'Tag'], ['/api/notes', 'Note']]) {
  definition.paths[path] = {
    get: { summary: `Список ${schema}`, responses: { 200: { description: 'OK' } } },
    post: { summary: `Створити ${schema}`, requestBody: { required: true, content: { 'application/json': { schema: { $ref: `#/components/schemas/${schema}` } } } }, responses: { 201: { description: 'Створено' } } }
  };
  definition.paths[`${path}/{id}`] = {
    get: { summary: `Отримати ${schema}`, parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }], responses: { 200: { description: 'OK' }, 404: { description: 'Не знайдено' } } },
    patch: { summary: `Оновити ${schema}`, parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }], responses: { 200: { description: 'OK' } } },
    delete: { summary: `Видалити ${schema}`, parameters: [{ name: 'id', in: 'path', required: true, schema: { type: 'integer' } }], responses: { 204: { description: 'Видалено' } } }
  };
}
module.exports = swaggerJsdoc({ definition, apis: [] });

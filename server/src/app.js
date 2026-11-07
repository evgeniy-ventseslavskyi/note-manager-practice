require('dotenv').config();
const express = require('express');
const cors = require('cors');
const morgan = require('morgan');
const swaggerUi = require('swagger-ui-express');
const { buildContainer } = require('./container');
const { resourceRoutes } = require('./routes/resourceRoutes');
const { notFound, errorHandler } = require('./middleware/errorHandler');
const swaggerSpec = require('./swagger');

async function createApp() {
  const app = express();
  const container = buildContainer();
  await container.resolve('sequelize').sync();
  app.use(cors());
  app.use(morgan('dev'));
  app.use(express.json());
  app.get('/health', (_req, res) => res.json({ status: 'ok' }));
  app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));
  app.use('/api/categories', resourceRoutes(container.resolve('categoryService')));
  app.use('/api/tags', resourceRoutes(container.resolve('tagService')));
  app.use('/api/notes', resourceRoutes(container.resolve('noteService')));
  app.use(notFound);
  app.use(errorHandler);
  return app;
}

if (require.main === module) {
  createApp().then(app => app.listen(process.env.PORT || 3000, () => console.log('API started on port 3000')));
}
module.exports = { createApp };

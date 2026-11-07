const express = require('express');
const { resourceController } = require('../controllers/resourceController');

function resourceRoutes(service) {
  const router = express.Router();
  const controller = resourceController(service);
  router.get('/', controller.list);
  router.get('/:id', controller.get);
  router.post('/', controller.create);
  router.patch('/:id', controller.update);
  router.delete('/:id', controller.remove);
  return router;
}
module.exports = { resourceRoutes };

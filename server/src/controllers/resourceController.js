function resourceController(service) {
  return {
    list: async (_req, res) => res.json(await service.getAll()),
    get: async (req, res) => res.json(await service.getById(req.params.id)),
    create: async (req, res) => res.status(201).json(await service.create(req.body)),
    update: async (req, res) => res.json(await service.update(req.params.id, req.body)),
    remove: async (req, res) => { await service.delete(req.params.id); res.status(204).end(); }
  };
}
module.exports = { resourceController };

function notFound(req, _res, next) {
  next(Object.assign(new Error(`Маршрут ${req.method} ${req.originalUrl} не знайдено`), { status: 404 }));
}
function errorHandler(error, _req, res, _next) {
  console.error(error.message);
  res.status(error.status || 500).json({ error: error.message || 'Внутрішня помилка сервера' });
}
module.exports = { notFound, errorHandler };

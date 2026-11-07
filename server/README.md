# Note Manager API

Серверна частина проєкту «Менеджер нотаток». Реалізована як REST API на Node.js та Express.

## Технології

- Node.js, Express;
- SQLite + Sequelize ORM;
- Awilix DI-контейнер;
- CORS, Morgan, централізована обробка помилок;
- Swagger UI.

## Запуск

```bash
cd server
npm install
cp .env.example .env
npm start
```

API працює за адресою `http://localhost:3000`.

- Swagger: `http://localhost:3000/api-docs`
- Перевірка сервера: `GET /health`

## Ресурси

- `/api/categories` — категорії;
- `/api/tags` — теги;
- `/api/notes` — нотатки.

Кожен ресурс підтримує GET, POST, PATCH та DELETE. Нотатка належить категорії та може мати багато тегів.

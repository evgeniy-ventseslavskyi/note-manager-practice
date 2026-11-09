# Клієнтська частина Менеджера нотаток

React-клієнт для серверного API з папки `../server`. У проєкті реалізовано компоненти, SCSS, маршрутизацію, DI-контейнер, Fetch API, обробку помилок та localStorage.

## Запуск

Спочатку у першому терміналі запустіть сервер:

```bash
cd ../server
npm install
npm start
```

Потім у другому терміналі запустіть клієнт:

```bash
cd client
npm install
cp .env.example .env
npm run dev
```

Відкрийте адресу, яку покаже Vite (зазвичай `http://localhost:5173`).

## Перевірка

```bash
npm test
npm run build
```

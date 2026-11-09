import { Route, Routes } from 'react-router-dom';
import Header from './components/Header.jsx';
import NotesPage from './pages/NotesPage.jsx';
import AboutPage from './pages/AboutPage.jsx';
import { services } from './services/container.js';

export default function App() {
  return (
    <div className="app-shell">
      <Header />
      <main className="container">
        <Routes>
          <Route path="/" element={<NotesPage api={services.api} storage={services.storage} />} />
          <Route path="/about" element={<AboutPage />} />
        </Routes>
      </main>
    </div>
  );
}

import { NavLink } from 'react-router-dom';
import './Header.scss';

export default function Header() {
  return (
    <header className="header">
      <div className="container header__content">
        <NavLink className="header__brand" to="/">Менеджер нотаток</NavLink>
        <nav className="header__nav" aria-label="Основна навігація">
          <NavLink to="/" end>Нотатки</NavLink>
          <NavLink to="/about">Про застосунок</NavLink>
        </nav>
      </div>
    </header>
  );
}

import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header({ sidebarOpen, setSidebarOpen }) {
  useEffect(() => {
    const languageSelector = document.getElementById("language-selector");
    const root = document.getElementById("root");

    const loadLanguage = async (lang) => {
      const response = await fetch(`/assets/locales/${lang}.json`);
      const translations = await response.json();

      document.title = translations.title;
      root.innerHTML = `<h1>${translations.welcomeMessage}</h1>`;
    };

    // Load default language
    loadLanguage("en");

    // Change language on selection
    languageSelector.addEventListener("change", (event) => {
      loadLanguage(event.target.value);
    });
  }, []);

  return (
    <header className="header">
      <button
        className="sidebar-toggle"
        aria-label={sidebarOpen ? "Collapse sidebar" : "Expand sidebar"}
        onClick={() => setSidebarOpen(!sidebarOpen)}
      >
        ☰
      </button>
      <img src="/assets/img/g2m.svg" alt="G^2M" className="logo-image" />
      <h1 className="logo"><Link to="/" aria-label="UrbanHeatInsight Home">UrbanHeatInsight</Link></h1>
      <nav className="nav-links">
        <Link to="/">Home</Link>
        <Link to="/about">About</Link>
      </nav>
      <select className='language-select' id="language-selector">
        <option className='language-select-option' value="en">English</option>
        <option className='language-select-option' value="de">Deutsch</option>
      </select>
    </header>
  );
}

export default Header;

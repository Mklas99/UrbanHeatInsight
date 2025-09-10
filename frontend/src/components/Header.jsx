import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header({ sidebarOpen, setSidebarOpen }) {
  const [translations, setTranslations] = useState({ title: '', welcomeMessage: '' });

  useEffect(() => {
    const languageSelector = document.getElementById("language-selector");

    const loadLanguage = async (lang) => {
      const response = await fetch(`/assets/locales/${lang}.json`);
      const translations = await response.json();

      document.title = translations.title;
      setTranslations(translations); // Update state with translations
    };

    // Load default language
    loadLanguage("en");

    // Change language on selection
    languageSelector.addEventListener("change", (event) => {
      loadLanguage(event.target.value);
    });

    // Cleanup event listener on unmount
    return () => {
      languageSelector.removeEventListener("change", (event) => {
        loadLanguage(event.target.value);
      });
    };
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
      <h1 className="logo"><Link to="/" aria-label="UrbanHeatInsight Home">Urban Heat Insight</Link></h1> 
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

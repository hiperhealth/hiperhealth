import React from "react";
import { Navbar, Nav, Container, Dropdown } from "react-bootstrap";
import { useTranslation } from "react-i18next";

export default function AppNavbar() {
  const { i18n, t } = useTranslation();

  const changeLanguage = (lng) => {
    i18n.changeLanguage(lng);
  };

  return (
    <Navbar bg="primary" variant="dark" expand="lg">
      <Container>
        {/* App brand / title */}
        <Navbar.Brand href="/" className="fw-bold text-white">
          {t('navbar.brand')}
        </Navbar.Brand>

        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          {/* Left side navigation */}
          <Nav className="me-auto">
            <Nav.Link href="/">{t('navbar.dashboard')}</Nav.Link>
            <Nav.Link href="/patients">{t('navbar.patients')}</Nav.Link>
            <Nav.Link href="/demographics">{t('navbar.addPatient')}</Nav.Link>
          </Nav>

          {/* Right side language dropdown */}
          <Dropdown align="end">
            <Dropdown.Toggle variant="light" size="sm" id="dropdown-language">
              🌐 {i18n.language.toUpperCase()}
            </Dropdown.Toggle>

            <Dropdown.Menu>
              <Dropdown.Item onClick={() => changeLanguage("en")}>
                {t('navbar.english')}
              </Dropdown.Item>
              <Dropdown.Item onClick={() => changeLanguage("es")}>
                {t('navbar.spanish')}
              </Dropdown.Item>
            </Dropdown.Menu>
          </Dropdown>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
}

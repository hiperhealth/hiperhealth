import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Form, Button, Container } from 'react-bootstrap';
import { useTranslation } from 'react-i18next';

export default function LanguageSelection() {
  const { i18n, t } = useTranslation();
  const navigate = useNavigate();

  const handleLanguageChange = (e) => {
    i18n.changeLanguage(e.target.value);
  };

  const handleSubmit = () => navigate('/demographics');

  return (
    <Container className="mt-5">
      <h3>{t('language.title')}</h3>
      <Form.Group className="mb-3">
        <Form.Label>{t('language.label')}</Form.Label>
      <Form.Select onChange={handleLanguageChange}>
  <option value="en">English</option>
  <option value="es">Español</option>
</Form.Select>

      </Form.Group>
      <Button onClick={handleSubmit}>{t('language.continue')}</Button>
    </Container>
  );
}

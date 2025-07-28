"""Tests for the medical_reports module."""

import os

import pytest

from sdx.agents.extraction.medical_reports import (
    extract_text_from_image,
    extract_text_from_pdf,
    get_report_data_from_image,
    get_report_data_from_pdf,
)


def test_extract_text_from_pdf(reports_pdf_dir):
    """Test PDF text extraction functionality."""
    test_files = list(reports_pdf_dir.glob('*.pdf'))
    if not test_files:
        pytest.skip('No test PDF files available in the reports directory')

    for pdf_path in test_files:
        text = extract_text_from_pdf(pdf_path)
        assert isinstance(text, str)
        assert len(text) > 0, (
            f'Extracted text from {pdf_path} should not be empty'
        )


def test_extract_text_nonexistent_file():
    """Test error handling for non-existent PDF files."""
    with pytest.raises(FileNotFoundError):
        extract_text_from_pdf('nonexistent_file.pdf')


@pytest.mark.skipif(
    not os.environ.get('OPENAI_API_KEY'), reason='OpenAI API key not available'
)
def test_get_report_data_from_pdf(reports_pdf_dir, api_key_openai):
    """Test FHIR data extraction from PDF."""
    test_files = list(reports_pdf_dir.glob('*.pdf'))
    if not test_files:
        pytest.skip('No test PDF files available in the reports directory')
    for pdf_path in test_files:
        fhir_data = get_report_data_from_pdf(pdf_path, api_key=api_key_openai)
        assert isinstance(fhir_data, dict)
        assert len(fhir_data) > 0, (
            f'No FHIR resources was extracted form {pdf_path}'
        )

        # Common FHIR resource types include Patient, Condition, Observation.
        expected_resource_types = {
            'Patient',
            'Condition',
            'Observation',
            'DiagnosticReport',
        }
        assert any(
            resource_type in fhir_data
            for resource_type in expected_resource_types
        ), f'No expected FHIR resource types found in {pdf_path}'


def test_extract_text_from_image(reports_image_dir):
    """Test image text extraction functionality."""
    test_files = (
        list(reports_image_dir.glob('*.png'))
        + list(reports_image_dir.glob('*.jpg'))
        + list(reports_image_dir.glob('*.jpeg'))
    )
    if not test_files:
        pytest.skip('No test image files available in the reports directory')
    for image_path in test_files:
        text = extract_text_from_image(image_path)
        assert isinstance(text, str)
        assert len(text) > 0, (
            f'Extracted text from {image_path} should not be empty'
        )


def test_extract_text_nonexistent_image():
    """Test error handling for non-existent image files."""
    with pytest.raises(FileNotFoundError):
        extract_text_from_image('nonexistent_file.png')


@pytest.mark.skipif(
    not os.environ.get('OPENAI_API_KEY'), reason='OpenAI API key not available'
)
def test_get_report_data_from_image(reports_image_dir, api_key_openai):
    """Test FHIR data extraction from image."""
    test_files = (
        list(reports_image_dir.glob('*.png'))
        + list(reports_image_dir.glob('*.jpg'))
        + list(reports_image_dir.glob('*.jpeg'))
    )
    if not test_files:
        pytest.skip('No test image files available in the reports directory')
    for pdf_path in test_files:
        fhir_data = get_report_data_from_image(
            pdf_path, api_key=api_key_openai
        )
        assert isinstance(fhir_data, dict)
        assert len(fhir_data) > 0, (
            f'No FHIR resources was extracted {pdf_path}'
        )
        expected_resource_types = {
            'Patient',
            'Condition',
            'Observation',
            'DiagnosticReport',
        }
        assert any(
            resource_type in fhir_data
            for resource_type in expected_resource_types
        ), f'No expected FHIR resource types found in {pdf_path}'

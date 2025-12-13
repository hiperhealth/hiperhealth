"""Tests for DICOM medical report extraction."""

from pathlib import Path

import pytest

from hiperhealth.agents.extraction.dicom_extractor import (
    DICOMTextExtractor,
    MedicalReportExtractorError,
)

# Paths
TEST_DATA_PATH = Path(__file__).parent / 'data' / 'reports' / 'dicom_files'
DICOM_FILE = (
    TEST_DATA_PATH
    / '1.2.276.0.7230010.3.1.4.8323329.5797.1517875190.762694.dcm'
)


def test_dicom_file_exists():
    """Ensure the DICOM test file exists."""
    assert DICOM_FILE.exists()


def test_extract_text_from_dicom_file():
    """Test text extraction from a valid DICOM file."""
    text = DICOMTextExtractor.extract_text(DICOM_FILE)
    assert isinstance(text, str)
    assert len(text.strip()) > 0


def test_dicom_metadata_present_in_output():
    """Ensure extracted text contains expected DICOM metadata fields."""
    text = DICOMTextExtractor.extract_text(DICOM_FILE)

    expected_fields = [
        'Patient',
        'Study',
        'Modality',
    ]

    assert any(field in text for field in expected_fields)


def test_invalid_dicom_file_raises():
    """Test that invalid DICOM input raises a proper exception."""
    invalid_path = Path(__file__)  # not a DICOM

    with pytest.raises(MedicalReportExtractorError):
        DICOMTextExtractor.extract_text(invalid_path)

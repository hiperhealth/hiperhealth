"""Tests for DICOM extraction utilities in the sdx package.

These exercises verify metadata extraction and robustness when fields are
missing. The sample DICOM file used for tests is located under
``tests/data/dicom/``.
"""

from pathlib import Path

import pydicom
import pytest

from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import ExplicitVRLittleEndian, generate_uid
from sdx.agents.extraction.dicom import DicomExtractor

# path to the sample DICOM test file
DATA_DIR = Path(__file__).parent / 'data' / 'dicom'
SAMPLE_DICOM = DATA_DIR / 'ID_0000_AGE_0060_CONTRAST_1_CT.dcm'


@pytest.fixture
def extractor():
    """Fixture for initializing the DicomExtractor."""
    return DicomExtractor()


def test_extract_metadata_basic(extractor):
    """Ensure metadata extraction works on a valid DICOM file."""
    assert SAMPLE_DICOM.exists(), (
        f'Sample DICOM file not found at {SAMPLE_DICOM}'
    )

    metadata = extractor.extract_metadata(SAMPLE_DICOM)

    # Basic structural checks
    assert isinstance(metadata, dict)
    assert 'PatientID' in metadata
    assert 'Modality' in metadata
    assert 'StudyDate' in metadata
    assert 'SeriesDescription' in metadata


def test_extract_metadata_missing_fields(extractor, tmp_path):
    """Ensure missing DICOM fields are handled gracefully."""
    # Provide minimal file meta and encoding so pydicom can write a conformant
    # DICOM file. Use FileDataset (not plain Dataset) and a 128-byte
    # preamble so the 'DICM' prefix and file meta info are written.
    file_meta = FileMetaDataset()
    file_meta.TransferSyntaxUID = ExplicitVRLittleEndian
    file_meta.MediaStorageSOPClassUID = generate_uid()
    file_meta.MediaStorageSOPInstanceUID = generate_uid()
    file_meta.ImplementationClassUID = generate_uid()

    test_file = tmp_path / 'empty.dcm'
    # FileDataset writes the file meta and preamble when saved
    ds = FileDataset(
        str(test_file), {}, file_meta=file_meta, preamble=b'\0' * 128
    )
    ds.save_as(
        test_file,
        enforce_file_format=True,
        little_endian=True,
        implicit_vr=False,
    )

    metadata = extractor.extract_metadata(test_file)

    # fallback values for missing tags
    assert metadata['PatientID'] == 'Unknown'
    assert metadata['StudyDate'] == 'Unknown'


def test_load_dicom_method(extractor):
    """Verify the internal DICOM loading method works safely."""
    ds = extractor._load_dicom(SAMPLE_DICOM, stop_before_pixels=True)
    assert isinstance(ds, pydicom.Dataset)
    assert hasattr(ds, 'PatientID') or hasattr(ds, 'Modality')


def test_extract_fhir_requires_api_key(extractor, monkeypatch):
    """Ensure extract_fhir raises EnvironmentError without an API key."""
    monkeypatch.delenv('OPENAI_API_KEY', raising=False)
    with pytest.raises(EnvironmentError):
        extractor.extract_fhir(SAMPLE_DICOM)

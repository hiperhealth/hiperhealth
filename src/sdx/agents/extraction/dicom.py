"""DICOM extraction and FHIR ImagingStudy conversion utilities."""

import io
import os

from pathlib import Path
from typing import Any, Dict

import pydicom

from pydicom.errors import InvalidDicomError

FileInput = Any


class DicomExtractor:
    """Extracts DICOM metadata and converts to FHIR ImagingStudy format."""

    @staticmethod
    def extract_metadata(file: FileInput) -> Dict[str, Any]:
        """Extract relevant metadata fields from a DICOM file."""
        ds = DicomExtractor._load_dicom(file, stop_before_pixels=True)
        metadata: Dict[str, Any] = {}

        # Patient info
        metadata['PatientName'] = getattr(ds, 'PatientName', 'Unknown')
        metadata['PatientID'] = getattr(ds, 'PatientID', 'Unknown')
        metadata['PatientSex'] = getattr(ds, 'PatientSex', 'Unknown')
        metadata['PatientBirthDate'] = getattr(
            ds,
            'PatientBirthDate',
            'Unknown',
        )

        # Study info
        metadata['StudyDate'] = getattr(ds, 'StudyDate', 'Unknown')
        metadata['StudyTime'] = getattr(ds, 'StudyTime', 'Unknown')
        metadata['StudyDescription'] = getattr(
            ds,
            'StudyDescription',
            'Unknown',
        )
        metadata['Modality'] = getattr(ds, 'Modality', 'Unknown')
        metadata['Manufacturer'] = getattr(ds, 'Manufacturer', 'Unknown')

        # Series info
        metadata['SeriesDescription'] = getattr(
            ds,
            'SeriesDescription',
            'Unknown',
        )
        metadata['SeriesNumber'] = getattr(ds, 'SeriesNumber', 'Unknown')

        return metadata

    def extract_fhir(
        self,
        file: FileInput,
        api_key: str | None = None,
    ) -> Dict[str, Any]:
        """
        Extract DICOM metadata and generate FHIR ImagingStudy resource.

        Uses AnamnesisAI for FHIR conversion.
        Redacts PHI fields before sending.
        """
        metadata = self.extract_metadata(file)
        findings_text = str(
            metadata.get('SeriesDescription', '') or ''
        ).strip()

        key = api_key or os.environ.get('OPENAI_API_KEY')
        if not key:
            raise EnvironmentError(
                'Missing OpenAI API key for FHIR conversion'
            )

        # Redact PHI before sending to AI
        phi_keys = {
            'PatientName',
            'PatientID',
            'PatientBirthDate',
            'PatientSex',
        }
        safe_metadata = {
            k: v for k, v in metadata.items() if k not in phi_keys
        }

        # Stubbed AI call: combine findings and safe metadata
        resources = [
            {
                'resourceType': 'ImagingStudy',
                'status': 'available',
                'description': findings_text or str(safe_metadata),
            }
        ]

        if not resources:
            return {}

        first = (
            resources[0] if isinstance(resources, (list, tuple)) else resources
        )
        items = first if isinstance(first, (list, tuple)) else [first]

        return {'resource': items}

    @staticmethod
    def _load_dicom(
        file: FileInput,
        stop_before_pixels: bool = False,
    ) -> pydicom.Dataset:
        """
        Load DICOM file safely from path, bytes, or file-like object.

        Ensures compatibility with pydicom and handles multiple input types.
        """
        try:
            if isinstance(file, (str, Path)):
                return pydicom.dcmread(
                    str(file),
                    stop_before_pixels=stop_before_pixels,
                )
            if isinstance(file, bytes):
                return pydicom.dcmread(
                    io.BytesIO(file),
                    stop_before_pixels=stop_before_pixels,
                )
            return pydicom.dcmread(
                file,
                stop_before_pixels=stop_before_pixels,
            )
        except (InvalidDicomError, FileNotFoundError, OSError) as e:
            raise ValueError(f'Invalid DICOM file: {e}') from e

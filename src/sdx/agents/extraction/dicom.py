"""DICOM extraction and FHIR ImagingStudy conversion utilities."""

import io
import re

from pathlib import Path
from typing import Any, Dict

FileInput = Any


class DicomExtractor:
    """Extracts DICOM metadata and converts to FHIR ImagingStudy format.

    pydicom is an optional dependency. Import is done lazily when DICOM
    functionality is used so the package can be installed without pydicom.
    """

    @staticmethod
    def _get_str(ds: Any, name: str, default: str = 'Unknown') -> str:
        """Return a JSON-safe string for a DICOM attribute."""
        val = getattr(ds, name, None)
        return str(val) if val not in (None, '') else default

    @staticmethod
    def _redact_metadata(metadata: Dict[str, Any]) -> Dict[str, str]:
        """Return a copy of metadata with a limited set of PHI keys removed.

        Not exhaustive.
        """
        phi_keys = {
            'PatientName',
            'PatientID',
            'PatientBirthDate',
            'PatientSex',
            'StudyDate',
            'StudyTime',
            'StudyDescription',
            'SeriesDescription',
            'AccessionNumber',
            'InstitutionName',
            'ReferringPhysicianName',
            'OperatorsName',
            'PerformingPhysicianName',
            'RequestingPhysician',
            'ProtocolName',
            'StationName',
            'OtherPatientIDs',
        }
        return {k: str(v) for k, v in metadata.items() if k not in phi_keys}

    @staticmethod
    def _validate_uid(uid: str) -> str:
        """Validate DICOM UID format and length."""
        uid = uid.strip()
        if not uid or len(uid) > 64 or not re.fullmatch(r'\d+(\.\d+)+', uid):
            raise ValueError(f'Invalid DICOM UID: {uid!r}')
        return uid

    @staticmethod
    def extract_metadata(file: FileInput) -> Dict[str, Any]:
        """Extract relevant metadata fields from a DICOM file."""
        ds = DicomExtractor._load_dicom(file, stop_before_pixels=True)
        metadata: Dict[str, Any] = {}

        # Patient info
        metadata['PatientName'] = DicomExtractor._get_str(ds, 'PatientName')
        metadata['PatientID'] = DicomExtractor._get_str(ds, 'PatientID')
        metadata['PatientSex'] = DicomExtractor._get_str(ds, 'PatientSex')
        metadata['PatientBirthDate'] = DicomExtractor._get_str(
            ds, 'PatientBirthDate'
        )

        # Study info
        metadata['StudyDate'] = DicomExtractor._get_str(ds, 'StudyDate')
        metadata['StudyTime'] = DicomExtractor._get_str(ds, 'StudyTime')
        metadata['StudyDescription'] = DicomExtractor._get_str(
            ds, 'StudyDescription'
        )
        metadata['Modality'] = DicomExtractor._get_str(ds, 'Modality')
        metadata['Manufacturer'] = DicomExtractor._get_str(ds, 'Manufacturer')

        # Series info
        metadata['SeriesDescription'] = DicomExtractor._get_str(
            ds, 'SeriesDescription'
        )
        metadata['SeriesNumber'] = DicomExtractor._get_str(ds, 'SeriesNumber')

        # UIDs
        metadata['StudyInstanceUID'] = DicomExtractor._get_str(
            ds, 'StudyInstanceUID', default=''
        )
        metadata['SeriesInstanceUID'] = DicomExtractor._get_str(
            ds, 'SeriesInstanceUID', default=''
        )

        return metadata

    def extract_fhir(
        self,
        file: FileInput,
        api_key: str | None = None,
        subject_reference: str | None = None,
        include_series_description: bool = False,
    ) -> Dict[str, Any]:
        """Build a minimally valid FHIR ImagingStudy from DICOM metadata."""
        _ = api_key
        metadata = self.extract_metadata(file)

        study_uid = self._validate_uid(
            str(metadata.get('StudyInstanceUID') or '')
        )
        series_uid = self._validate_uid(
            str(metadata.get('SeriesInstanceUID') or '')
        )

        imaging_study: Dict[str, Any] = {
            'resourceType': 'ImagingStudy',
            'status': 'available',
            'uid': study_uid,
            'series': [{'uid': series_uid}],
        }

        findings_text = str(metadata.get('SeriesDescription') or '').strip()
        patient_name = str(metadata.get('PatientName') or '').strip()
        patient_id = str(metadata.get('PatientID') or '').strip()

        # Only include description if not PHI-like or sentinel
        if include_series_description and findings_text:
            if findings_text.lower() != 'unknown' and findings_text not in (
                patient_name,
                patient_id,
            ):
                imaging_study['series'][0]['description'] = findings_text

        if subject_reference:
            imaging_study['subject'] = {'reference': subject_reference}

        return imaging_study

    @staticmethod
    def _load_dicom(file: FileInput, stop_before_pixels: bool = False) -> Any:
        """Load DICOM file safely from path, bytes, or file-like object."""
        try:
            import pydicom

            from pydicom.errors import InvalidDicomError
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                'pydicom is required for DICOM extraction. '
                'Install with "pip install sdx[dicom]" or add pydicom '
                'to your environment.'
            ) from e

        try:
            if isinstance(file, (str, Path)):
                return pydicom.dcmread(
                    str(file), stop_before_pixels=stop_before_pixels
                )
            if isinstance(file, bytes):
                return pydicom.dcmread(
                    io.BytesIO(file), stop_before_pixels=stop_before_pixels
                )
            return pydicom.dcmread(file, stop_before_pixels=stop_before_pixels)
        except (InvalidDicomError, FileNotFoundError, OSError) as e:
            raise ValueError(f'Invalid DICOM file: {e}') from e

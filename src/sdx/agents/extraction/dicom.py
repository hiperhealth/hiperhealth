"""DICOM extraction and FHIR ImagingStudy conversion utilities."""

import io

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
        """Return a JSON-safe string for a DICOM attribute.

        pydicom value types (e.g. PersonName) may not be JSON-serializable, so
        convert to str when present and return a default otherwise.
        """
        val = getattr(ds, name, None)
        if val is None or val == '':
            return default
        return str(val)

    @staticmethod
    def _redact_metadata(metadata: Dict[str, Any]) -> Dict[str, str]:
        """Return a copy of metadata with common PHI keys removed and.

        values stringified.
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
        }
        return {k: str(v) for k, v in metadata.items() if k not in phi_keys}

    @staticmethod
    def extract_metadata(file: FileInput) -> Dict[str, Any]:
        """Extract relevant metadata fields from a DICOM file.

        Values are normalized to strings where appropriate.
        """
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

        return metadata

    def extract_fhir(
        self,
        file: FileInput,
        api_key: str | None = None,
        subject_reference: str | None = None,
        include_series_description: bool = False,
    ) -> Dict[str, Any]:
        """Extract DICOM metadata and generate a minimal FHIR ImagingStudy.

        If an API key is provided this method could call an external AI service
        to enrich findings. If no key is available, proceed in offline mode and
        return a basic ImagingStudy resource constructed from metadata.
        """
        metadata = self.extract_metadata(file)
        findings_text = str(
            metadata.get('SeriesDescription', '') or ''
        ).strip()

        # Only require a key when we actually perform a remote AI call. For now
        # proceed in offline mode if no key is provided.
        # reference api_key to avoid unused-variable tooling warnings
        if api_key:
            # api_key would be used by a remote enrichment call
            pass
        # Redact PHI and stringify remaining values
        safe_metadata = DicomExtractor._redact_metadata(metadata)

        # If a remote AI call were implemented, it would be performed here and
        # would require `key`. Since that's not implemented, return a minimal
        # ImagingStudy resource constructed locally.
        series: list[Dict[str, str]] = []
        imaging_study: Dict[str, Any] = {
            'resourceType': 'ImagingStudy',
            'status': 'available',
            'series': series,
        }

        if subject_reference:
            imaging_study['subject'] = {'reference': subject_reference}

        if include_series_description and findings_text:
            series.append({'description': findings_text})

        # attach a short study-level summary (non-PHI)
        if safe_metadata:
            imaging_study['description'] = str(safe_metadata)

        return imaging_study

    @staticmethod
    def _load_dicom(
        file: FileInput,
        stop_before_pixels: bool = False,
    ) -> Any:
        """Load DICOM file safely from path, bytes, or file-like object.

        pydicom is imported lazily so the module can be used without pydicom
        being installed. If pydicom is missing, a ModuleNotFoundError will be
        raised when DICOM functionality is accessed.
        """
        try:
            import pydicom

            from pydicom.errors import InvalidDicomError
        except ModuleNotFoundError as e:
            raise ModuleNotFoundError(
                'pydicom is required for DICOM extraction. '
                'Install with "pip install sdx[dicom]" or add pydicom to your '
                'environment.'
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

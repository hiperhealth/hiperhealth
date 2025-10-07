"""DICOM data module for extracting metadata and generating FHIR ImagingStudy.

This module provides functionality to extract metadata from DICOM files
and convert it into FHIR ImagingStudy resources.
"""

from __future__ import annotations

import os

from abc import ABC, abstractmethod
from pathlib import Path
from typing import IO, Any, Dict, Union, cast

import pydicom

from anamnesisai import AnamnesisAI
from pydicom.errors import InvalidDicomError

FileInput = Union[str, Path, IO[bytes], bytes]


# Exceptions
class DICOMExtractorError(Exception):
    """Base exception for DICOM extraction errors."""

    ...


class FileNotDICOMError(DICOMExtractorError):
    """Raised when file is not a valid DICOM."""

    ...


class DICOMExtractor(ABC):
    """Base class for DICOM extraction."""

    @abstractmethod
    def extract_metadata(self, file: FileInput) -> Dict[str, Any]:
        """Extract metadata from DICOM file."""
        raise NotImplementedError


class DICOMFileExtractor(DICOMExtractor):
    """DICOM file extractor implementation."""

    def extract_metadata(self, file: FileInput) -> Dict[str, Any]:
        """Read DICOM file and extract key metadata."""
        ds: pydicom.Dataset

        try:
            if isinstance(file, (str, Path)):
                ds = pydicom.dcmread(file)
            elif isinstance(file, bytes):
                ds = pydicom.dcmread(cast(IO[bytes], file))
            else:
                ds = pydicom.dcmread(file)
        except (InvalidDicomError, FileNotFoundError) as e:
            raise FileNotDICOMError(f'Invalid DICOM file: {e}') from e

        metadata: Dict[str, Any] = {}

        # Patient info
        metadata['PatientID'] = getattr(ds, 'PatientID', 'Unknown')
        metadata['PatientSex'] = getattr(ds, 'PatientSex', 'Unknown')
        metadata['PatientBirthDate'] = getattr(
            ds, 'PatientBirthDate', 'Unknown'
        )

        # Study info
        metadata['StudyDate'] = getattr(ds, 'StudyDate', 'Unknown')
        metadata['StudyTime'] = getattr(ds, 'StudyTime', 'Unknown')
        metadata['StudyDescription'] = getattr(
            ds, 'StudyDescription', 'Unknown'
        )
        metadata['Modality'] = getattr(ds, 'Modality', 'Unknown')
        metadata['Manufacturer'] = getattr(ds, 'Manufacturer', 'Unknown')

        # Series info
        metadata['SeriesDescription'] = getattr(
            ds, 'SeriesDescription', 'Unknown'
        )
        metadata['SeriesNumber'] = getattr(ds, 'SeriesNumber', 'Unknown')

        return metadata

    def extract_fhir(
        self, file: FileInput, api_key: str | None = None
    ) -> Dict[str, Any]:
        """Extract DICOM metadata and generate FHIR ImagingStudy resource.

        Uses AnamnesisAI for FHIR conversion.
        """
        metadata = self.extract_metadata(file)
        findings_text = metadata.get('SeriesDescription', '')

        key = api_key or os.environ.get('OPENAI_API_KEY')
        if not key:
            raise EnvironmentError(
                'Missing OpenAI API key for FHIR conversion'
            )

        anaai = AnamnesisAI(backend='openai', api_key=key)
        resources = anaai.extract_fhir(findings_text)

        result: Dict[str, Any] = {
            res.__class__.__name__: res.model_dump() for res in resources[0]
        }

        return result


def get_dicom_extractor() -> DICOMFileExtractor:
    """Return an instance of DICOMFileExtractor."""
    return DICOMFileExtractor()

"""DICOM data module for extracting metadata and generating FHIR ImagingStudy."""

from __future__ import annotations

import io
from pathlib import Path
from typing import Union, Dict, Any, List

import pydicom
from pydicom.errors import InvalidDicomError
from PIL import Image

from anamnesisai import AnamnesisAI
from sdx.utils import make_json_serializable

FileInput = Union[str, Path, io.BytesIO]

class DICOMExtractorError(Exception):
    """Base exception for DICOM extraction errors."""
    ...


class FileNotDICOMError(DICOMExtractorError):
    """Raised when file is not a valid DICOM."""
    ...


class DICOMDataExtractor:
    """Extractor for DICOM metadata and FHIR ImagingStudy."""

    def extract_metadata(self, file: FileInput) -> Dict[str, Any]:
        """Extract DICOM metadata from a file or in-memory object."""
        ds = self._load_dicom(file)
        metadata: Dict[str, Any] = {}

        # Patient info
        metadata["PatientName"] = str(getattr(ds, "PatientName", "Unknown"))
        metadata["PatientID"] = getattr(ds, "PatientID", "Unknown")
        metadata["PatientSex"] = getattr(ds, "PatientSex", "Unknown")
        metadata["PatientBirthDate"] = getattr(ds, "PatientBirthDate", "Unknown")

        # Study info
        metadata["StudyDate"] = getattr(ds, "StudyDate", "Unknown")
        metadata["StudyTime"] = getattr(ds, "StudyTime", "Unknown")
        metadata["StudyDescription"] = getattr(ds, "StudyDescription", "Unknown")
        metadata["Modality"] = getattr(ds, "Modality", "Unknown")
        metadata["Manufacturer"] = getattr(ds, "Manufacturer", "Unknown")
        metadata["InstitutionName"] = getattr(ds, "InstitutionName", "Unknown")

        # Image info
        metadata["Rows"] = getattr(ds, "Rows", None)
        metadata["Columns"] = getattr(ds, "Columns", None)
        metadata["PixelSpacing"] = getattr(ds, "PixelSpacing", None)
        metadata["ImageType"] = getattr(ds, "ImageType", None)
        metadata["SeriesDescription"] = getattr(ds, "SeriesDescription", "")

        return metadata

    def extract_image(self, file: FileInput) -> Image.Image | None:
        """Extract pixel data as PIL Image if present."""
        ds = self._load_dicom(file)
        if not hasattr(ds, "PixelData"):
            return None

        try:
            arr = ds.pixel_array
            img = Image.fromarray(arr)
            return img
        except Exception:
            return None

    def extract_fhir(self, file: FileInput, api_key: str | None = None) -> Dict[str, Any]:
        """
        Extract DICOM metadata and generate FHIR ImagingStudy resource using AnamnesisAI.
        """
        metadata = self.extract_metadata(file)
        findings_text = metadata.get("SeriesDescription", "")

        key = api_key or None
        if not key:
            raise EnvironmentError("Missing OpenAI API key for FHIR conversion")

        anaai = AnamnesisAI(backend="openai", api_key=key)

        # Convert DICOM metadata + optional findings to FHIR ImagingStudy
        resources = anaai.extract_fhir(findings_text or str(metadata))
        fhir_data: Dict[str, Any] = make_json_serializable(
            {res.__class__.__name__: res.model_dump() for res in resources[0]}
        )
        return fhir_data

    def _load_dicom(self, file: FileInput) -> pydicom.dataset.FileDataset:
        """Load DICOM file from path or in-memory bytes."""
        try:
            if isinstance(file, (str, Path)):
                ds = pydicom.dcmread(str(file))
            elif isinstance(file, io.BytesIO):
                file.seek(0)
                ds = pydicom.dcmread(file)
            else:
                raise TypeError("Unsupported file type for DICOM extraction.")
        except InvalidDicomError as e:
            raise FileNotDICOMError(f"File is not a valid DICOM: {e}") from e
        return ds

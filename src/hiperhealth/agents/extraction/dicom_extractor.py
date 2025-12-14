"""DICOM medical report extractor."""

from __future__ import annotations

import io
from typing import Any, Dict, Optional
from pathlib import Path

import numpy as np
import pytesseract
import pydicom
from PIL import Image
from pydicom.dataset import Dataset

from .medical_reports import MedicalReportExtractorError, TextExtractionError


class DICOMTextExtractor:
    """Extract relevant information from DICOM files."""

    @staticmethod
    def extract_metadata(ds: Dataset) -> Dict[str, Any]:
        """Extract clinically relevant metadata."""
        return {
            "PatientName": str(ds.get("PatientName", "")),
            "PatientID": ds.get("PatientID"),
            "PatientSex": ds.get("PatientSex"),
            "PatientBirthDate": ds.get("PatientBirthDate"),
            "StudyDate": ds.get("StudyDate"),
            "StudyDescription": ds.get("StudyDescription"),
            "Modality": ds.get("Modality"),
            "BodyPartExamined": ds.get("BodyPartExamined"),
            "InstitutionName": ds.get("InstitutionName"),
            "ReferringPhysicianName": str(ds.get("ReferringPhysicianName", "")),
        }

    @staticmethod
    def extract_text_from_pixels(ds: Dataset) -> Optional[str]:
        """OCR burned-in text from DICOM pixel data if present."""
        if not hasattr(ds, "PixelData"):
            return None

        try:
            pixel_array = ds.pixel_array
            if pixel_array.ndim > 2:
                pixel_array = pixel_array[:, :, 0]

            img = Image.fromarray(np.uint8((pixel_array / pixel_array.max()) * 255))
            text = pytesseract.image_to_string(img)
            return text.strip() or None
        except Exception:
            return None

    @classmethod
    def extract_text(cls, source: str | Path | io.BytesIO) -> str:
        """Extract metadata + OCR text from DICOM."""
        # Convert Path to str
        if isinstance(source, Path):
            source = str(source)
        # Wrap IO[bytes] streams that are not BytesIO into BytesIO
        elif hasattr(source, "read") and not isinstance(source, io.BytesIO):
            source = io.BytesIO(source.read())
            source.seek(0)

        try:
            ds = pydicom.dcmread(source)
        except Exception as e:
            raise MedicalReportExtractorError(f"Failed to read DICOM file: {e}") from e

        metadata = cls.extract_metadata(ds)
        ocr_text = cls.extract_text_from_pixels(ds)

        combined_text = "\n".join(f"{k}: {v}" for k, v in metadata.items() if v)

        if ocr_text:
            combined_text += "\n\nOCR Text:\n" + ocr_text

        if not combined_text.strip():
            raise TextExtractionError("No extractable data in DICOM")

        return combined_text

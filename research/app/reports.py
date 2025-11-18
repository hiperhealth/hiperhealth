"""Helper functions for managing and processing medical reports."""

import io
import json

from typing import List, Optional, Tuple

from fastapi import UploadFile
from sdx.agents.extraction.medical_reports import (
    MedicalReportExtractorError,
    MedicalReportFileExtractor,
)


def load_fhir_reports(consultation) -> List[dict]:
    """Load and deserialize FHIR reports from consultation."""
    if consultation.previous_tests:
        try:
            reports = json.loads(consultation.previous_tests)
            if isinstance(reports, str):
                reports = json.loads(reports)
            return reports
        except Exception as e:
            print(f'Error loading fhir_reports: {e}')
            return []
    return []


def save_fhir_reports(consultation, reports: List[dict], repo):
    """Serialize and save FHIR reports to consultation."""
    try:
        json_data = json.dumps(reports)
        consultation.previous_tests = json_data
        repo.db.commit()
        print(f'Saved {len(reports)} reports')
    except Exception as e:
        raise ValueError(f'Failed to save reports: {e}')


def validate_report_file(
    report: UploadFile,
    seen_filenames: set,
    extractor: MedicalReportFileExtractor,
) -> Tuple[bool, Optional[str]]:
    """Validate uploaded report file."""
    filename_lower = report.filename.lower()

    if filename_lower in seen_filenames:
        return (
            False,
            f'File named "{report.filename}" has already been uploaded',
        )

    if report.content_type not in extractor.allowed_mimetypes or not any(
        filename_lower.endswith(f'.{ext}')
        for ext in extractor.allowed_extensions
    ):
        return (
            False,
            'Only PDF, PNG, JPEG, JPG files are allowed as Medical Reports',
        )

    return True, None


async def process_uploaded_reports(
    reports: List[UploadFile],
    seen_filenames: set,
    extractor: MedicalReportFileExtractor,
) -> Tuple[List[dict], Optional[str]]:
    """Process uploaded medical reports and extract FHIR data."""
    fhir_reports = []

    for report in reports:
        if not report.filename:
            continue

        valid, error_msg = validate_report_file(
            report, seen_filenames, extractor
        )
        if not valid:
            return [], error_msg

        try:
            data = await report.read()
            fhir = extractor.extract_report_data(io.BytesIO(data))
            if isinstance(fhir, dict):
                fhir['filename'] = report.filename
            fhir_reports.append(fhir)
            seen_filenames.add(report.filename.lower())
        except MedicalReportExtractorError as e:
            return [], f'Error extracting report {report.filename}: {e}'
        except Exception as e:
            return [], f'Unexpected error processing {report.filename}: {e}'

    return fhir_reports, None

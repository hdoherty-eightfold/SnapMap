"""
CSV Validator Service
Robust validation for CSV files against Eightfold schemas
- Schema-based header validation with typo detection
- Data quality checks (invalid characters, proper formatting)
- Required field validation
- Type validation
"""

import pandas as pd
import re
from typing import List, Dict, Tuple, Any, Optional
from difflib import SequenceMatcher
try:
    from Levenshtein import distance as levenshtein_distance
    HAS_LEVENSHTEIN = True
except ImportError:
    HAS_LEVENSHTEIN = False

from app.services.schema_manager import get_schema_manager


class ValidationIssue:
    """Represents a validation issue found in the CSV"""

    def __init__(
        self,
        severity: str,  # 'critical', 'warning', 'info'
        issue_type: str,
        field: str,
        description: str,
        affected_rows: Optional[int] = None,
        suggestion: Optional[str] = None
    ):
        self.severity = severity
        self.issue_type = issue_type
        self.field = field
        self.description = description
        self.affected_rows = affected_rows
        self.suggestion = suggestion

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "severity": self.severity,
            "type": self.issue_type,
            "field": self.field,
            "description": self.description,
            "affected_rows": self.affected_rows or "all",
            "suggestion": self.suggestion
        }


class CSVValidator:
    """
    Validates CSV files against Eightfold schemas

    Features:
    - Header validation with fuzzy matching for typos
    - Required field checks
    - Data type validation
    - Data quality checks (invalid characters, formatting)
    - CSV structure validation
    """

    def __init__(self):
        self.schema_manager = get_schema_manager()

    def validate_file(
        self,
        df: pd.DataFrame,
        entity_name: str,
        filename: str
    ) -> Tuple[bool, List[ValidationIssue]]:
        """
        Validate CSV file against schema

        Args:
            df: Pandas DataFrame
            entity_name: Target entity type (e.g., 'employee')
            filename: Original filename for context

        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []

        # Get schema
        try:
            schema = self.schema_manager.get_schema(entity_name)
            # Convert Pydantic model to dict if needed
            if hasattr(schema, 'model_dump'):
                schema = schema.model_dump()
            elif hasattr(schema, 'dict'):
                schema = schema.dict()
        except Exception as e:
            issues.append(ValidationIssue(
                severity="critical",
                issue_type="schema_error",
                field="",
                description=f"Unable to load schema for '{entity_name}': {str(e)}"
            ))
            return False, issues

        # 1. Validate CSV structure
        issues.extend(self._validate_csv_structure(df, filename))

        # 2. Validate headers
        header_issues, header_mapping = self._validate_headers(df, schema)
        issues.extend(header_issues)

        # 3. Check required fields
        issues.extend(self._check_required_fields(df, schema, header_mapping))

        # 4. Validate data types and quality
        issues.extend(self._validate_data_quality(df, schema, header_mapping))

        # Determine if validation passed
        has_critical = any(issue.severity == "critical" for issue in issues)
        is_valid = not has_critical

        return is_valid, issues

    def _validate_csv_structure(
        self,
        df: pd.DataFrame,
        filename: str
    ) -> List[ValidationIssue]:
        """Validate basic CSV structure"""
        issues = []

        # Check if DataFrame is empty
        if df.empty:
            issues.append(ValidationIssue(
                severity="critical",
                issue_type="empty_file",
                field="",
                description=f"File '{filename}' is empty or has no data rows"
            ))
            return issues

        # Check for unnamed columns
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            issues.append(ValidationIssue(
                severity="warning",
                issue_type="unnamed_columns",
                field=", ".join(unnamed_cols),
                description=f"File has {len(unnamed_cols)} unnamed columns, likely due to trailing commas in header row"
            ))

        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            issues.append(ValidationIssue(
                severity="critical",
                issue_type="duplicate_columns",
                field=", ".join(set(duplicate_cols)),
                description=f"Duplicate column names found: {', '.join(set(duplicate_cols))}"
            ))

        # Check for completely empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            issues.append(ValidationIssue(
                severity="info",
                issue_type="empty_columns",
                field=", ".join(empty_cols),
                description=f"Columns with no data: {', '.join(empty_cols)}"
            ))

        return issues

    def _validate_headers(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any]
    ) -> Tuple[List[ValidationIssue], Dict[str, str]]:
        """
        Validate headers against schema with fuzzy matching

        Returns:
            Tuple of (issues, mapping of source_column -> target_field)
        """
        issues = []
        header_mapping = {}

        # Get expected fields from schema
        expected_fields = {field['name']: field for field in schema['fields']}
        source_headers = [str(col).strip() for col in df.columns]

        # Find missing required fields
        required_fields = [
            field['name'] for field in schema['fields']
            if field.get('required', False)
        ]

        # Try to match each source header to a target field
        matched_targets = set()

        for source_header in source_headers:
            # Try exact match (case-insensitive)
            exact_match = None
            for target_field in expected_fields.keys():
                if source_header.upper() == target_field.upper():
                    exact_match = target_field
                    break

            if exact_match:
                header_mapping[source_header] = exact_match
                matched_targets.add(exact_match)
            else:
                # Try fuzzy match for potential typos
                best_match, confidence = self._find_best_match(
                    source_header,
                    list(expected_fields.keys())
                )

                if best_match and confidence > 0.8:  # High confidence threshold
                    issues.append(ValidationIssue(
                        severity="warning",
                        issue_type="misspelled_header",
                        field=source_header,
                        description=f"Header '{source_header}' appears to be a misspelling of '{best_match}'",
                        suggestion=f"Rename '{source_header}' to '{best_match}'"
                    ))
                    # Still add to mapping with the match
                    header_mapping[source_header] = best_match
                    matched_targets.add(best_match)
                elif best_match and confidence > 0.6:  # Medium confidence
                    issues.append(ValidationIssue(
                        severity="info",
                        issue_type="possible_typo",
                        field=source_header,
                        description=f"Header '{source_header}' might be related to '{best_match}' (similarity: {confidence:.0%})",
                        suggestion=f"Consider if '{source_header}' should be '{best_match}'"
                    ))
                else:
                    # Unknown header
                    issues.append(ValidationIssue(
                        severity="info",
                        issue_type="unknown_header",
                        field=source_header,
                        description=f"Header '{source_header}' does not match any expected field"
                    ))

        # Check for missing required fields
        for required_field in required_fields:
            if required_field not in matched_targets:
                issues.append(ValidationIssue(
                    severity="critical",
                    issue_type="missing_required_field",
                    field=required_field,
                    description=f"Required field '{required_field}' is missing from the file"
                ))

        return issues, header_mapping

    def _check_required_fields(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        header_mapping: Dict[str, str]
    ) -> List[ValidationIssue]:
        """Check if required fields have data"""
        issues = []

        required_fields = [
            field['name'] for field in schema['fields']
            if field.get('required', False)
        ]

        # Check each required field
        for target_field in required_fields:
            # Find source column that maps to this field
            source_col = None
            for src, tgt in header_mapping.items():
                if tgt == target_field:
                    source_col = src
                    break

            if source_col and source_col in df.columns:
                # Check for null/empty values
                null_count = df[source_col].isna().sum()
                empty_count = (df[source_col].astype(str).str.strip() == '').sum()
                total_invalid = null_count + empty_count

                if total_invalid > 0:
                    issues.append(ValidationIssue(
                        severity="critical",
                        issue_type="missing_required_data",
                        field=source_col,
                        description=f"Required field '{source_col}' has {total_invalid} empty/null values",
                        affected_rows=int(total_invalid)
                    ))

        return issues

    def _validate_data_quality(
        self,
        df: pd.DataFrame,
        schema: Dict[str, Any],
        header_mapping: Dict[str, str]
    ) -> List[ValidationIssue]:
        """Validate data quality and types"""
        issues = []

        for source_col, target_field in header_mapping.items():
            if source_col not in df.columns:
                continue

            # Get field definition from schema
            field_def = None
            for field in schema['fields']:
                if field['name'] == target_field:
                    field_def = field
                    break

            if not field_def:
                continue

            series = df[source_col]
            field_type = field_def.get('type', 'string')

            # Validate based on type
            if field_type == 'email':
                issues.extend(self._validate_email_field(source_col, series))
            elif field_type == 'date':
                issues.extend(self._validate_date_field(source_col, series))
            elif field_type == 'number' or field_type == 'integer':
                issues.extend(self._validate_numeric_field(source_col, series))

            # Check for invalid characters
            issues.extend(self._check_invalid_characters(source_col, series))

            # Check max length if specified
            if field_def.get('max_length'):
                issues.extend(
                    self._check_max_length(source_col, series, field_def['max_length'])
                )

        return issues

    def _validate_email_field(
        self,
        col_name: str,
        series: pd.Series
    ) -> List[ValidationIssue]:
        """Validate email addresses"""
        issues = []
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # Check non-null values
        non_null = series.dropna()
        if non_null.empty:
            return issues

        invalid = ~non_null.astype(str).str.match(email_pattern, na=False)
        invalid_count = invalid.sum()

        if invalid_count > 0:
            issues.append(ValidationIssue(
                severity="warning",
                issue_type="invalid_email",
                field=col_name,
                description=f"Field '{col_name}' has {invalid_count} invalid email addresses",
                affected_rows=int(invalid_count)
            ))

        return issues

    def _validate_date_field(
        self,
        col_name: str,
        series: pd.Series
    ) -> List[ValidationIssue]:
        """Validate date fields"""
        issues = []

        non_null = series.dropna()
        if non_null.empty:
            return issues

        # Try to parse as dates
        try:
            parsed = pd.to_datetime(non_null, errors='coerce')
            invalid_count = parsed.isna().sum()

            if invalid_count > 0:
                issues.append(ValidationIssue(
                    severity="warning",
                    issue_type="invalid_date",
                    field=col_name,
                    description=f"Field '{col_name}' has {invalid_count} values that cannot be parsed as dates",
                    affected_rows=int(invalid_count)
                ))
        except Exception as e:
            issues.append(ValidationIssue(
                severity="warning",
                issue_type="date_parse_error",
                field=col_name,
                description=f"Unable to validate dates in '{col_name}': {str(e)}"
            ))

        return issues

    def _validate_numeric_field(
        self,
        col_name: str,
        series: pd.Series
    ) -> List[ValidationIssue]:
        """Validate numeric fields"""
        issues = []

        non_null = series.dropna()
        if non_null.empty:
            return issues

        # Try to convert to numeric
        try:
            numeric = pd.to_numeric(non_null, errors='coerce')
            invalid_count = numeric.isna().sum()

            if invalid_count > 0:
                issues.append(ValidationIssue(
                    severity="warning",
                    issue_type="invalid_number",
                    field=col_name,
                    description=f"Field '{col_name}' has {invalid_count} non-numeric values",
                    affected_rows=int(invalid_count)
                ))
        except Exception:
            pass

        return issues

    def _check_invalid_characters(
        self,
        col_name: str,
        series: pd.Series
    ) -> List[ValidationIssue]:
        """Check for problematic characters in data"""
        issues = []

        non_null = series.dropna()
        if non_null.empty:
            return issues

        # Check for null bytes and control characters
        str_series = non_null.astype(str)
        has_nullbyte = str_series.str.contains('\x00', regex=False, na=False).any()
        has_control = str_series.str.contains(r'[\x00-\x08\x0B\x0C\x0E-\x1F]', regex=True, na=False).any()

        if has_nullbyte:
            issues.append(ValidationIssue(
                severity="warning",
                issue_type="null_bytes",
                field=col_name,
                description=f"Field '{col_name}' contains null bytes which may cause import issues"
            ))

        if has_control:
            issues.append(ValidationIssue(
                severity="info",
                issue_type="control_characters",
                field=col_name,
                description=f"Field '{col_name}' contains control characters"
            ))

        return issues

    def _check_max_length(
        self,
        col_name: str,
        series: pd.Series,
        max_length: int
    ) -> List[ValidationIssue]:
        """Check if values exceed maximum length"""
        issues = []

        non_null = series.dropna()
        if non_null.empty:
            return issues

        str_series = non_null.astype(str)
        too_long = str_series.str.len() > max_length
        too_long_count = too_long.sum()

        if too_long_count > 0:
            issues.append(ValidationIssue(
                severity="warning",
                issue_type="exceeds_max_length",
                field=col_name,
                description=f"Field '{col_name}' has {too_long_count} values exceeding max length of {max_length}",
                affected_rows=int(too_long_count)
            ))

        return issues

    def _find_best_match(
        self,
        source: str,
        targets: List[str]
    ) -> Tuple[Optional[str], float]:
        """
        Find best matching target for source string using fuzzy matching

        Returns:
            Tuple of (best_match, confidence_score)
        """
        if not targets:
            return None, 0.0

        source_upper = source.upper()
        best_match = None
        best_score = 0.0

        for target in targets:
            target_upper = target.upper()

            # Calculate similarity
            if HAS_LEVENSHTEIN:
                # Use Levenshtein distance if available (more accurate)
                max_len = max(len(source_upper), len(target_upper))
                if max_len == 0:
                    similarity = 1.0
                else:
                    dist = levenshtein_distance(source_upper, target_upper)
                    similarity = 1.0 - (dist / max_len)
            else:
                # Fall back to SequenceMatcher
                similarity = SequenceMatcher(None, source_upper, target_upper).ratio()

            if similarity > best_score:
                best_score = similarity
                best_match = target

        return best_match, best_score


# Singleton instance
_csv_validator = None


def get_csv_validator() -> CSVValidator:
    """Get singleton CSVValidator instance"""
    global _csv_validator
    if _csv_validator is None:
        _csv_validator = CSVValidator()
    return _csv_validator

"""
Basic CSV Structure Validator
Validates CSV structure without needing schema knowledge
Run at upload time before entity type is known
"""

import pandas as pd
from typing import List, Dict, Any


class BasicCSVIssue:
    """Represents a basic CSV structure issue"""

    def __init__(self, severity: str, description: str):
        self.severity = severity
        self.description = description

    def to_dict(self) -> Dict[str, Any]:
        return {
            "severity": self.severity,
            "description": self.description
        }


class BasicCSVValidator:
    """Validates basic CSV structure"""

    def validate_structure(
        self,
        df: pd.DataFrame,
        filename: str
    ) -> List[BasicCSVIssue]:
        """
        Validate basic CSV structure

        Args:
            df: Pandas DataFrame
            filename: Original filename

        Returns:
            List of issues found
        """
        issues = []

        # Check if DataFrame is empty
        if df.empty:
            issues.append(BasicCSVIssue(
                severity="critical",
                description=f"File '{filename}' is empty or has no data rows"
            ))
            return issues

        # Check for unnamed columns (trailing commas)
        unnamed_cols = [col for col in df.columns if str(col).startswith('Unnamed:')]
        if unnamed_cols:
            issues.append(BasicCSVIssue(
                severity="warning",
                description=f"File has {len(unnamed_cols)} unnamed columns. This usually indicates extra commas in the header row."
            ))

        # Check for duplicate column names
        duplicate_cols = df.columns[df.columns.duplicated()].tolist()
        if duplicate_cols:
            issues.append(BasicCSVIssue(
                severity="critical",
                description=f"Duplicate column names found: {', '.join(set(duplicate_cols))}"
            ))

        # Check for completely empty columns
        empty_cols = [col for col in df.columns if df[col].isna().all()]
        if empty_cols:
            issues.append(BasicCSVIssue(
                severity="warning",
                description=f"Found {len(empty_cols)} completely empty columns: {', '.join(empty_cols)}"
            ))

        # Check if all rows are empty
        if df.isna().all().all():
            issues.append(BasicCSVIssue(
                severity="critical",
                description="All columns in the file are empty"
            ))

        # Check for null bytes or problematic characters
        for col in df.columns:
            if df[col].dtype == 'object':  # String columns
                try:
                    has_nullbyte = df[col].astype(str).str.contains('\x00', regex=False, na=False).any()
                    if has_nullbyte:
                        issues.append(BasicCSVIssue(
                            severity="warning",
                            description=f"Column '{col}' contains null bytes which may cause processing issues"
                        ))
                        break  # Only report once
                except:
                    pass

        return issues


# Singleton
_basic_validator = None


def get_basic_csv_validator() -> BasicCSVValidator:
    """Get singleton BasicCSVValidator instance"""
    global _basic_validator
    if _basic_validator is None:
        _basic_validator = BasicCSVValidator()
    return _basic_validator

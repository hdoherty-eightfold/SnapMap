"""
Data Validation Service
Provides comprehensive data loss detection and validation
"""

import pandas as pd
from typing import List, Dict, Any, Optional, Tuple


class DataLossError(Exception):
    """Exception raised when data loss is detected"""

    def __init__(self, message: str, lost_rows: int, total_rows: int, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.lost_rows = lost_rows
        self.total_rows = total_rows
        self.details = details or {}
        super().__init__(self.message)


class DataValidator:
    """
    Validates data integrity throughout the ETL pipeline

    Features:
    - Row count validation (detect data loss)
    - Field completeness validation
    - Data quality checks
    - Detailed error reporting with row numbers
    """

    def validate_row_count(
        self,
        input_df: pd.DataFrame,
        output_df: pd.DataFrame,
        operation_name: str,
        allow_duplicates_removal: bool = False
    ) -> bool:
        """
        Validate that no rows were lost during processing

        Args:
            input_df: Input DataFrame
            output_df: Output DataFrame
            operation_name: Name of the operation for error messages
            allow_duplicates_removal: Whether to allow row count reduction due to deduplication

        Returns:
            True if validation passes

        Raises:
            DataLossError: If rows were lost unexpectedly
        """
        input_count = len(input_df)
        output_count = len(output_df)

        if input_count == output_count:
            return True

        if output_count > input_count:
            # More rows in output (unusual but not necessarily an error)
            return True

        # Data loss detected
        lost_count = input_count - output_count
        loss_percentage = (lost_count / input_count) * 100

        # Check if loss is due to duplicate removal
        if allow_duplicates_removal:
            return True

        # Identify which rows were lost
        lost_details = self._identify_lost_rows(input_df, output_df)

        error_msg = (
            f"Data loss detected in {operation_name}: "
            f"{lost_count} rows lost ({loss_percentage:.1f}%). "
            f"Input: {input_count} rows, Output: {output_count} rows."
        )

        raise DataLossError(
            message=error_msg,
            lost_rows=lost_count,
            total_rows=input_count,
            details=lost_details
        )

    def _identify_lost_rows(
        self,
        input_df: pd.DataFrame,
        output_df: pd.DataFrame
    ) -> Dict[str, Any]:
        """
        Identify which rows were lost and potential reasons

        Returns:
            Dictionary with details about lost rows
        """
        details = {
            "input_rows": len(input_df),
            "output_rows": len(output_df),
            "lost_count": len(input_df) - len(output_df),
            "potential_reasons": []
        }

        # Check for null values in critical columns
        null_counts = input_df.isnull().sum()
        if null_counts.any():
            details["potential_reasons"].append({
                "reason": "Null values present",
                "columns": null_counts[null_counts > 0].to_dict()
            })

        # Check for duplicate rows
        duplicate_count = input_df.duplicated().sum()
        if duplicate_count > 0:
            details["potential_reasons"].append({
                "reason": "Duplicate rows present",
                "duplicate_count": int(duplicate_count)
            })

        # Try to identify specific lost row indices
        # This is approximate - we check if the first few rows are preserved
        if len(output_df) > 0:
            try:
                # Compare first column values to estimate which rows remain
                first_col_input = input_df.iloc[:, 0].astype(str).tolist()
                first_col_output = output_df.iloc[:, 0].astype(str).tolist()

                missing_indices = []
                for idx, val in enumerate(first_col_input[:100]):  # Check first 100 rows
                    if val not in first_col_output:
                        missing_indices.append(idx)

                if missing_indices:
                    details["sample_missing_row_indices"] = missing_indices[:10]  # First 10
            except Exception:
                pass

        return details

    def validate_field_completeness(
        self,
        df: pd.DataFrame,
        required_fields: List[str],
        operation_name: str
    ) -> Tuple[bool, List[Dict[str, Any]]]:
        """
        Validate that required fields are present and non-empty

        Args:
            df: DataFrame to validate
            required_fields: List of required field names
            operation_name: Name of the operation for error messages

        Returns:
            Tuple of (is_valid, list of validation issues)
        """
        issues = []

        for field in required_fields:
            if field not in df.columns:
                issues.append({
                    "field": field,
                    "severity": "error",
                    "message": f"Required field '{field}' is missing",
                    "operation": operation_name
                })
            else:
                # Check for null/empty values
                null_count = df[field].isna().sum()
                if null_count > 0:
                    null_percentage = (null_count / len(df)) * 100
                    issues.append({
                        "field": field,
                        "severity": "warning",
                        "message": f"Field '{field}' has {null_count} null values ({null_percentage:.1f}%)",
                        "operation": operation_name,
                        "null_count": int(null_count)
                    })

        is_valid = not any(issue["severity"] == "error" for issue in issues)
        return is_valid, issues

    def validate_multi_value_fields(
        self,
        df: pd.DataFrame,
        multi_value_fields: List[str],
        separator: str = "||"
    ) -> Dict[str, Any]:
        """
        Validate multi-value fields with specific separator

        Args:
            df: DataFrame to validate
            multi_value_fields: List of field names that contain multi-value data
            separator: Expected separator (default: ||)

        Returns:
            Dictionary with validation results
        """
        results = {
            "has_multi_value_fields": False,
            "fields_analyzed": [],
            "total_multi_value_cells": 0
        }

        for field in multi_value_fields:
            if field not in df.columns:
                continue

            # Check how many cells contain the separator
            cells_with_separator = df[field].astype(str).str.contains(separator, regex=False).sum()

            if cells_with_separator > 0:
                results["has_multi_value_fields"] = True
                results["total_multi_value_cells"] += cells_with_separator

                # Sample some multi-value cells
                multi_value_samples = df[df[field].astype(str).str.contains(separator, regex=False)][field].head(3).tolist()

                results["fields_analyzed"].append({
                    "field_name": field,
                    "cells_with_separator": int(cells_with_separator),
                    "separator": separator,
                    "samples": multi_value_samples
                })

        return results


# Singleton instance
_data_validator = None


def get_data_validator() -> DataValidator:
    """Get singleton DataValidator instance"""
    global _data_validator
    if _data_validator is None:
        _data_validator = DataValidator()
    return _data_validator

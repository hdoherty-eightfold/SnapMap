"""
File Parser Service
Handles CSV and Excel file parsing
"""

import pandas as pd
from io import BytesIO
from typing import Dict, Tuple
import re


class FileParser:
    """Parse CSV and Excel files"""

    def parse_file(self, file_content: bytes, filename: str) -> pd.DataFrame:
        """
        Parse file content into DataFrame

        Args:
            file_content: File bytes
            filename: Original filename

        Returns:
            pandas DataFrame

        Raises:
            ValueError: If file format is unsupported or parsing fails
        """
        try:
            if filename.endswith('.csv'):
                return pd.read_csv(BytesIO(file_content))
            elif filename.endswith(('.xlsx', '.xls')):
                return pd.read_excel(BytesIO(file_content))
            else:
                raise ValueError(f"Unsupported file format. Please upload CSV or Excel files.")
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")

    def detect_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Detect data types for each column

        Returns dictionary mapping column names to type strings
        """
        types = {}

        for col in df.columns:
            # Get non-null sample
            sample = df[col].dropna().head(10)

            if sample.empty:
                types[col] = "string"
                continue

            # Check for email pattern
            if self._is_email_column(sample):
                types[col] = "email"
            # Check for date
            elif self._is_date_column(sample):
                types[col] = "date"
            # Check for numeric
            elif pd.api.types.is_numeric_dtype(sample):
                types[col] = "number"
            else:
                types[col] = "string"

        return types

    def _is_email_column(self, series: pd.Series) -> bool:
        """Check if series contains email addresses"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        try:
            # Check if most values match email pattern
            matches = series.astype(str).str.match(email_pattern)
            return matches.sum() / len(series) > 0.7
        except:
            return False

    def _is_date_column(self, series: pd.Series) -> bool:
        """Check if series contains dates"""
        try:
            # Try to parse as datetime
            pd.to_datetime(series, errors='coerce')
            # If most values parse successfully, it's a date
            parsed = pd.to_datetime(series, errors='coerce')
            return parsed.notna().sum() / len(series) > 0.7
        except:
            return False


# Singleton instance
_file_parser = None


def get_file_parser() -> FileParser:
    """Get singleton FileParser instance"""
    global _file_parser
    if _file_parser is None:
        _file_parser = FileParser()
    return _file_parser

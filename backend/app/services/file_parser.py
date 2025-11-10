"""
File Parser Service
Handles CSV and Excel file parsing
"""

import pandas as pd
from io import BytesIO
from typing import Dict, Tuple, Optional
import re
import chardet
import csv


class FileParser:
    """Parse CSV and Excel files"""

    def detect_file_format(self, file_content: bytes, filename: str) -> Dict:
        """
        Detect file format details including delimiter, encoding, headers

        Args:
            file_content: File bytes
            filename: Original filename

        Returns:
            Dictionary with format details
        """
        result = {
            "delimiter": None,
            "encoding": "utf-8",
            "has_header": True,
            "row_count": 0,
            "field_count": 0,
            "preview_fields": [],
            "special_characters_detected": [],
            "multi_value_fields": [],
            "suggested_entity": None
        }

        if filename.endswith(('.xlsx', '.xls')):
            # Excel files don't need delimiter detection
            try:
                df = pd.read_excel(BytesIO(file_content), nrows=10)
                result["field_count"] = len(df.columns)
                result["preview_fields"] = df.columns.tolist()

                # Get full row count
                df_full = pd.read_excel(BytesIO(file_content))
                result["row_count"] = len(df_full)

                # Detect multi-value fields
                for col in df.columns:
                    sample = df[col].dropna().head(5).astype(str)
                    if sample.str.contains(r'\|\|').any():
                        result["multi_value_fields"].append(col)

                # Detect special characters
                all_text = ' '.join(df.astype(str).values.flatten())
                special_chars = set(re.findall(r'[^\x00-\x7F]', all_text))
                result["special_characters_detected"] = list(special_chars)[:10]

            except Exception as e:
                pass

        elif filename.endswith('.csv'):
            # Detect encoding - try UTF-8 first
            try:
                file_content.decode('utf-8')
                result["encoding"] = 'utf-8'
            except UnicodeDecodeError:
                # Fall back to chardet
                detected = chardet.detect(file_content)
                result["encoding"] = detected['encoding'] or 'utf-8'

            # Try different delimiters - use Sniffer first, then fallback
            best_delimiter = ','
            max_columns = 0

            # First, try using csv.Sniffer on a sample (without ||)
            try:
                # Remove || sequences for delimiter detection as they're multi-value separators
                sample = file_content[:8192].decode(result["encoding"], errors='ignore')
                sample_clean = sample.replace('||', '__')
                sniffer = csv.Sniffer()
                dialect = sniffer.sniff(sample_clean, delimiters=',;|\t')
                best_delimiter = dialect.delimiter
                # Validate the sniffed delimiter
                df_test = pd.read_csv(BytesIO(file_content), delimiter=best_delimiter, encoding=result["encoding"], nrows=2)
                max_columns = len(df_test.columns)
            except Exception as e:
                # Fallback to manual detection
                delimiters = [',', ';', '|', '\t']

                for delim in delimiters:
                    try:
                        df = pd.read_csv(BytesIO(file_content), delimiter=delim, encoding=result["encoding"], nrows=5)
                        num_cols = len(df.columns)
                        # Check if this delimiter actually splits the data properly
                        # by ensuring we don't just have a single column with the full line
                        if num_cols > 1 and num_cols > max_columns:
                            max_columns = num_cols
                            best_delimiter = delim
                    except:
                        continue

            result["delimiter"] = best_delimiter

            try:
                # Special handling for pipe delimiter with || multi-value separator
                # Use a UTF-8 safe placeholder that won't corrupt multi-byte sequences
                if best_delimiter == '|':
                    # Use Unit Separator (U+001F) as placeholder - safe for UTF-8
                    placeholder = '\u001F'
                    temp_content = file_content.replace(b'||', placeholder.encode(result["encoding"]))

                    df = pd.read_csv(
                        BytesIO(temp_content),
                        sep=best_delimiter,
                        encoding=result["encoding"],
                        nrows=10,
                        engine='python',
                        on_bad_lines='warn',
                        skipinitialspace=True
                    )
                    df_full = pd.read_csv(
                        BytesIO(temp_content),
                        sep=best_delimiter,
                        encoding=result["encoding"],
                        engine='python',
                        on_bad_lines='warn',
                        skipinitialspace=True
                    )

                    # Restore || in the data
                    for col in df.columns:
                        df[col] = df[col].astype(str).str.replace(placeholder, '||', regex=False)
                    for col in df_full.columns:
                        df_full[col] = df_full[col].astype(str).str.replace(placeholder, '||', regex=False)
                else:
                    # Use C engine for better performance and handling of malformed CSV
                    df = pd.read_csv(
                        BytesIO(file_content),
                        sep=best_delimiter,
                        encoding=result["encoding"],
                        nrows=10,
                        on_bad_lines='warn'
                    )
                    df_full = pd.read_csv(
                        BytesIO(file_content),
                        sep=best_delimiter,
                        encoding=result["encoding"],
                        on_bad_lines='warn'
                    )

                result["field_count"] = len(df.columns)
                result["preview_fields"] = df.columns.tolist()
                result["row_count"] = len(df_full)

                # Detect multi-value fields (contains ||)
                for col in df.columns:
                    sample = df[col].dropna().head(5).astype(str)
                    if sample.str.contains(r'\|\|', regex=True).any():
                        result["multi_value_fields"].append(col)

                # Detect special characters
                all_text = ' '.join(df.astype(str).values.flatten())
                special_chars = set(re.findall(r'[^\x00-\x7F]', all_text))
                result["special_characters_detected"] = list(special_chars)[:10]

            except Exception as e:
                # If parsing fails, return what we have
                pass

        # Suggest entity type based on field names
        field_names_lower = [f.lower() for f in result["preview_fields"]]
        if any('candidate' in f or 'applicant' in f for f in field_names_lower):
            result["suggested_entity"] = "candidate"
        elif any('employee' in f or 'worker' in f for f in field_names_lower):
            result["suggested_entity"] = "employee"

        return result

    def parse_file(self, file_content: bytes, filename: str, delimiter: Optional[str] = None, encoding: Optional[str] = None) -> Tuple[pd.DataFrame, Dict]:
        """
        Parse file content into DataFrame

        Args:
            file_content: File bytes
            filename: Original filename
            delimiter: Optional delimiter override
            encoding: Optional encoding override

        Returns:
            Tuple of (pandas DataFrame, metadata dict)

        Raises:
            ValueError: If file format is unsupported or parsing fails
        """
        metadata = {
            "detected_delimiter": None,
            "detected_encoding": "utf-8"
        }

        try:
            if filename.endswith('.csv'):
                # Auto-detect encoding if not provided
                if not encoding:
                    # Try UTF-8 first as it's most common for modern files
                    try:
                        file_content.decode('utf-8')
                        encoding = 'utf-8'
                    except UnicodeDecodeError:
                        # Fall back to chardet if UTF-8 fails
                        detected = chardet.detect(file_content)
                        encoding = detected['encoding'] or 'utf-8'

                metadata["detected_encoding"] = encoding

                # Auto-detect delimiter if not provided
                if not delimiter:
                    # Try csv.Sniffer first
                    try:
                        sample = file_content[:8192].decode(encoding, errors='ignore')
                        sample_clean = sample.replace('||', '__')
                        sniffer = csv.Sniffer()
                        dialect = sniffer.sniff(sample_clean, delimiters=',;|\t')
                        delimiter = dialect.delimiter
                    except:
                        # Fallback to manual detection
                        delimiters = [',', ';', '|', '\t']
                        best_delimiter = ','
                        max_columns = 0

                        for delim in delimiters:
                            try:
                                df_test = pd.read_csv(
                                    BytesIO(file_content),
                                    delimiter=delim,
                                    encoding=encoding,
                                    nrows=5,
                                    engine='python'
                                )

                                if len(df_test.columns) > max_columns:
                                    max_columns = len(df_test.columns)
                                    best_delimiter = delim
                            except:
                                continue

                        delimiter = best_delimiter

                metadata["detected_delimiter"] = delimiter

                # Parse the full file with special handling for pipe delimiter
                if delimiter == '|':
                    # Use UTF-8 safe placeholder for || separator
                    placeholder = '\u001F'
                    temp_content = file_content.replace(b'||', placeholder.encode(encoding))
                    df = pd.read_csv(
                        BytesIO(temp_content),
                        sep=delimiter,
                        encoding=encoding,
                        engine='python',
                        on_bad_lines='warn',
                        skipinitialspace=True
                    )
                    # Restore || in all columns
                    for col in df.columns:
                        df[col] = df[col].astype(str).str.replace(placeholder, '||', regex=False)
                else:
                    # Use C engine for better performance and malformed CSV handling
                    df = pd.read_csv(
                        BytesIO(file_content),
                        delimiter=delimiter,
                        encoding=encoding,
                        on_bad_lines='warn'
                    )

                # Provide helpful error if parsing fails
                if df.empty or len(df.columns) == 1:
                    raise ValueError(
                        f"Could not parse file with {delimiter} delimiter. "
                        f"Detected {len(df.columns)} field(s). "
                        f"Please specify the correct delimiter or check file format."
                    )

                return df, metadata

            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(file_content))
                return df, metadata
            else:
                raise ValueError(
                    f"Unsupported file format: {filename.split('.')[-1]}. "
                    f"Supported formats: CSV (.csv), Excel (.xlsx, .xls)"
                )
        except ValueError:
            raise
        except UnicodeDecodeError as e:
            # Specific handling for character encoding issues
            raise ValueError(
                f"Character encoding issue detected at byte position {e.start}. "
                f"File contains characters incompatible with {metadata.get('detected_encoding', 'unknown')} encoding. "
                f"Supported encodings: UTF-8, Latin-1 (ISO-8859-1), Windows-1252. "
                f"Please convert the file to UTF-8 encoding."
            )
        except Exception as e:
            error_msg = str(e)
            # Provide specific error messages based on common issues
            if 'codec' in error_msg.lower() or 'decode' in error_msg.lower():
                raise ValueError(
                    f"Character encoding issue detected. "
                    f"Detected encoding: {metadata.get('detected_encoding', 'unknown')}. "
                    f"Supported encodings: UTF-8, Latin-1, Windows-1252. "
                    f"Try saving the file as UTF-8 or specify the correct encoding."
                )
            elif 'delimiter' in error_msg.lower() or 'separator' in error_msg.lower():
                raise ValueError(
                    f"Delimiter detection failed. Attempted delimiter: '{delimiter}'. "
                    f"Supported delimiters: comma (,), pipe (|), tab (\\t), semicolon (;). "
                    f"Please check the file format and specify the correct delimiter."
                )
            else:
                raise ValueError(f"Error parsing file: {error_msg}")

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

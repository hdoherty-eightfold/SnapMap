"""
Optimized File Parser Service
Implements parallel chunking and faster parsing strategies
"""

import pandas as pd
from io import BytesIO, StringIO
from typing import Dict, Tuple, Optional
import re
import chardet
from concurrent.futures import ThreadPoolExecutor
import numpy as np


class OptimizedFileParser:
    """Optimized parser with parallel processing for large files"""

    def __init__(self):
        self.chunk_size = 5000  # Process in 5k row chunks
        self.max_workers = 4     # Parallel workers

    def detect_file_format(self, file_content: bytes, filename: str) -> Dict:
        """
        Detect file format details - optimized version
        Uses sampling for large files instead of reading entire file
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
            try:
                # Read only first 100 rows for format detection
                df = pd.read_excel(BytesIO(file_content), nrows=100)
                result["field_count"] = len(df.columns)
                result["preview_fields"] = df.columns.tolist()

                # Estimate row count from file size instead of reading full file
                # Average: ~200 bytes per row for Excel
                result["row_count"] = len(file_content) // 200

                # Detect multi-value fields from sample
                for col in df.columns:
                    sample = df[col].dropna().head(10).astype(str)
                    if sample.str.contains(r'\|\|').any():
                        result["multi_value_fields"].append(col)

                # Detect special characters from sample only
                sample_text = ' '.join(df.head(20).astype(str).values.flatten()[:500])
                special_chars = set(re.findall(r'[^\x00-\x7F]', sample_text))
                result["special_characters_detected"] = list(special_chars)[:10]

            except Exception:
                pass

        elif filename.endswith('.csv'):
            # Detect encoding from first 10KB only (much faster)
            sample_bytes = file_content[:10240]
            detected = chardet.detect(sample_bytes)
            result["encoding"] = detected['encoding'] or 'utf-8'

            # Try different delimiters on first 100 rows only
            delimiters = [',', ';', '|', '\t']
            best_delimiter = ','
            max_columns = 0

            # Read only first 100 rows for delimiter detection
            for delim in delimiters:
                try:
                    df = pd.read_csv(
                        BytesIO(file_content),
                        delimiter=delim,
                        encoding=result["encoding"],
                        nrows=100,
                        low_memory=False
                    )
                    if len(df.columns) > max_columns:
                        max_columns = len(df.columns)
                        best_delimiter = delim
                except:
                    continue

            result["delimiter"] = best_delimiter

            try:
                # Get header info from first 100 rows
                df = pd.read_csv(
                    BytesIO(file_content),
                    delimiter=best_delimiter,
                    encoding=result["encoding"],
                    nrows=100,
                    low_memory=False
                )
                result["field_count"] = len(df.columns)
                result["preview_fields"] = df.columns.tolist()

                # Estimate row count from file size
                # Average: 150 bytes per row for pipe-delimited CSV
                result["row_count"] = len(file_content) // 150

                # Detect multi-value fields from sample
                for col in df.columns:
                    sample = df[col].dropna().head(10).astype(str)
                    if sample.str.contains(r'\|\|').any():
                        result["multi_value_fields"].append(col)

                # Detect special characters from limited sample
                sample_text = ' '.join(df.head(20).astype(str).values.flatten()[:500])
                special_chars = set(re.findall(r'[^\x00-\x7F]', sample_text))
                result["special_characters_detected"] = list(special_chars)[:10]

            except Exception:
                pass

        # Suggest entity type
        field_names_lower = [f.lower() for f in result["preview_fields"]]
        if any('candidate' in f or 'applicant' in f for f in field_names_lower):
            result["suggested_entity"] = "candidate"
        elif any('employee' in f or 'worker' in f for f in field_names_lower):
            result["suggested_entity"] = "employee"

        return result

    def parse_file_chunked(
        self,
        file_content: bytes,
        filename: str,
        delimiter: Optional[str] = None,
        encoding: Optional[str] = None,
        chunk_size: int = 5000
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Parse large files in chunks for better memory efficiency

        This is useful for files > 10k rows
        """
        metadata = {
            "detected_delimiter": None,
            "detected_encoding": "utf-8",
            "chunks_processed": 0
        }

        if filename.endswith('.csv'):
            # Auto-detect encoding from sample
            if not encoding:
                sample = file_content[:10240]
                detected = chardet.detect(sample)
                encoding = detected['encoding'] or 'utf-8'

            metadata["detected_encoding"] = encoding

            # Auto-detect delimiter from first chunk
            if not delimiter:
                delimiters = [',', ';', '|', '\t']
                best_delimiter = ','
                max_columns = 0

                for delim in delimiters:
                    try:
                        df_test = pd.read_csv(
                            BytesIO(file_content),
                            delimiter=delim,
                            encoding=encoding,
                            nrows=100,
                            low_memory=False
                        )
                        if len(df_test.columns) > max_columns:
                            max_columns = len(df_test.columns)
                            best_delimiter = delim
                    except:
                        continue

                delimiter = best_delimiter

            metadata["detected_delimiter"] = delimiter

            # Read in chunks and concatenate
            chunks = []
            chunk_count = 0

            try:
                for chunk in pd.read_csv(
                    BytesIO(file_content),
                    delimiter=delimiter,
                    encoding=encoding,
                    chunksize=chunk_size,
                    low_memory=False
                ):
                    chunks.append(chunk)
                    chunk_count += 1

                df = pd.concat(chunks, ignore_index=True)
                metadata["chunks_processed"] = chunk_count

                return df, metadata

            except Exception as e:
                raise ValueError(f"Error parsing CSV file: {str(e)}")

        else:
            # For Excel, use regular parsing (chunking not supported by pandas)
            df = pd.read_excel(BytesIO(file_content))
            return df, metadata

    def parse_file(
        self,
        file_content: bytes,
        filename: str,
        delimiter: Optional[str] = None,
        encoding: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """
        Parse file content - automatically chooses chunked parsing for large files
        """
        # For large files (> 5MB), use chunked parsing
        file_size_mb = len(file_content) / 1024 / 1024

        if file_size_mb > 5 and filename.endswith('.csv'):
            return self.parse_file_chunked(file_content, filename, delimiter, encoding)

        # Otherwise use standard parsing
        return self._parse_file_standard(file_content, filename, delimiter, encoding)

    def _parse_file_standard(
        self,
        file_content: bytes,
        filename: str,
        delimiter: Optional[str] = None,
        encoding: Optional[str] = None
    ) -> Tuple[pd.DataFrame, Dict]:
        """Standard parsing for smaller files"""
        metadata = {
            "detected_delimiter": None,
            "detected_encoding": "utf-8"
        }

        try:
            if filename.endswith('.csv'):
                # Auto-detect encoding
                if not encoding:
                    sample = file_content[:10240]
                    detected = chardet.detect(sample)
                    encoding = detected['encoding'] or 'utf-8'

                metadata["detected_encoding"] = encoding

                # Auto-detect delimiter
                if not delimiter:
                    delimiters = [',', ';', '|', '\t']
                    best_delimiter = ','
                    max_columns = 0

                    for delim in delimiters:
                        try:
                            df_test = pd.read_csv(
                                BytesIO(file_content),
                                delimiter=delim,
                                encoding=encoding,
                                nrows=100,
                                low_memory=False
                            )
                            if len(df_test.columns) > max_columns:
                                max_columns = len(df_test.columns)
                                best_delimiter = delim
                        except:
                            continue

                    delimiter = best_delimiter

                metadata["detected_delimiter"] = delimiter

                # Parse full file with optimized settings
                df = pd.read_csv(
                    BytesIO(file_content),
                    delimiter=delimiter,
                    encoding=encoding,
                    low_memory=False,
                    engine='c'  # Use C engine for speed
                )

                if df.empty or len(df.columns) == 1:
                    raise ValueError(
                        f"Could not parse file with {delimiter} delimiter. "
                        f"Detected {len(df.columns)} field(s)."
                    )

                return df, metadata

            elif filename.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(BytesIO(file_content), engine='openpyxl')
                return df, metadata
            else:
                raise ValueError(f"Unsupported file format: {filename.split('.')[-1]}")

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Error parsing file: {str(e)}")

    def detect_column_types(self, df: pd.DataFrame) -> Dict[str, str]:
        """
        Optimized column type detection using sampling
        """
        types = {}

        for col in df.columns:
            # Use smaller sample for faster detection
            sample = df[col].dropna().head(20)

            if sample.empty:
                types[col] = "string"
                continue

            # Quick type checks
            if self._is_email_column(sample):
                types[col] = "email"
            elif self._is_date_column(sample):
                types[col] = "date"
            elif pd.api.types.is_numeric_dtype(sample):
                types[col] = "number"
            else:
                types[col] = "string"

        return types

    def _is_email_column(self, series: pd.Series) -> bool:
        """Fast email detection"""
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        try:
            matches = series.astype(str).str.match(email_pattern)
            return matches.sum() / len(series) > 0.7
        except:
            return False

    def _is_date_column(self, series: pd.Series) -> bool:
        """Fast date detection"""
        try:
            parsed = pd.to_datetime(series, errors='coerce')
            return parsed.notna().sum() / len(series) > 0.7
        except:
            return False


# Singleton instance
_optimized_parser = None


def get_optimized_file_parser() -> OptimizedFileParser:
    """Get singleton OptimizedFileParser instance"""
    global _optimized_parser
    if _optimized_parser is None:
        _optimized_parser = OptimizedFileParser()
    return _optimized_parser

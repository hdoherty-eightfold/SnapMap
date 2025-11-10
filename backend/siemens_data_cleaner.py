#!/usr/bin/env python3
"""
Siemens CSV Data Quality Cleaner
=================================

This script identifies and fixes data quality issues in Siemens candidate CSV files.

Issues Detected and Fixed:
1. Encoding issues: Non-ASCII characters (Latin-1, Turkish, Chinese, Arabic)
2. Quote patterns: Double single quotes ('') used instead of proper quoting
3. Custom delimiters: Percentage signs (%) used as field separators in HomeLocation
4. Phone number formatting: Leading quotes and inconsistent formats
5. Empty fields: Excessive empty values
6. Special characters: Control characters, newlines in fields
7. Data normalization: Standardized formats for consistent parsing

Author: Python Pro Agent
Date: 2025-11-07
"""

import csv
import re
import sys
import unicodedata
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional
from collections import Counter, defaultdict
from dataclasses import dataclass, field
import json


@dataclass
class DataQualityReport:
    """Container for data quality analysis results."""

    total_rows: int = 0
    total_fields: int = 0

    # Issue counters
    encoding_issues: Counter = field(default_factory=Counter)
    quote_issues: int = 0
    delimiter_issues: int = 0
    phone_format_issues: int = 0
    multiline_issues: int = 0
    empty_fields: Counter = field(default_factory=Counter)
    special_chars: Counter = field(default_factory=Counter)
    malformed_rows: List[int] = field(default_factory=list)

    # Patterns detected
    phone_patterns: Set[str] = field(default_factory=set)
    problematic_fields: Set[str] = field(default_factory=set)

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            'total_rows': self.total_rows,
            'total_fields': self.total_fields,
            'issues': {
                'encoding_issues': len(self.encoding_issues),
                'quote_issues': self.quote_issues,
                'delimiter_issues': self.delimiter_issues,
                'phone_format_issues': self.phone_format_issues,
                'multiline_issues': self.multiline_issues,
                'malformed_rows': len(self.malformed_rows)
            },
            'encoding_details': dict(self.encoding_issues.most_common(20)),
            'empty_fields': dict(self.empty_fields),
            'special_chars': {
                f'U+{ord(char):04X}': count
                for char, count in self.special_chars.most_common(30)
            },
            'problematic_fields': list(self.problematic_fields)
        }


class SiemensDataCleaner:
    """Main data cleaning class for Siemens CSV files."""

    # Characters that should be normalized or removed
    PROBLEMATIC_CHARS = {
        # Curly quotes to straight quotes
        '\u201c': '"',  # Left double quote
        '\u201d': '"',  # Right double quote
        '\u2018': "'",  # Left single quote
        '\u2019': "'",  # Right single quote

        # Dashes to hyphens
        '\u2013': '-',  # En dash
        '\u2014': '-',  # Em dash

        # Special spaces to regular space
        '\u00a0': ' ',  # Non-breaking space
        '\u2009': ' ',  # Thin space
        '\u200b': '',   # Zero-width space

        # Control characters to remove
        '\r': '',       # Carriage return (will be normalized separately)
        '\x00': '',     # Null byte
    }

    def __init__(self, input_file: Path, delimiter: str = '|'):
        """
        Initialize the cleaner.

        Args:
            input_file: Path to the input CSV file
            delimiter: CSV delimiter character (default: '|')
        """
        self.input_file = Path(input_file)
        self.delimiter = delimiter
        self.report = DataQualityReport()

    def analyze(self) -> DataQualityReport:
        """
        Analyze the CSV file for data quality issues without making changes.

        Returns:
            DataQualityReport with all identified issues
        """
        print(f"Analyzing file: {self.input_file}")
        print("=" * 80)

        with open(self.input_file, 'r', encoding='utf-8', errors='replace') as f:
            reader = csv.DictReader(f, delimiter=self.delimiter)

            # Store fieldnames
            if reader.fieldnames:
                self.report.total_fields = len(reader.fieldnames)

            for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is 1)
                self.report.total_rows += 1
                self._analyze_row(row_num, row)

        self._print_analysis_report()
        return self.report

    def _analyze_row(self, row_num: int, row: Dict[str, str]) -> None:
        """Analyze a single row for issues."""
        for field_name, value in row.items():
            if not value:
                self.report.empty_fields[field_name] += 1
                continue

            # Check for encoding issues
            for char in value:
                char_code = ord(char)
                if char_code > 127:  # Non-ASCII
                    self.report.special_chars[char] += 1

                    # Categorize encoding issues
                    if char_code > 255:
                        # High Unicode (Chinese, Arabic, special symbols)
                        self.report.encoding_issues['high_unicode'] += 1
                    elif 0x80 <= char_code <= 0xFF:
                        # Extended ASCII (Latin-1, accented characters)
                        self.report.encoding_issues['extended_ascii'] += 1

            # Check for quote issues (double single quotes)
            if "''" in value:
                self.report.quote_issues += 1
                self.report.problematic_fields.add(field_name)

            # Check for custom delimiters in HomeLocation
            if field_name == 'HomeLocation' and '%' in value:
                self.report.delimiter_issues += 1

            # Check for phone number formatting issues
            if field_name in ['WorkPhones', 'HomePhones'] and value:
                if value.startswith("'"):
                    self.report.phone_format_issues += 1
                    self.report.phone_patterns.add(value[:20])

            # Check for multiline issues
            if '\n' in value or '\r' in value:
                self.report.multiline_issues += 1
                self.report.problematic_fields.add(field_name)

    def _print_analysis_report(self) -> None:
        """Print a formatted analysis report."""
        print(f"\n{'DATA QUALITY ANALYSIS REPORT':^80}")
        print("=" * 80)

        print(f"\nFile Statistics:")
        print(f"  Total Rows: {self.report.total_rows:,}")
        print(f"  Total Fields: {self.report.total_fields}")

        print(f"\nIssues Detected:")
        print(f"  Encoding Issues:")
        print(f"    - Extended ASCII (Latin-1, accented): {self.report.encoding_issues['extended_ascii']:,}")
        print(f"    - High Unicode (Chinese, Arabic, etc): {self.report.encoding_issues['high_unicode']:,}")
        print(f"  Quote Issues (double single quotes): {self.report.quote_issues:,}")
        print(f"  Custom Delimiter Issues (% signs): {self.report.delimiter_issues:,}")
        print(f"  Phone Format Issues (leading quotes): {self.report.phone_format_issues:,}")
        print(f"  Multiline Field Issues: {self.report.multiline_issues:,}")

        print(f"\nTop 10 Empty Fields:")
        for field, count in self.report.empty_fields.most_common(10):
            pct = (count / self.report.total_rows) * 100
            print(f"  {field}: {count:,} ({pct:.1f}%)")

        print(f"\nTop 15 Non-ASCII Characters:")
        for char, count in self.report.special_chars.most_common(15):
            char_name = unicodedata.name(char, 'UNKNOWN')
            try:
                # Try to print the character
                print(f"  U+{ord(char):04X} ({char}): {count:,} - {char_name}")
            except (UnicodeEncodeError, UnicodeDecodeError):
                # If it fails, print without the character
                print(f"  U+{ord(char):04X}: {count:,} - {char_name}")

        print(f"\nProblematic Fields: {', '.join(sorted(self.report.problematic_fields))}")

        print(f"\nPhone Number Patterns Found:")
        for pattern in sorted(self.report.phone_patterns)[:5]:
            try:
                print(f"  {pattern}...")
            except (UnicodeEncodeError, UnicodeDecodeError):
                print(f"  [Pattern with special characters]")

    def clean(self, output_file: Optional[Path] = None) -> Path:
        """
        Clean the CSV file and write to output.

        Args:
            output_file: Output file path (default: adds _cleaned suffix)

        Returns:
            Path to the cleaned file
        """
        if output_file is None:
            output_file = self.input_file.parent / f"{self.input_file.stem}_cleaned.csv"
        else:
            output_file = Path(output_file)

        print(f"\nCleaning data and writing to: {output_file}")
        print("=" * 80)

        cleaned_rows = 0

        with open(self.input_file, 'r', encoding='utf-8', errors='replace') as infile, \
             open(output_file, 'w', encoding='utf-8', newline='') as outfile:

            reader = csv.DictReader(infile, delimiter=self.delimiter)

            # Write header
            if reader.fieldnames:
                writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames, delimiter=self.delimiter)
                writer.writeheader()

            # Process each row
            for row in reader:
                cleaned_row = self._clean_row(row)
                writer.writerow(cleaned_row)
                cleaned_rows += 1

                if cleaned_rows % 100 == 0:
                    print(f"  Processed {cleaned_rows:,} rows...", end='\r')

        print(f"\n[OK] Successfully cleaned {cleaned_rows:,} rows")
        print(f"[OK] Output written to: {output_file}")

        return output_file

    def _clean_row(self, row: Dict[str, str]) -> Dict[str, str]:
        """
        Clean a single row of data.

        Args:
            row: Dictionary representing a CSV row

        Returns:
            Cleaned row dictionary
        """
        cleaned = {}

        for field_name, value in row.items():
            if not value:
                cleaned[field_name] = value
                continue

            # Apply all cleaning transformations
            clean_value = value

            # 1. Normalize problematic characters
            clean_value = self._normalize_characters(clean_value)

            # 2. Fix quote issues
            if field_name == 'HomeLocation':
                clean_value = self._clean_home_location(clean_value)
            else:
                clean_value = self._fix_quotes(clean_value)

            # 3. Fix phone numbers
            if field_name in ['WorkPhones', 'HomePhones']:
                clean_value = self._clean_phone_number(clean_value)

            # 4. Remove multiline issues
            clean_value = self._normalize_whitespace(clean_value)

            # 5. Trim whitespace
            clean_value = clean_value.strip()

            cleaned[field_name] = clean_value

        return cleaned

    def _normalize_characters(self, text: str) -> str:
        """
        Normalize problematic characters to standard equivalents.

        Args:
            text: Input text

        Returns:
            Normalized text
        """
        # Replace known problematic characters
        for bad_char, good_char in self.PROBLEMATIC_CHARS.items():
            text = text.replace(bad_char, good_char)

        # Normalize Unicode to NFKC form (compatibility decomposition)
        # This handles most accented characters consistently
        # Note: We keep accented characters as they're valid data
        text = unicodedata.normalize('NFKC', text)

        return text

    def _fix_quotes(self, text: str) -> str:
        """
        Fix quote-related issues.

        Args:
            text: Input text

        Returns:
            Text with fixed quotes
        """
        # Replace double single quotes with nothing (they seem to be escape artifacts)
        text = text.replace("''", "")

        return text

    def _clean_home_location(self, location: str) -> str:
        """
        Clean the HomeLocation field which uses % as delimiters.

        Args:
            location: HomeLocation field value

        Returns:
            Cleaned location string
        """
        # Remove leading/trailing double single quotes
        location = self._fix_quotes(location)

        # The format is: '' Home street: %value% , Home state: %value%, ...
        # We'll parse and reconstruct in a cleaner format

        # Extract components
        parts = {}
        patterns = {
            'street': r'Home street:\s*%([^%]*)%',
            'state': r'Home state:\s*%([^%]*)%',
            'city': r'Home city:\s*%([^%]*)%',
            'zip': r'Home zip code:\s*%([^%]*)%',
            'country': r'Home country:\s*%([^%]*)%'
        }

        for key, pattern in patterns.items():
            match = re.search(pattern, location)
            if match:
                parts[key] = match.group(1).strip()

        # Reconstruct in a clean format (JSON-like or semicolon-separated)
        # Using semicolon as it's safer than comma for CSV
        if parts:
            clean_parts = []
            for key in ['street', 'city', 'state', 'zip', 'country']:
                if key in parts and parts[key]:
                    clean_parts.append(f"{key}={parts[key]}")

            return "; ".join(clean_parts)

        # If pattern doesn't match, return cleaned original
        return location.replace('%', '').strip()

    def _clean_phone_number(self, phone: str) -> str:
        """
        Clean phone number formatting.

        Args:
            phone: Phone number string

        Returns:
            Cleaned phone number
        """
        if not phone:
            return phone

        # Remove leading single quotes
        if phone.startswith("'"):
            phone = phone[1:]

        # Remove trailing quotes
        if phone.endswith("'"):
            phone = phone[:-1]

        # Normalize whitespace
        phone = ' '.join(phone.split())

        return phone

    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize all whitespace characters.

        Args:
            text: Input text

        Returns:
            Text with normalized whitespace
        """
        # Replace newlines and carriage returns with spaces
        text = text.replace('\r\n', ' ')
        text = text.replace('\n', ' ')
        text = text.replace('\r', ' ')

        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)

        return text

    def generate_report(self, output_file: Optional[Path] = None) -> Path:
        """
        Generate a detailed JSON report of the analysis.

        Args:
            output_file: Output file path for JSON report

        Returns:
            Path to the report file
        """
        if output_file is None:
            output_file = self.input_file.parent / f"{self.input_file.stem}_quality_report.json"
        else:
            output_file = Path(output_file)

        report_dict = self.report.to_dict()

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(report_dict, f, indent=2, ensure_ascii=False)

        print(f"\n[OK] Quality report written to: {output_file}")
        return output_file


def main():
    """Main entry point for the script."""
    import argparse

    parser = argparse.ArgumentParser(
        description='Clean and analyze Siemens candidate CSV data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze only (no changes)
  python siemens_data_cleaner.py input.csv --analyze-only

  # Clean the file
  python siemens_data_cleaner.py input.csv --output cleaned.csv

  # Analyze and clean with report
  python siemens_data_cleaner.py input.csv --output cleaned.csv --report report.json
        """
    )

    parser.add_argument('input_file', type=Path, help='Input CSV file to process')
    parser.add_argument('-o', '--output', type=Path, help='Output file for cleaned data')
    parser.add_argument('-r', '--report', type=Path, help='Output file for JSON quality report')
    parser.add_argument('-a', '--analyze-only', action='store_true',
                       help='Only analyze, do not clean')
    parser.add_argument('-d', '--delimiter', default='|',
                       help='CSV delimiter (default: |)')

    args = parser.parse_args()

    # Validate input file
    if not args.input_file.exists():
        print(f"Error: Input file not found: {args.input_file}", file=sys.stderr)
        sys.exit(1)

    # Create cleaner instance
    cleaner = SiemensDataCleaner(args.input_file, delimiter=args.delimiter)

    # Always analyze first
    cleaner.analyze()

    # Generate report if requested
    if args.report:
        cleaner.generate_report(args.report)

    # Clean if not analyze-only
    if not args.analyze_only:
        cleaned_file = cleaner.clean(args.output)

        print(f"\n{'CLEANING COMPLETE':^80}")
        print("=" * 80)
        print(f"\nOriginal file: {args.input_file}")
        print(f"Cleaned file:  {cleaned_file}")
        print(f"\nNext steps:")
        print(f"  1. Review the cleaned file: {cleaned_file}")
        print(f"  2. Compare with original to verify changes")
        print(f"  3. Test with your data parser/validator")
        if args.report:
            print(f"  4. Review quality report: {args.report}")
    else:
        print(f"\n{'ANALYSIS COMPLETE':^80}")
        print("=" * 80)
        print(f"\nRun without --analyze-only to clean the file")


if __name__ == '__main__':
    main()

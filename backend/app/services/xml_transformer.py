"""
XML Transformer Service
Transforms CSV data to Eightfold XML format based on employee schema
"""

import pandas as pd
from xml.etree.ElementTree import Element, SubElement, tostring, ElementTree
from xml.dom import minidom
from typing import Dict, List, Any
from datetime import datetime


class XMLTransformer:
    """
    Transforms CSV data to Eightfold XML format

    Features:
    - Converts mapped CSV data to EF_Employee XML structure
    - Handles complex nested elements (email_list, phone_list, etc.)
    - Formats dates and data types correctly
    - Generates pretty-printed XML output
    """

    def __init__(self):
        # Field type mappings
        self.date_fields = {
            'HIRING_DATE', 'ROLE_CHANGE_DATE', 'LAST_ACTIVITY_TS',
            'DATE_OF_BIRTH', 'START_DATE', 'END_DATE'
        }

        self.list_fields = {
            'EMAIL': 'email_list/email',
            'PHONE': 'phone_list/phone',
            'URL': 'url_list/url'
        }

        # Direct field mappings (CSV field -> XML element)
        self.field_map = {
            'EMPLOYEE_ID': 'employee_id',
            'USER_ID': 'user_id',
            'FIRST_NAME': 'first_name',
            'LAST_NAME': 'last_name',
            'PREFERRED_FIRST_NAME': 'preferred_first_name',
            'PREFERRED_LAST_NAME': 'preferred_last_name',
            'EMAIL': 'email_list/email',
            'PHONE': 'phone_list/phone',
            'TITLE': 'title',
            'DETAILED_TITLE': 'detailed_title',
            'ROLE': 'role',
            'COMPANY_NAME': 'company_name',
            'LEVEL': 'level',
            'LOCATION': 'location',
            'LOCATION_COUNTRY': 'location_country',
            'HIRING_DATE': 'hiring_date',
            'ROLE_CHANGE_DATE': 'role_change_date',
            'MANAGER_USERID': 'manager_userid',
            'MANAGER_EMAIL': 'manager_email',
            'MANAGER_FULLNAME': 'manager_fullname',
            'BUSINESS_UNIT': 'business_unit',
            'DIVISION': 'division',
            'LAST_ACTIVITY_TS': 'last_activity_ts',
        }

    def transform_csv_to_xml(
        self,
        df: pd.DataFrame,
        mappings: List[Dict[str, Any]],
        entity_name: str = "employee"
    ) -> str:
        """
        Transform CSV DataFrame to Eightfold XML format

        Args:
            df: Pandas DataFrame with CSV data
            mappings: List of field mappings {source, target, ...}
            entity_name: Entity type (currently only 'employee' supported)

        Returns:
            Pretty-printed XML string
        """
        # Create root element
        root = Element("EF_Employee_List")

        # Create mapping dictionary: target -> source
        # Handle both dict and Pydantic Mapping objects
        target_to_source = {}
        for m in mappings:
            if isinstance(m, dict):
                target_to_source[m['target']] = m['source']
            else:
                # Handle Pydantic Mapping object
                target_to_source[m.target] = m.source

        # Process each row as an employee
        for idx, row in df.iterrows():
            employee_elem = self._create_employee_element(row, target_to_source)
            root.append(employee_elem)

        # Pretty print XML
        xml_str = self._prettify_xml(root)
        return xml_str

    def _create_employee_element(
        self,
        row: pd.Series,
        target_to_source: Dict[str, str]
    ) -> Element:
        """
        Create a single EF_Employee element from a data row

        Args:
            row: Pandas Series with row data
            target_to_source: Mapping of target field -> source field

        Returns:
            XML Element for employee
        """
        employee = Element("EF_Employee")

        # Track which lists have been created
        created_lists = set()

        # Process each field mapping
        for target_field, source_field in target_to_source.items():
            if source_field not in row.index:
                continue

            value = row[source_field]

            # Skip if value is NaN or None
            if pd.isna(value) or value is None:
                continue

            # Handle list fields (email_list, phone_list, etc.)
            if target_field in self.list_fields:
                list_path = self.list_fields[target_field]
                self._add_list_element(employee, list_path, str(value), created_lists)

            # Handle standard fields
            elif target_field in self.field_map:
                xml_path = self.field_map[target_field]
                self._add_element_by_path(employee, xml_path, value, created_lists)

            # Handle unmapped fields as simple elements (lowercase)
            else:
                element_name = target_field.lower()
                self._add_simple_element(employee, element_name, value)

        return employee

    def _add_element_by_path(
        self,
        parent: Element,
        path: str,
        value: Any,
        created_lists: set
    ):
        """
        Add an element by XML path (e.g., 'email_list/email')

        Args:
            parent: Parent XML element
            path: Element path (e.g., 'email_list/email' or 'title')
            value: Value to set
            created_lists: Set of already created list containers
        """
        parts = path.split('/')

        if len(parts) == 1:
            # Simple element
            self._add_simple_element(parent, parts[0], value)
        else:
            # Nested element (e.g., email_list/email)
            list_name = parts[0]
            item_name = parts[1]

            # Get or create list container
            if list_name not in created_lists:
                list_elem = SubElement(parent, list_name)
                created_lists.add(list_name)
            else:
                # Find existing list element
                list_elem = parent.find(list_name)

            # Add item to list
            item_elem = SubElement(list_elem, item_name)
            item_elem.text = self._format_value(value, item_name)

    def _add_list_element(
        self,
        parent: Element,
        path: str,
        value: str,
        created_lists: set
    ):
        """
        Add an element to a list container

        Args:
            parent: Parent XML element
            path: Element path (e.g., 'email_list/email')
            value: Value to add
            created_lists: Set of already created list containers
        """
        parts = path.split('/')
        list_name = parts[0]
        item_name = parts[1]

        # Get or create list container
        if list_name not in created_lists:
            list_elem = SubElement(parent, list_name)
            created_lists.add(list_name)
        else:
            # Find existing list element
            list_elem = parent.find(list_name)

        # Handle multiple values - check for || separator first (Siemens format), then comma
        value_str = str(value)
        if '||' in value_str:
            # Siemens multi-value format with || separator
            values = [v.strip() for v in value_str.split('||')]
        else:
            # Standard comma-separated format
            values = [v.strip() for v in value_str.split(',')]

        for val in values:
            if val:  # Skip empty values
                item_elem = SubElement(list_elem, item_name)
                item_elem.text = val

    def _add_simple_element(
        self,
        parent: Element,
        name: str,
        value: Any
    ):
        """
        Add a simple text element

        Args:
            parent: Parent XML element
            name: Element name
            value: Element value
        """
        elem = SubElement(parent, name)
        elem.text = self._format_value(value, name)

    def _format_value(self, value: Any, field_name: str) -> str:
        """
        Format value based on field type

        Args:
            value: Raw value
            field_name: Field name (for type detection)

        Returns:
            Formatted string value (XML-safe)
        """
        from app.utils.sanitization import sanitize_xml_content

        # Handle dates
        if field_name.upper() in self.date_fields:
            try:
                if isinstance(value, str):
                    # Try parsing common date formats
                    for fmt in ['%Y-%m-%d', '%m/%d/%Y', '%d/%m/%Y', '%Y/%m/%d']:
                        try:
                            dt = datetime.strptime(value, fmt)
                            # Return in ISO format (dates don't need XML escaping)
                            if '_TS' in field_name.upper():
                                return dt.strftime('%Y-%m-%dT%H:%M:%S')
                            else:
                                return dt.strftime('%Y-%m-%d')
                        except ValueError:
                            continue
                    # If no format matched, sanitize and return
                    return sanitize_xml_content(str(value))
                elif isinstance(value, (datetime, pd.Timestamp)):
                    if '_TS' in field_name.upper():
                        return value.strftime('%Y-%m-%dT%H:%M:%S')
                    else:
                        return value.strftime('%Y-%m-%d')
            except Exception:
                pass

        # Handle booleans
        if isinstance(value, bool):
            return 'true' if value else 'false'

        # Convert to string and sanitize for XML
        # This escapes special characters: &, <, >, ", '
        return sanitize_xml_content(value)

    def _prettify_xml(self, elem: Element) -> str:
        """
        Return a pretty-printed XML string

        Args:
            elem: XML Element

        Returns:
            Formatted XML string
        """
        rough_string = tostring(elem, encoding='utf-8', method='xml')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ", encoding='UTF-8').decode('utf-8')


# Singleton instance
_xml_transformer = None


def get_xml_transformer() -> XMLTransformer:
    """Get singleton XMLTransformer instance"""
    global _xml_transformer
    if _xml_transformer is None:
        _xml_transformer = XMLTransformer()
    return _xml_transformer

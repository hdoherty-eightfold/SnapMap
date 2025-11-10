"""
Transformation Engine
Transforms data according to field mappings with data loss validation
"""

import pandas as pd
from datetime import datetime
from typing import List, Dict, Any
import re

from app.models.mapping import Mapping
from app.models.schema import EntitySchema
from app.services.data_validator import get_data_validator, DataLossError


class TransformationEngine:
    """Handles data transformation"""

    def transform_data(
        self,
        source_data: List[Dict[str, Any]],
        mappings: List[Mapping],
        schema: EntitySchema
    ) -> tuple[pd.DataFrame, List[str]]:
        """
        Transform source data according to mappings with data loss validation

        Args:
            source_data: Source data as list of dictionaries
            mappings: Field mappings
            schema: Target schema

        Returns:
            Tuple of (transformed DataFrame, list of transformations applied)

        Raises:
            DataLossError: If rows are lost during transformation
        """
        # Convert to DataFrame
        source_df = pd.DataFrame(source_data)
        initial_row_count = len(source_df)

        # Create mapping dictionary
        mapping_dict = {m.source: m.target for m in mappings}

        # Initialize output DataFrame with target columns
        target_columns = [f.name for f in schema.fields]
        output_df = pd.DataFrame(columns=target_columns)

        # Track transformations
        transformations = []

        # Apply mappings
        for source_col, target_col in mapping_dict.items():
            if source_col in source_df.columns:
                # Get field definition
                field_def = schema.get_field_by_name(target_col)

                if field_def:
                    # Apply type-specific transformations
                    if field_def.type == "date":
                        output_df[target_col] = self._transform_date(source_df[source_col])
                        transformations.append(
                            f"{source_col} → {target_col}: Date format converted to YYYY-MM-DD"
                        )
                    else:
                        output_df[target_col] = source_df[source_col]
                        transformations.append(f"{source_col} → {target_col}: Field mapped")

        # Add default values for required fields not mapped
        for field in schema.get_required_fields():
            if field.name not in output_df.columns or output_df[field.name].isna().all():
                if field.name == "LAST_ACTIVITY_TS":
                    # Auto-generate timestamp
                    output_df[field.name] = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
                    transformations.append(
                        f"{field.name}: Auto-generated with current timestamp"
                    )

        # Validate no data loss during field mapping
        validator = get_data_validator()
        try:
            validator.validate_row_count(
                input_df=source_df,
                output_df=output_df,
                operation_name="field mapping"
            )
        except DataLossError as e:
            # Re-raise with additional context
            raise DataLossError(
                message=f"Data loss during field mapping: {e.message}",
                lost_rows=e.lost_rows,
                total_rows=e.total_rows,
                details={
                    **e.details,
                    "transformations_applied": transformations,
                    "mapped_fields": list(mapping_dict.keys())
                }
            )

        return output_df, transformations

    def _transform_date(self, series: pd.Series) -> pd.Series:
        """
        Transform date column to YYYY-MM-DD format

        Handles various input formats
        """
        try:
            # Parse dates (handles multiple formats automatically)
            parsed = pd.to_datetime(series, errors='coerce')
            # Format as YYYY-MM-DD
            return parsed.dt.strftime('%Y-%m-%d')
        except:
            # If parsing fails, return as-is
            return series


# Singleton instance
_transformation_engine = None


def get_transformation_engine() -> TransformationEngine:
    """Get singleton TransformationEngine instance"""
    global _transformation_engine
    if _transformation_engine is None:
        _transformation_engine = TransformationEngine()
    return _transformation_engine

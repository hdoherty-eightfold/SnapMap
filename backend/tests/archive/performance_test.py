"""
Comprehensive Performance Testing Suite for SnapMap
Tests various file sizes and scenarios with detailed profiling
"""

import sys
import time
import cProfile
import pstats
import io
import psutil
import os
import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple
import json
from datetime import datetime

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from app.services.file_parser import get_file_parser
from app.services.semantic_matcher import get_semantic_matcher
from app.services.transformer import get_transformation_engine
from app.services.xml_transformer import get_xml_transformer
from app.services.schema_manager import get_schema_manager
from app.models.mapping import Mapping


class PerformanceTester:
    """Performance testing suite with profiling and metrics"""

    def __init__(self):
        self.results = []
        self.process = psutil.Process(os.getpid())
        self.base_memory = self.process.memory_info().rss / 1024 / 1024  # MB

    def measure_time(self, func, *args, **kwargs) -> Tuple[any, float]:
        """Measure execution time of a function"""
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        return result, elapsed

    def measure_memory(self) -> float:
        """Get current memory usage in MB"""
        return self.process.memory_info().rss / 1024 / 1024

    def profile_function(self, func, *args, **kwargs) -> Tuple[any, Dict]:
        """Profile a function and return stats"""
        profiler = cProfile.Profile()
        profiler.enable()

        start_time = time.time()
        start_memory = self.measure_memory()

        result = func(*args, **kwargs)

        elapsed_time = time.time() - start_time
        memory_used = self.measure_memory() - start_memory

        profiler.disable()

        # Get profiling stats
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(20)  # Top 20 functions

        return result, {
            'time': elapsed_time,
            'memory_mb': memory_used,
            'profile_output': s.getvalue()
        }

    def generate_test_data(self, row_count: int, field_count: int = 50,
                          has_special_chars: bool = False,
                          has_multi_values: bool = False) -> pd.DataFrame:
        """Generate test CSV data with specified characteristics"""
        print(f"  Generating test data: {row_count} rows, {field_count} fields...")

        data = {}

        # Standard fields
        data['EmployeeID'] = [f'EMP{i:06d}' for i in range(row_count)]
        data['FirstName'] = [f'First{i}' for i in range(row_count)]
        data['LastName'] = [f'Last{i}' for i in range(row_count)]
        data['Email'] = [f'employee{i}@company.com' for i in range(row_count)]
        data['Title'] = [f'Position {i % 10}' for i in range(row_count)]
        data['Department'] = [f'Dept {i % 5}' for i in range(row_count)]
        data['Location'] = [f'Location {i % 8}' for i in range(row_count)]
        data['HireDate'] = pd.date_range('2020-01-01', periods=row_count, freq='D').strftime('%Y-%m-%d').tolist()
        data['Salary'] = np.random.randint(40000, 150000, row_count).tolist()
        data['Phone'] = [f'+1-555-{i:07d}' for i in range(row_count)]

        # Add special characters if requested
        if has_special_chars:
            data['FirstName'] = [f'José{i}' if i % 3 == 0 else f'María{i}' if i % 3 == 1 else f'Müller{i}'
                                for i in range(row_count)]
            data['Notes'] = [f'Description with Turkish çğıöşü and Spanish ñáéíóú chars {i}'
                           for i in range(row_count)]

        # Add multi-value fields if requested
        if has_multi_values:
            data['Skills'] = [f'Skill{i}||Skill{i+1}||Skill{i+2}||Skill{i+3}||Skill{i+4}'
                             for i in range(row_count)]
            data['Certifications'] = [f'Cert{i}||Cert{i+1}||Cert{i+2}' for i in range(row_count)]

        # Add extra fields to reach target count
        for i in range(10, field_count):
            data[f'Field{i}'] = [f'Value{j}_{i}' for j in range(row_count)]

        # Add long text fields
        if has_special_chars:
            long_text = 'Lorem ipsum dolor sit amet, ' * 50  # ~1400 chars
            data['LongDescription'] = [f'{long_text} {i}' for i in range(row_count)]

        return pd.DataFrame(data)

    def test_file_upload_parse(self, row_count: int, **data_params) -> Dict:
        """Test file parsing performance"""
        print(f"\n[TEST] File Upload & Parse - {row_count} rows")

        # Generate test data
        df = self.generate_test_data(row_count, **data_params)

        # Convert to CSV bytes
        csv_content = df.to_csv(index=False, sep='|').encode('utf-8')
        file_size_mb = len(csv_content) / 1024 / 1024

        print(f"  File size: {file_size_mb:.2f} MB")

        # Test parsing
        parser = get_file_parser()
        result, stats = self.profile_function(
            parser.parse_file,
            csv_content,
            'test_data.csv',
            delimiter='|'
        )

        parsed_df, metadata = result

        print(f"  Parse time: {stats['time']:.3f}s")
        print(f"  Memory used: {stats['memory_mb']:.2f} MB")
        print(f"  Rows parsed: {len(parsed_df)}")
        print(f"  Columns: {len(parsed_df.columns)}")

        return {
            'test': 'file_upload_parse',
            'row_count': row_count,
            'file_size_mb': file_size_mb,
            'parse_time': stats['time'],
            'memory_mb': stats['memory_mb'],
            'success': len(parsed_df) == row_count,
            'profile': stats['profile_output']
        }

    def test_semantic_mapping(self, row_count: int, **data_params) -> Dict:
        """Test semantic field mapping performance"""
        print(f"\n[TEST] Semantic Field Mapping - {row_count} rows")

        # Generate test data
        df = self.generate_test_data(row_count, **data_params)
        source_fields = df.columns.tolist()

        print(f"  Fields to map: {len(source_fields)}")

        # Test semantic mapping
        matcher = get_semantic_matcher()

        result, stats = self.profile_function(
            matcher.map_fields_batch,
            source_fields,
            'employee',
            min_confidence=0.5
        )

        mappings = result
        mapped_count = sum(1 for m in mappings if m['target_field'] is not None)

        print(f"  Mapping time: {stats['time']:.3f}s")
        print(f"  Time per field: {stats['time']/len(source_fields)*1000:.2f}ms")
        print(f"  Memory used: {stats['memory_mb']:.2f} MB")
        print(f"  Fields mapped: {mapped_count}/{len(source_fields)}")

        return {
            'test': 'semantic_mapping',
            'row_count': row_count,
            'field_count': len(source_fields),
            'mapping_time': stats['time'],
            'time_per_field_ms': stats['time']/len(source_fields)*1000,
            'memory_mb': stats['memory_mb'],
            'mapped_count': mapped_count,
            'profile': stats['profile_output']
        }

    def test_data_transformation(self, row_count: int, **data_params) -> Dict:
        """Test data transformation performance"""
        print(f"\n[TEST] Data Transformation - {row_count} rows")

        # Generate test data
        df = self.generate_test_data(row_count, **data_params)
        source_data = df.to_dict('records')

        # Get schema
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema('employee')

        # Create mappings
        mappings = [
            Mapping(source='EmployeeID', target='EMPLOYEE_ID', confidence=1.0, method='manual'),
            Mapping(source='FirstName', target='FIRST_NAME', confidence=1.0, method='manual'),
            Mapping(source='LastName', target='LAST_NAME', confidence=1.0, method='manual'),
            Mapping(source='Email', target='EMAIL', confidence=1.0, method='manual'),
            Mapping(source='Title', target='TITLE', confidence=1.0, method='manual'),
            Mapping(source='HireDate', target='HIRING_DATE', confidence=1.0, method='manual'),
        ]

        print(f"  Transforming {len(source_data)} records...")

        # Test transformation
        engine = get_transformation_engine()
        result, stats = self.profile_function(
            engine.transform_data,
            source_data,
            mappings,
            schema
        )

        transformed_df, transformations = result

        print(f"  Transform time: {stats['time']:.3f}s")
        print(f"  Memory used: {stats['memory_mb']:.2f} MB")
        print(f"  Rows transformed: {len(transformed_df)}")
        print(f"  Transformations applied: {len(transformations)}")

        return {
            'test': 'data_transformation',
            'row_count': row_count,
            'transform_time': stats['time'],
            'memory_mb': stats['memory_mb'],
            'success': len(transformed_df) == row_count,
            'profile': stats['profile_output']
        }

    def test_xml_export(self, row_count: int, **data_params) -> Dict:
        """Test XML export performance"""
        print(f"\n[TEST] XML Export - {row_count} rows")

        # Generate test data
        df = self.generate_test_data(row_count, **data_params)

        # Create mappings
        mappings = [
            {'source': 'EmployeeID', 'target': 'EMPLOYEE_ID'},
            {'source': 'FirstName', 'target': 'FIRST_NAME'},
            {'source': 'LastName', 'target': 'LAST_NAME'},
            {'source': 'Email', 'target': 'EMAIL'},
            {'source': 'Title', 'target': 'TITLE'},
        ]

        print(f"  Generating XML for {len(df)} records...")

        # Test XML transformation
        xml_transformer = get_xml_transformer()
        result, stats = self.profile_function(
            xml_transformer.transform_csv_to_xml,
            df,
            mappings,
            'employee'
        )

        xml_content = result
        xml_size_mb = len(xml_content.encode('utf-8')) / 1024 / 1024

        print(f"  XML generation time: {stats['time']:.3f}s")
        print(f"  Memory used: {stats['memory_mb']:.2f} MB")
        print(f"  XML size: {xml_size_mb:.2f} MB")

        return {
            'test': 'xml_export',
            'row_count': row_count,
            'xml_time': stats['time'],
            'xml_size_mb': xml_size_mb,
            'memory_mb': stats['memory_mb'],
            'profile': stats['profile_output']
        }

    def test_complete_pipeline(self, row_count: int, **data_params) -> Dict:
        """Test complete pipeline from upload to export"""
        print(f"\n[TEST] Complete Pipeline - {row_count} rows")

        overall_start = time.time()
        start_memory = self.measure_memory()

        # Step 1: Generate and parse
        df = self.generate_test_data(row_count, **data_params)
        csv_content = df.to_csv(index=False, sep='|').encode('utf-8')

        parser = get_file_parser()
        parsed_df, metadata = parser.parse_file(csv_content, 'test.csv', delimiter='|')
        parse_time = time.time() - overall_start

        # Step 2: Semantic mapping
        step2_start = time.time()
        matcher = get_semantic_matcher()
        mappings = matcher.map_fields_batch(parsed_df.columns.tolist(), 'employee', min_confidence=0.5)
        mapping_time = time.time() - step2_start

        # Step 3: Transform
        step3_start = time.time()
        schema_manager = get_schema_manager()
        schema = schema_manager.get_schema('employee')

        mapping_objs = [
            Mapping(source=m['source_field'], target=m['target_field'],
                   confidence=m['confidence'], method='semantic')
            for m in mappings if m['target_field'] is not None
        ][:6]  # Use first 6 mappings

        engine = get_transformation_engine()
        transformed_df, transformations = engine.transform_data(
            parsed_df.to_dict('records'), mapping_objs, schema
        )
        transform_time = time.time() - step3_start

        # Step 4: XML export
        step4_start = time.time()
        xml_transformer = get_xml_transformer()
        xml_mappings = [{'source': m.source, 'target': m.target} for m in mapping_objs]
        xml_content = xml_transformer.transform_csv_to_xml(transformed_df, xml_mappings, 'employee')
        xml_time = time.time() - step4_start

        total_time = time.time() - overall_start
        total_memory = self.measure_memory() - start_memory

        print(f"  Parse time: {parse_time:.3f}s")
        print(f"  Mapping time: {mapping_time:.3f}s")
        print(f"  Transform time: {transform_time:.3f}s")
        print(f"  XML export time: {xml_time:.3f}s")
        print(f"  TOTAL TIME: {total_time:.3f}s")
        print(f"  Memory used: {total_memory:.2f} MB")

        return {
            'test': 'complete_pipeline',
            'row_count': row_count,
            'parse_time': parse_time,
            'mapping_time': mapping_time,
            'transform_time': transform_time,
            'xml_time': xml_time,
            'total_time': total_time,
            'memory_mb': total_memory,
            'success': len(transformed_df) == row_count
        }

    def run_benchmarks(self):
        """Run comprehensive benchmarks"""
        print("=" * 80)
        print("SNAPMAP PERFORMANCE BENCHMARK SUITE")
        print("=" * 80)
        print(f"Python version: {sys.version}")
        print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Base memory: {self.base_memory:.2f} MB")
        print("=" * 80)

        # Test scenarios as specified
        scenarios = [
            # Small file (100 rows)
            {'name': 'Small File (100 rows)', 'row_count': 100, 'field_count': 50},
            # Medium file (1,000 rows)
            {'name': 'Medium File (1,000 rows)', 'row_count': 1000, 'field_count': 50},
            # Large file (10,000 rows)
            {'name': 'Large File (10,000 rows)', 'row_count': 10000, 'field_count': 50},
            # Siemens-like file (1,213 rows with special chars and multi-values)
            {
                'name': 'Siemens File (1,213 rows)',
                'row_count': 1213,
                'field_count': 52,
                'has_special_chars': True,
                'has_multi_values': True
            },
        ]

        for scenario in scenarios:
            print(f"\n{'=' * 80}")
            print(f"SCENARIO: {scenario['name']}")
            print(f"{'=' * 80}")

            scenario_name = scenario.pop('name')

            # Run all tests for this scenario
            try:
                parse_result = self.test_file_upload_parse(**scenario)
                self.results.append({**parse_result, 'scenario': scenario_name})

                map_result = self.test_semantic_mapping(**scenario)
                self.results.append({**map_result, 'scenario': scenario_name})

                transform_result = self.test_data_transformation(**scenario)
                self.results.append({**transform_result, 'scenario': scenario_name})

                xml_result = self.test_xml_export(**scenario)
                self.results.append({**xml_result, 'scenario': scenario_name})

                pipeline_result = self.test_complete_pipeline(**scenario)
                self.results.append({**pipeline_result, 'scenario': scenario_name})

            except Exception as e:
                print(f"\n  ERROR: {e}")
                import traceback
                traceback.print_exc()

        print("\n" + "=" * 80)
        print("BENCHMARK COMPLETE")
        print("=" * 80)

    def generate_report(self) -> str:
        """Generate performance report"""
        report = []
        report.append("# SnapMap Performance Test Report\n")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report.append(f"**Python Version:** {sys.version}\n")
        report.append("\n---\n")

        # Summary table
        report.append("\n## Performance Summary\n")
        report.append("\n| Scenario | Test | Rows | Time (s) | Memory (MB) | Status |\n")
        report.append("|----------|------|------|----------|-------------|--------|\n")

        for result in self.results:
            scenario = result.get('scenario', 'Unknown')
            test = result.get('test', 'Unknown')
            row_count = result.get('row_count', 0)

            # Get time metric
            time_val = result.get('total_time') or result.get('parse_time') or \
                      result.get('mapping_time') or result.get('transform_time') or \
                      result.get('xml_time', 0)

            memory = result.get('memory_mb', 0)
            success = result.get('success', True)
            status = "PASS" if success else "FAIL"

            report.append(f"| {scenario} | {test} | {row_count:,} | {time_val:.3f} | {memory:.2f} | {status} |\n")

        # Detailed results
        report.append("\n---\n")
        report.append("\n## Detailed Results\n")

        # Group by scenario
        scenarios = {}
        for result in self.results:
            scenario = result.get('scenario', 'Unknown')
            if scenario not in scenarios:
                scenarios[scenario] = []
            scenarios[scenario].append(result)

        for scenario, results in scenarios.items():
            report.append(f"\n### {scenario}\n")

            for result in results:
                test_name = result.get('test', 'Unknown')
                report.append(f"\n#### {test_name}\n")

                # Key metrics
                if test_name == 'file_upload_parse':
                    report.append(f"- **Parse Time:** {result.get('parse_time', 0):.3f}s\n")
                    report.append(f"- **File Size:** {result.get('file_size_mb', 0):.2f} MB\n")
                    target_time = 1 if result.get('row_count', 0) <= 100 else \
                                 2 if result.get('row_count', 0) <= 1000 else 10
                    status = "PASS" if result.get('parse_time', 999) < target_time else "FAIL"
                    report.append(f"- **Target:** < {target_time}s - {status}\n")

                elif test_name == 'semantic_mapping':
                    report.append(f"- **Mapping Time:** {result.get('mapping_time', 0):.3f}s\n")
                    report.append(f"- **Fields Mapped:** {result.get('mapped_count', 0)}/{result.get('field_count', 0)}\n")
                    report.append(f"- **Time per Field:** {result.get('time_per_field_ms', 0):.2f}ms\n")
                    target_time = 2 if result.get('row_count', 0) <= 100 else \
                                 3 if result.get('row_count', 0) <= 1000 else 5
                    status = "PASS" if result.get('mapping_time', 999) < target_time else "FAIL"
                    report.append(f"- **Target:** < {target_time}s - {status}\n")

                elif test_name == 'data_transformation':
                    report.append(f"- **Transform Time:** {result.get('transform_time', 0):.3f}s\n")
                    target_time = 1 if result.get('row_count', 0) <= 100 else \
                                 2 if result.get('row_count', 0) <= 1000 else 5
                    status = "PASS" if result.get('transform_time', 999) < target_time else "FAIL"
                    report.append(f"- **Target:** < {target_time}s - {status}\n")

                elif test_name == 'xml_export':
                    report.append(f"- **XML Generation Time:** {result.get('xml_time', 0):.3f}s\n")
                    report.append(f"- **XML Size:** {result.get('xml_size_mb', 0):.2f} MB\n")

                elif test_name == 'complete_pipeline':
                    report.append(f"- **Parse:** {result.get('parse_time', 0):.3f}s\n")
                    report.append(f"- **Mapping:** {result.get('mapping_time', 0):.3f}s\n")
                    report.append(f"- **Transform:** {result.get('transform_time', 0):.3f}s\n")
                    report.append(f"- **XML Export:** {result.get('xml_time', 0):.3f}s\n")
                    report.append(f"- **TOTAL:** {result.get('total_time', 0):.3f}s\n")
                    target_time = 10
                    status = "PASS" if result.get('total_time', 999) < target_time else "FAIL"
                    report.append(f"- **Target:** < {target_time}s - {status}\n")

                report.append(f"- **Memory Used:** {result.get('memory_mb', 0):.2f} MB\n")

        # Bottleneck analysis
        report.append("\n---\n")
        report.append("\n## Bottleneck Analysis\n")

        # Find slowest operations
        complete_pipeline_results = [r for r in self.results if r.get('test') == 'complete_pipeline']

        if complete_pipeline_results:
            report.append("\n### Time Distribution in Complete Pipeline\n")

            for result in complete_pipeline_results:
                scenario = result.get('scenario', 'Unknown')
                total = result.get('total_time', 1)

                report.append(f"\n**{scenario}:**\n")
                report.append(f"- Parse: {result.get('parse_time', 0):.3f}s ({result.get('parse_time', 0)/total*100:.1f}%)\n")
                report.append(f"- Mapping: {result.get('mapping_time', 0):.3f}s ({result.get('mapping_time', 0)/total*100:.1f}%)\n")
                report.append(f"- Transform: {result.get('transform_time', 0):.3f}s ({result.get('transform_time', 0)/total*100:.1f}%)\n")
                report.append(f"- XML Export: {result.get('xml_time', 0):.3f}s ({result.get('xml_time', 0)/total*100:.1f}%)\n")

        # Optimization recommendations
        report.append("\n---\n")
        report.append("\n## Optimization Recommendations\n")

        recommendations = []

        # Analyze results for bottlenecks
        for result in complete_pipeline_results:
            total = result.get('total_time', 1)
            parse_pct = result.get('parse_time', 0) / total * 100
            mapping_pct = result.get('mapping_time', 0) / total * 100
            transform_pct = result.get('transform_time', 0) / total * 100
            xml_pct = result.get('xml_time', 0) / total * 100

            if parse_pct > 30:
                recommendations.append("**File Parsing** is a bottleneck (>30% of time). Consider: parallel chunk processing, faster CSV library (polars), or streaming parsing.")

            if mapping_pct > 30:
                recommendations.append("**Semantic Mapping** is a bottleneck (>30% of time). Consider: caching embeddings more aggressively, batch processing optimizations.")

            if xml_pct > 30:
                recommendations.append("**XML Export** is a bottleneck (>30% of time). Consider: streaming XML generation, C-based XML library (lxml), or parallel processing.")

        if not recommendations:
            recommendations.append("Performance is well-balanced across all stages.")

        for rec in set(recommendations):  # Remove duplicates
            report.append(f"\n{rec}\n")

        # Memory analysis
        report.append("\n---\n")
        report.append("\n## Memory Usage Analysis\n")

        max_memory = max([r.get('memory_mb', 0) for r in self.results])
        report.append(f"\n**Peak Memory Usage:** {max_memory:.2f} MB\n")

        # Check for memory issues
        large_file_results = [r for r in self.results if r.get('row_count', 0) >= 10000]
        if large_file_results:
            avg_memory = sum([r.get('memory_mb', 0) for r in large_file_results]) / len(large_file_results)
            report.append(f"**Average Memory for Large Files (10k+ rows):** {avg_memory:.2f} MB\n")

            if max_memory > 500:
                report.append("\n**WARNING:** High memory usage detected. Consider implementing streaming processing for large files.\n")

        # Scalability assessment
        report.append("\n---\n")
        report.append("\n## Scalability Assessment\n")

        pipeline_times = {}
        for result in complete_pipeline_results:
            row_count = result.get('row_count', 0)
            total_time = result.get('total_time', 0)
            pipeline_times[row_count] = total_time

        if len(pipeline_times) >= 3:
            sorted_sizes = sorted(pipeline_times.keys())

            # Calculate time per row at different scales
            report.append("\n**Time per Row:**\n")
            for size in sorted_sizes:
                time_per_row = (pipeline_times[size] / size) * 1000  # ms per row
                report.append(f"- {size:,} rows: {time_per_row:.3f}ms/row\n")

            # Assess linearity
            small_time_per_row = pipeline_times[sorted_sizes[0]] / sorted_sizes[0]
            large_time_per_row = pipeline_times[sorted_sizes[-1]] / sorted_sizes[-1]

            if large_time_per_row <= small_time_per_row * 1.5:
                report.append("\n**Assessment:** Excellent scalability - near-linear performance.\n")
            elif large_time_per_row <= small_time_per_row * 3:
                report.append("\n**Assessment:** Good scalability - sub-linear degradation.\n")
            else:
                report.append("\n**Assessment:** Performance degrades significantly at scale. Optimization recommended.\n")

        # Profiling insights
        report.append("\n---\n")
        report.append("\n## Top Performance Hotspots (From Profiling)\n")

        # Get one complete pipeline result with profiling data
        for result in complete_pipeline_results:
            if 'profile' in result:
                report.append("\n```\n")
                # Extract top 10 lines from profile
                profile_lines = result['profile'].split('\n')[:15]
                report.append('\n'.join(profile_lines))
                report.append("\n```\n")
                break

        return ''.join(report)


def main():
    """Main entry point"""
    tester = PerformanceTester()

    try:
        # Run benchmarks
        tester.run_benchmarks()

        # Generate report
        report = tester.generate_report()

        # Save report
        report_path = Path(__file__).parent.parent / 'PERFORMANCE_REPORT.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n{'=' * 80}")
        print(f"Performance report saved to: {report_path}")
        print(f"{'=' * 80}\n")

        # Also save JSON results
        json_path = Path(__file__).parent.parent / 'performance_results.json'
        with open(json_path, 'w') as f:
            json.dump(tester.results, f, indent=2, default=str)

        print(f"JSON results saved to: {json_path}\n")

    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()

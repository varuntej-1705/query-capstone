"""
Data Processor Module
Handles file parsing, data cleaning, and dataset merging
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional, Any
import os


class DataProcessor:
    """Handles all data processing operations"""
    
    @staticmethod
    def convert_to_native(obj):
        """Convert numpy types to native Python types for JSON serialization"""
        if isinstance(obj, dict):
            return {k: DataProcessor.convert_to_native(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [DataProcessor.convert_to_native(item) for item in obj]
        elif isinstance(obj, (np.integer, np.int64, np.int32)):
            return int(obj)
        elif isinstance(obj, (np.floating, np.float64, np.float32)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif pd.isna(obj):
            return None
        else:
            return obj
    
    @staticmethod
    def read_file(filepath: str) -> pd.DataFrame:
        """Read CSV or Excel file into DataFrame"""
        ext = os.path.splitext(filepath)[1].lower()
        
        if ext == '.csv':
            return pd.read_csv(filepath)
        elif ext in ['.xlsx', '.xls']:
            return pd.read_excel(filepath)
        else:
            raise ValueError(f"Unsupported file format: {ext}")
    
    @staticmethod
    def get_dataset_info(df: pd.DataFrame) -> Dict[str, Any]:
        """Get comprehensive information about a dataset"""
        info = {
            'rows': int(len(df)),
            'columns': int(len(df.columns)),
            'column_names': df.columns.tolist(),
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'missing_values': {k: int(v) for k, v in df.isnull().sum().to_dict().items()},
            'missing_percentage': {k: float(v) for k, v in (df.isnull().sum() / len(df) * 100).round(2).to_dict().items()},
            'memory_usage': float(df.memory_usage(deep=True).sum() / 1024 / 1024),  # MB
            'duplicates': int(df.duplicated().sum()),
            'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),
            'categorical_columns': df.select_dtypes(include=['object', 'category']).columns.tolist(),
            'datetime_columns': df.select_dtypes(include=['datetime64']).columns.tolist()
        }
        return info
    
    @staticmethod
    def get_preview(df: pd.DataFrame, rows: int = 10) -> Dict[str, Any]:
        """Get preview data for display"""
        # Convert DataFrame to native Python types for JSON serialization
        preview_df = df.head(rows).fillna('')
        data = []
        for _, row in preview_df.iterrows():
            row_dict = {}
            for col in preview_df.columns:
                val = row[col]
                if isinstance(val, (np.integer, np.int64, np.int32)):
                    row_dict[col] = int(val)
                elif isinstance(val, (np.floating, np.float64, np.float32)):
                    row_dict[col] = float(val)
                elif isinstance(val, np.bool_):
                    row_dict[col] = bool(val)
                else:
                    row_dict[col] = val
            data.append(row_dict)
        
        return {
            'columns': df.columns.tolist(),
            'data': data,
            'total_rows': int(len(df))
        }
    
    @staticmethod
    def detect_common_columns(datasets: Dict[str, pd.DataFrame]) -> Dict[str, List[str]]:
        """Detect common columns between datasets"""
        if len(datasets) < 2:
            return {}
        
        common_cols = {}
        dataset_names = list(datasets.keys())
        
        for i in range(len(dataset_names)):
            for j in range(i + 1, len(dataset_names)):
                name1, name2 = dataset_names[i], dataset_names[j]
                cols1 = set(datasets[name1].columns)
                cols2 = set(datasets[name2].columns)
                common = list(cols1.intersection(cols2))
                if common:
                    common_cols[f"{name1}__{name2}"] = common
        
        return common_cols
    
    @staticmethod
    def merge_datasets(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        on: str,
        how: str = 'inner'
    ) -> pd.DataFrame:
        """Merge two datasets on a common column"""
        return pd.merge(df1, df2, on=on, how=how)
    
    @staticmethod
    def handle_missing_values(
        df: pd.DataFrame,
        strategy: str = 'drop',
        fill_value: Any = None
    ) -> pd.DataFrame:
        """Handle missing values in dataset"""
        df = df.copy()
        
        if strategy == 'drop':
            return df.dropna()
        elif strategy == 'fill_mean':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            return df
        elif strategy == 'fill_median':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
            return df
        elif strategy == 'fill_mode':
            for col in df.columns:
                df[col] = df[col].fillna(df[col].mode().iloc[0] if not df[col].mode().empty else None)
            return df
        elif strategy == 'fill_value' and fill_value is not None:
            return df.fillna(fill_value)
        elif strategy == 'forward_fill':
            return df.ffill()
        elif strategy == 'backward_fill':
            return df.bfill()
        else:
            return df
    
    @staticmethod
    def remove_duplicates(df: pd.DataFrame, keep: str = 'first') -> pd.DataFrame:
        """Remove duplicate rows"""
        return df.drop_duplicates(keep=keep)
    
    @staticmethod
    def infer_data_source(df: pd.DataFrame) -> str:
        """Infer the type of data source based on column patterns"""
        columns_lower = [col.lower() for col in df.columns]
        
        # Check for common patterns
        if any('customer' in col or 'client' in col for col in columns_lower):
            return 'Customer Data'
        elif any('sales' in col or 'revenue' in col or 'transaction' in col for col in columns_lower):
            return 'Sales/Transaction Data'
        elif any('product' in col or 'item' in col or 'sku' in col for col in columns_lower):
            return 'Product Data'
        elif any('employee' in col or 'staff' in col or 'hr' in col for col in columns_lower):
            return 'HR/Employee Data'
        elif any('date' in col or 'time' in col for col in columns_lower):
            return 'Time Series Data'
        elif any('lat' in col or 'lon' in col or 'location' in col for col in columns_lower):
            return 'Geospatial Data'
        else:
            return 'General Dataset'
    
    @staticmethod
    def calculate_health_score(df: pd.DataFrame) -> Dict[str, Any]:
        """
        Calculate comprehensive data health score (0-100)
        Uses weighted scoring based on:
        - Missing values percentage (30% weight)
        - Duplicate row count (20% weight)
        - Outlier ratio using IQR (25% weight)
        - Data type consistency (25% weight)
        """
        total_rows = len(df)
        total_cols = len(df.columns)
        
        if total_rows == 0 or total_cols == 0:
            return {
                'score': 0,
                'category': 'Poor',
                'color': 'red',
                'components': {}
            }
        
        # 1. Missing Values Score (30% weight)
        missing_percentage = (df.isnull().sum().sum() / (total_rows * total_cols)) * 100
        missing_score = max(0, 100 - (missing_percentage * 2))  # Penalize 2 points per 1% missing
        
        # 2. Duplicate Score (20% weight)
        duplicate_count = df.duplicated().sum()
        duplicate_percentage = (duplicate_count / total_rows) * 100
        duplicate_score = max(0, 100 - (duplicate_percentage * 2))
        
        # 3. Outlier Score using IQR method (25% weight)
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_count = 0
        total_numeric_values = 0
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outliers = ((col_data < lower_bound) | (col_data > upper_bound)).sum()
                outlier_count += outliers
                total_numeric_values += len(col_data)
        
        outlier_percentage = (outlier_count / max(1, total_numeric_values)) * 100
        outlier_score = max(0, 100 - (outlier_percentage * 3))  # Penalize 3 points per 1% outliers
        
        # 4. Data Type Consistency Score (25% weight)
        consistency_issues = 0
        for col in df.columns:
            # Check if column has mixed types (object columns with potential numbers)
            if df[col].dtype == 'object':
                try:
                    numeric_convertible = pd.to_numeric(df[col], errors='coerce').notna().sum()
                    non_null_count = df[col].notna().sum()
                    if non_null_count > 0:
                        # If more than 50% can be converted to numbers, flag as inconsistent
                        if numeric_convertible / non_null_count > 0.5 and numeric_convertible < non_null_count:
                            consistency_issues += 1
                except:
                    pass
        
        consistency_percentage = (consistency_issues / max(1, total_cols)) * 100
        consistency_score = max(0, 100 - (consistency_percentage * 5))
        
        # Calculate weighted total score
        weights = {
            'missing_values': 0.30,
            'duplicates': 0.20,
            'outliers': 0.25,
            'consistency': 0.25
        }
        
        total_score = (
            missing_score * weights['missing_values'] +
            duplicate_score * weights['duplicates'] +
            outlier_score * weights['outliers'] +
            consistency_score * weights['consistency']
        )
        
        total_score = round(min(100, max(0, total_score)), 1)
        
        # Determine category and color
        if total_score >= 80:
            category = 'Good'
            color = 'green'
        elif total_score >= 50:
            category = 'Average'
            color = 'yellow'
        else:
            category = 'Poor'
            color = 'red'
        
        return {
            'score': total_score,
            'category': category,
            'color': color,
            'components': {
                'missing_values': {
                    'score': round(missing_score, 1),
                    'percentage': round(missing_percentage, 2),
                    'weight': '30%',
                    'description': f'{round(missing_percentage, 1)}% missing values'
                },
                'duplicates': {
                    'score': round(duplicate_score, 1),
                    'count': int(duplicate_count),
                    'percentage': round(duplicate_percentage, 2),
                    'weight': '20%',
                    'description': f'{duplicate_count} duplicate rows ({round(duplicate_percentage, 1)}%)'
                },
                'outliers': {
                    'score': round(outlier_score, 1),
                    'count': int(outlier_count),
                    'percentage': round(outlier_percentage, 2),
                    'weight': '25%',
                    'description': f'{outlier_count} outliers detected ({round(outlier_percentage, 1)}%)'
                },
                'consistency': {
                    'score': round(consistency_score, 1),
                    'issues': int(consistency_issues),
                    'weight': '25%',
                    'description': f'{consistency_issues} columns with type inconsistencies'
                }
            }
        }

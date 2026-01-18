"""
EDA Engine Module
Core exploratory data analysis functionality
"""
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from scipy import stats


class EDAEngine:
    """Core engine for automated exploratory data analysis"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        self.numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        self.categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()
    
    def get_descriptive_statistics(self) -> Dict[str, Any]:
        """Generate comprehensive descriptive statistics"""
        stats_dict = {}
        
        # Numeric statistics
        if self.numeric_cols:
            numeric_stats = self.df[self.numeric_cols].describe().to_dict()
            
            # Add additional statistics
            for col in self.numeric_cols:
                if col not in stats_dict:
                    stats_dict[col] = {}
                stats_dict[col] = {
                    'count': int(self.df[col].count()),
                    'mean': round(float(self.df[col].mean()), 4) if not pd.isna(self.df[col].mean()) else None,
                    'std': round(float(self.df[col].std()), 4) if not pd.isna(self.df[col].std()) else None,
                    'min': round(float(self.df[col].min()), 4) if not pd.isna(self.df[col].min()) else None,
                    'max': round(float(self.df[col].max()), 4) if not pd.isna(self.df[col].max()) else None,
                    'median': round(float(self.df[col].median()), 4) if not pd.isna(self.df[col].median()) else None,
                    'skewness': round(float(self.df[col].skew()), 4) if not pd.isna(self.df[col].skew()) else None,
                    'kurtosis': round(float(self.df[col].kurtosis()), 4) if not pd.isna(self.df[col].kurtosis()) else None,
                    'q1': round(float(self.df[col].quantile(0.25)), 4),
                    'q3': round(float(self.df[col].quantile(0.75)), 4),
                    'iqr': round(float(self.df[col].quantile(0.75) - self.df[col].quantile(0.25)), 4),
                    'missing': int(self.df[col].isnull().sum()),
                    'unique': int(self.df[col].nunique())
                }
        
        # Categorical statistics
        for col in self.categorical_cols:
            stats_dict[col] = {
                'count': int(self.df[col].count()),
                'unique': int(self.df[col].nunique()),
                'top': str(self.df[col].mode().iloc[0]) if not self.df[col].mode().empty else None,
                'freq': int(self.df[col].value_counts().iloc[0]) if len(self.df[col].value_counts()) > 0 else 0,
                'missing': int(self.df[col].isnull().sum())
            }
        
        return stats_dict
    
    def get_missing_value_analysis(self) -> Dict[str, Any]:
        """Analyze missing values in the dataset"""
        missing_count = self.df.isnull().sum()
        missing_percent = (missing_count / len(self.df) * 100).round(2)
        
        return {
            'total_missing': int(missing_count.sum()),
            'total_cells': int(self.df.size),
            'missing_percentage': round(float(missing_count.sum() / self.df.size * 100), 2),
            'by_column': {
                col: {
                    'count': int(missing_count[col]),
                    'percentage': float(missing_percent[col])
                }
                for col in self.df.columns
            },
            'columns_with_missing': [col for col in self.df.columns if missing_count[col] > 0]
        }
    
    def get_correlation_matrix(self) -> Dict[str, Any]:
        """Calculate correlation matrix for numeric columns"""
        if not self.numeric_cols:
            return {'matrix': {}, 'columns': []}
        
        corr_matrix = self.df[self.numeric_cols].corr().round(4)
        
        # Find strong correlations
        strong_correlations = []
        for i, col1 in enumerate(self.numeric_cols):
            for j, col2 in enumerate(self.numeric_cols):
                if i < j:
                    corr_val = corr_matrix.loc[col1, col2]
                    if abs(corr_val) >= 0.7:
                        strong_correlations.append({
                            'column1': col1,
                            'column2': col2,
                            'correlation': float(corr_val),
                            'strength': 'Strong Positive' if corr_val > 0 else 'Strong Negative'
                        })
        
        return {
            'matrix': corr_matrix.to_dict(),
            'columns': self.numeric_cols,
            'strong_correlations': strong_correlations
        }
    
    def detect_outliers(self, method: str = 'iqr') -> Dict[str, Any]:
        """Detect outliers in numeric columns"""
        outliers = {}
        
        for col in self.numeric_cols:
            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                outlier_mask = (self.df[col] < lower_bound) | (self.df[col] > upper_bound)
            elif method == 'zscore':
                z_scores = np.abs(stats.zscore(self.df[col].dropna()))
                outlier_mask = z_scores > 3
            else:
                continue
            
            outlier_count = int(outlier_mask.sum())
            outliers[col] = {
                'count': outlier_count,
                'percentage': round(float(outlier_count / len(self.df) * 100), 2),
                'lower_bound': round(float(lower_bound), 4) if method == 'iqr' else None,
                'upper_bound': round(float(upper_bound), 4) if method == 'iqr' else None
            }
        
        return outliers
    
    def get_distribution_data(self, column: str, bins: int = 30) -> Dict[str, Any]:
        """Get distribution data for a column"""
        if column in self.numeric_cols:
            hist, bin_edges = np.histogram(self.df[column].dropna(), bins=bins)
            return {
                'type': 'numeric',
                'histogram': {
                    'counts': hist.tolist(),
                    'bin_edges': bin_edges.tolist()
                },
                'stats': {
                    'mean': float(self.df[column].mean()),
                    'median': float(self.df[column].median()),
                    'std': float(self.df[column].std())
                }
            }
        elif column in self.categorical_cols:
            value_counts = self.df[column].value_counts().head(20)
            return {
                'type': 'categorical',
                'value_counts': {
                    'labels': value_counts.index.tolist(),
                    'values': value_counts.values.tolist()
                }
            }
        return {}
    
    def get_group_by_analysis(self, group_col: str, agg_col: str, agg_func: str = 'mean') -> Dict[str, Any]:
        """Perform group-by analysis"""
        if group_col not in self.df.columns or agg_col not in self.numeric_cols:
            return {}
        
        agg_funcs = {
            'mean': 'mean',
            'sum': 'sum',
            'count': 'count',
            'min': 'min',
            'max': 'max',
            'median': 'median'
        }
        
        if agg_func not in agg_funcs:
            agg_func = 'mean'
        
        grouped = self.df.groupby(group_col)[agg_col].agg(agg_funcs[agg_func]).reset_index()
        grouped = grouped.sort_values(agg_col, ascending=False).head(20)
        
        return {
            'groups': grouped[group_col].tolist(),
            'values': grouped[agg_col].round(4).tolist(),
            'agg_function': agg_func
        }
    
    def generate_insights(self) -> List[Dict[str, Any]]:
        """Auto-generate insights from the data"""
        insights = []
        
        # Dataset size insight
        insights.append({
            'type': 'info',
            'icon': 'database',
            'title': 'Dataset Overview',
            'description': f"The dataset contains {len(self.df):,} rows and {len(self.df.columns)} columns, with {len(self.numeric_cols)} numeric and {len(self.categorical_cols)} categorical features."
        })
        
        # Missing values insight
        missing_total = self.df.isnull().sum().sum()
        if missing_total > 0:
            missing_pct = round(missing_total / self.df.size * 100, 2)
            insights.append({
                'type': 'warning',
                'icon': 'alert-triangle',
                'title': 'Missing Values Detected',
                'description': f"Found {missing_total:,} missing values ({missing_pct}% of all data). Consider imputation or removal strategies."
            })
        else:
            insights.append({
                'type': 'success',
                'icon': 'check-circle',
                'title': 'Complete Data',
                'description': "No missing values detected in the dataset. Data quality is excellent."
            })
        
        # Correlation insights
        if len(self.numeric_cols) >= 2:
            corr_data = self.get_correlation_matrix()
            if corr_data['strong_correlations']:
                for corr in corr_data['strong_correlations'][:3]:
                    insights.append({
                        'type': 'trend',
                        'icon': 'trending-up',
                        'title': f"Strong Correlation Found",
                        'description': f"{corr['column1']} and {corr['column2']} have a {corr['strength'].lower()} correlation ({corr['correlation']:.2f}). This suggests a significant relationship between these variables."
                    })
        
        # Outlier insights
        outliers = self.detect_outliers()
        high_outlier_cols = [col for col, data in outliers.items() if data['percentage'] > 5]
        if high_outlier_cols:
            insights.append({
                'type': 'warning',
                'icon': 'alert-circle',
                'title': 'Outliers Detected',
                'description': f"Columns with significant outliers (>5%): {', '.join(high_outlier_cols)}. Consider investigating these anomalies."
            })
        
        # Distribution insights
        for col in self.numeric_cols[:3]:
            skewness = self.df[col].skew()
            if abs(skewness) > 1:
                skew_type = 'positively' if skewness > 0 else 'negatively'
                insights.append({
                    'type': 'info',
                    'icon': 'bar-chart-2',
                    'title': f"Skewed Distribution",
                    'description': f"'{col}' is {skew_type} skewed (skewness: {skewness:.2f}). Consider transformation for modeling."
                })
        
        # Unique values insight for categorical
        for col in self.categorical_cols[:2]:
            unique_count = self.df[col].nunique()
            if unique_count == len(self.df):
                insights.append({
                    'type': 'info',
                    'icon': 'key',
                    'title': 'Potential ID Column',
                    'description': f"'{col}' has all unique values. This might be an identifier column."
                })
            elif unique_count <= 5:
                top_vals = self.df[col].value_counts().head(3)
                vals_str = ', '.join([f"{v}: {c}" for v, c in top_vals.items()])
                insights.append({
                    'type': 'info',
                    'icon': 'list',
                    'title': f"Low Cardinality Feature",
                    'description': f"'{col}' has only {unique_count} unique values. Top values: {vals_str}"
                })
        
        return insights

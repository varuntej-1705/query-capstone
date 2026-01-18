"""
Report Generator Module
Generates HTML and PDF reports from EDA results
"""
import os
import json
from datetime import datetime
from typing import Dict, Any, List
from jinja2 import Template

class ReportGenerator:
    """Generate EDA reports in various formats"""
    
    HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>EDA Report - {{ title }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', system-ui, sans-serif;
            background: #f5f7fa;
            color: #2d3748;
            line-height: 1.6;
            padding: 2rem;
        }
        .container { max-width: 1200px; margin: 0 auto; }
        .header {
            background: linear-gradient(135deg, #3B5998, #00ACC1);
            color: white;
            padding: 2rem;
            border-radius: 12px;
            margin-bottom: 2rem;
        }
        .header h1 { font-size: 2rem; margin-bottom: 0.5rem; }
        .header p { opacity: 0.9; }
        .section {
            background: white;
            border-radius: 12px;
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
        }
        .section h2 {
            color: #3B5998;
            margin-bottom: 1rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #e2e8f0;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 1rem;
        }
        .stat-card {
            background: #f8fafc;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
        }
        .stat-value { font-size: 1.5rem; font-weight: bold; color: #3B5998; }
        .stat-label { font-size: 0.875rem; color: #64748b; }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 1rem;
        }
        th, td {
            padding: 0.75rem;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
        }
        th { background: #f8fafc; font-weight: 600; }
        .insight-card {
            background: #f0f9ff;
            border-left: 4px solid #00ACC1;
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 0 8px 8px 0;
        }
        .insight-card.warning { background: #fffbeb; border-left-color: #f59e0b; }
        .insight-card.success { background: #f0fdf4; border-left-color: #22c55e; }
        .footer {
            text-align: center;
            padding: 2rem;
            color: #64748b;
            font-size: 0.875rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{{ title }}</h1>
            <p>Generated on {{ generated_date }}</p>
        </div>
        
        <div class="section">
            <h2>Dataset Overview</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{{ stats.rows }}</div>
                    <div class="stat-label">Total Rows</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.columns }}</div>
                    <div class="stat-label">Total Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.numeric_cols }}</div>
                    <div class="stat-label">Numeric Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.categorical_cols }}</div>
                    <div class="stat-label">Categorical Columns</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.missing_pct }}%</div>
                    <div class="stat-label">Missing Data</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{{ stats.duplicates }}</div>
                    <div class="stat-label">Duplicates</div>
                </div>
            </div>
        </div>
        
        {% if descriptive_stats %}
        <div class="section">
            <h2>Descriptive Statistics</h2>
            <table>
                <thead>
                    <tr>
                        <th>Column</th>
                        <th>Mean</th>
                        <th>Std</th>
                        <th>Min</th>
                        <th>Max</th>
                        <th>Median</th>
                    </tr>
                </thead>
                <tbody>
                    {% for col, data in descriptive_stats.items() %}
                    {% if data.mean is defined %}
                    <tr>
                        <td>{{ col }}</td>
                        <td>{{ data.mean }}</td>
                        <td>{{ data.std }}</td>
                        <td>{{ data.min }}</td>
                        <td>{{ data.max }}</td>
                        <td>{{ data.median }}</td>
                    </tr>
                    {% endif %}
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% endif %}
        
        {% if correlations %}
        <div class="section">
            <h2>Strong Correlations</h2>
            {% for corr in correlations %}
            <div class="insight-card">
                <strong>{{ corr.column1 }}</strong> ↔ <strong>{{ corr.column2 }}</strong>: 
                {{ corr.correlation }} ({{ corr.strength }})
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        {% if insights %}
        <div class="section">
            <h2>Key Insights</h2>
            {% for insight in insights %}
            <div class="insight-card {{ insight.type }}">
                <strong>{{ insight.title }}</strong><br>
                {{ insight.description }}
            </div>
            {% endfor %}
        </div>
        {% endif %}
        
        <div class="footer">
            <p>Generated by Integrated EDA Application | Capstone Project 2026</p>
        </div>
    </div>
</body>
</html>
    """
    
    @classmethod
    def generate_html_report(
        cls,
        title: str,
        dataset_info: Dict[str, Any],
        descriptive_stats: Dict[str, Any],
        correlation_data: Dict[str, Any],
        insights: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """Generate HTML report"""
        template = Template(cls.HTML_TEMPLATE)
        
        stats = {
            'rows': dataset_info.get('rows', 0),
            'columns': dataset_info.get('columns', 0),
            'numeric_cols': len(dataset_info.get('numeric_columns', [])),
            'categorical_cols': len(dataset_info.get('categorical_columns', [])),
            'missing_pct': round(sum(dataset_info.get('missing_percentage', {}).values()) / 
                                max(len(dataset_info.get('missing_percentage', {})), 1), 2),
            'duplicates': dataset_info.get('duplicates', 0)
        }
        
        html_content = template.render(
            title=title,
            generated_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            stats=stats,
            descriptive_stats=descriptive_stats,
            correlations=correlation_data.get('strong_correlations', []),
            insights=insights
        )
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_path
    
    @classmethod
    def generate_summary_json(
        cls,
        dataset_info: Dict[str, Any],
        descriptive_stats: Dict[str, Any],
        correlation_data: Dict[str, Any],
        insights: List[Dict[str, Any]],
        output_path: str
    ) -> str:
        """Generate JSON summary report"""
        report = {
            'generated_at': datetime.now().isoformat(),
            'dataset_info': dataset_info,
            'descriptive_statistics': descriptive_stats,
            'correlations': correlation_data,
            'insights': insights
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        return output_path
    
    @classmethod
    def generate_csv_summary(
        cls,
        descriptive_stats: Dict[str, Any],
        output_path: str
    ) -> str:
        """Generate CSV summary of statistics"""
        import csv
        
        headers = ['Column', 'Type', 'Count', 'Mean', 'Std', 'Min', 'Max', 'Median', 'Missing']
        rows = []
        
        for col, stats in descriptive_stats.items():
            if 'mean' in stats:
                rows.append([
                    col, 'numeric', stats.get('count', ''),
                    stats.get('mean', ''), stats.get('std', ''),
                    stats.get('min', ''), stats.get('max', ''),
                    stats.get('median', ''), stats.get('missing', '')
                ])
            else:
                rows.append([
                    col, 'categorical', stats.get('count', ''),
                    '', '', '', '',
                    stats.get('top', ''), stats.get('missing', '')
                ])
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(headers)
            writer.writerows(rows)
        
        return output_path

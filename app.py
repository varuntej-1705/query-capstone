"""
Integrated Python-Based Exploratory Data Analysis Application
Main Flask Application
"""
from flask import Flask, render_template, request, jsonify, session, send_file, redirect, url_for
from flask_cors import CORS
import pandas as pd
import numpy as np
import os
import json
import uuid
from datetime import datetime
from werkzeug.utils import secure_filename

from config import Config
from data_processor import DataProcessor
from eda_engine import EDAEngine
from visualization_engine import VisualizationEngine
from report_generator import ReportGenerator

# Initialize Flask app
app = Flask(__name__)
app.config.from_object(Config)
CORS(app)

# In-memory storage for datasets (in production, use Redis or database)
datasets_store = {}


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def get_session_id():
    """Get or create session ID"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']


def get_datasets():
    """Get datasets for current session"""
    session_id = get_session_id()
    if session_id not in datasets_store:
        datasets_store[session_id] = {}
    return datasets_store[session_id]


# ============== PAGE ROUTES ==============

@app.route('/')
def index():
    """Show intro splash screen"""
    return render_template('intro.html')


@app.route('/dashboard/overview')
def dashboard_overview():
    """Dashboard 1: Overview/Home"""
    return render_template('dashboards/overview.html', active='overview')


@app.route('/dashboard/datasets')
def dashboard_datasets():
    """Dashboard 2: Dataset Management"""
    return render_template('dashboards/dataset.html', active='datasets')


@app.route('/dashboard/integration')
def dashboard_integration():
    """Dashboard 3: Data Integration & Cleaning"""
    return render_template('dashboards/integration.html', active='integration')


@app.route('/dashboard/eda')
def dashboard_eda():
    """Dashboard 4: Automated EDA"""
    return render_template('dashboards/eda.html', active='eda')


@app.route('/dashboard/visualization')
def dashboard_visualization():
    """Dashboard 5: Interactive Visualization"""
    return render_template('dashboards/visualization.html', active='visualization')


@app.route('/dashboard/comparison')
def dashboard_comparison():
    """Dashboard 6: Manual vs Automated Comparison"""
    return render_template('dashboards/comparison.html', active='comparison')


@app.route('/dashboard/insights')
def dashboard_insights():
    """Dashboard 7: Insight Summary"""
    return render_template('dashboards/insights.html', active='insights')


@app.route('/dashboard/export')
def dashboard_export():
    """Dashboard 8: Reports & Export"""
    return render_template('dashboards/export.html', active='export')


# ============== API ROUTES ==============

@app.route('/api/upload', methods=['POST'])
def upload_file():
    """Upload a dataset file"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Use CSV or Excel files.'}), 400
        
        filename = secure_filename(file.filename)
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Read and store dataset
        df = DataProcessor.read_file(filepath)
        dataset_id = str(uuid.uuid4())[:8]
        
        datasets = get_datasets()
        datasets[dataset_id] = {
            'name': filename,
            'path': filepath,
            'df': df,
            'uploaded_at': datetime.now().isoformat(),
            'info': DataProcessor.get_dataset_info(df),
            'source_type': DataProcessor.infer_data_source(df)
        }
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'name': filename,
            'info': datasets[dataset_id]['info'],
            'source_type': datasets[dataset_id]['source_type']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/datasets', methods=['GET'])
def list_datasets():
    """List all uploaded datasets"""
    datasets = get_datasets()
    
    result = []
    for dataset_id, data in datasets.items():
        result.append({
            'id': dataset_id,
            'name': data['name'],
            'rows': data['info']['rows'],
            'columns': data['info']['columns'],
            'source_type': data.get('source_type', 'Unknown'),
            'uploaded_at': data['uploaded_at']
        })
    
    return jsonify({'datasets': result})


@app.route('/api/datasets/<dataset_id>', methods=['GET'])
def get_dataset(dataset_id):
    """Get dataset details"""
    datasets = get_datasets()
    
    if dataset_id not in datasets:
        return jsonify({'error': 'Dataset not found'}), 404
    
    data = datasets[dataset_id]
    preview = DataProcessor.get_preview(data['df'])
    
    return jsonify({
        'id': dataset_id,
        'name': data['name'],
        'info': data['info'],
        'preview': preview,
        'source_type': data.get('source_type', 'Unknown')
    })


@app.route('/api/datasets/<dataset_id>', methods=['DELETE'])
def delete_dataset(dataset_id):
    """Delete a dataset"""
    datasets = get_datasets()
    
    if dataset_id not in datasets:
        return jsonify({'error': 'Dataset not found'}), 404
    
    del datasets[dataset_id]
    return jsonify({'success': True})


@app.route('/api/sample-datasets', methods=['GET'])
def list_sample_datasets():
    """List available sample datasets"""
    samples = []
    sample_dir = Config.SAMPLE_DATA_FOLDER
    
    if os.path.exists(sample_dir):
        for filename in os.listdir(sample_dir):
            if filename.endswith(('.csv', '.xlsx')):
                filepath = os.path.join(sample_dir, filename)
                try:
                    df = DataProcessor.read_file(filepath)
                    samples.append({
                        'name': filename,
                        'rows': len(df),
                        'columns': len(df.columns)
                    })
                except:
                    pass
    
    return jsonify({'samples': samples})


@app.route('/api/sample-datasets/<filename>/load', methods=['POST'])
def load_sample_dataset(filename):
    """Load a sample dataset"""
    try:
        filepath = os.path.join(Config.SAMPLE_DATA_FOLDER, secure_filename(filename))
        
        if not os.path.exists(filepath):
            return jsonify({'error': 'Sample dataset not found'}), 404
        
        df = DataProcessor.read_file(filepath)
        dataset_id = str(uuid.uuid4())[:8]
        
        datasets = get_datasets()
        datasets[dataset_id] = {
            'name': filename,
            'path': filepath,
            'df': df,
            'uploaded_at': datetime.now().isoformat(),
            'info': DataProcessor.get_dataset_info(df),
            'source_type': DataProcessor.infer_data_source(df)
        }
        
        return jsonify({
            'success': True,
            'dataset_id': dataset_id,
            'name': filename,
            'info': datasets[dataset_id]['info']
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/common-columns', methods=['GET'])
def get_common_columns():
    """Detect common columns between datasets"""
    datasets = get_datasets()
    
    if len(datasets) < 2:
        return jsonify({'error': 'Need at least 2 datasets to find common columns'}), 400
    
    df_dict = {did: data['df'] for did, data in datasets.items()}
    common = DataProcessor.detect_common_columns(df_dict)
    
    # Format for frontend
    result = []
    for pair, cols in common.items():
        parts = pair.split('__')
        result.append({
            'dataset1': parts[0],
            'dataset1_name': datasets[parts[0]]['name'],
            'dataset2': parts[1],
            'dataset2_name': datasets[parts[1]]['name'],
            'common_columns': cols
        })
    
    return jsonify({'common_columns': result})


@app.route('/api/merge', methods=['POST'])
def merge_datasets():
    """Merge two datasets"""
    try:
        data = request.json
        
        dataset1_id = data.get('dataset1_id')
        dataset2_id = data.get('dataset2_id')
        join_column = data.get('join_column')
        join_type = data.get('join_type', 'inner')
        
        datasets = get_datasets()
        
        if dataset1_id not in datasets or dataset2_id not in datasets:
            return jsonify({'error': 'One or more datasets not found'}), 404
        
        df1 = datasets[dataset1_id]['df']
        df2 = datasets[dataset2_id]['df']
        
        merged_df = DataProcessor.merge_datasets(df1, df2, join_column, join_type)
        
        # Store merged dataset
        merged_id = str(uuid.uuid4())[:8]
        merged_name = f"merged_{datasets[dataset1_id]['name']}_{datasets[dataset2_id]['name']}"
        
        datasets[merged_id] = {
            'name': merged_name,
            'path': None,
            'df': merged_df,
            'uploaded_at': datetime.now().isoformat(),
            'info': DataProcessor.get_dataset_info(merged_df),
            'source_type': 'Merged Dataset'
        }
        
        return jsonify({
            'success': True,
            'dataset_id': merged_id,
            'name': merged_name,
            'info': datasets[merged_id]['info'],
            'preview': DataProcessor.get_preview(merged_df)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/clean', methods=['POST'])
def clean_dataset():
    """Clean a dataset"""
    try:
        data = request.json
        
        dataset_id = data.get('dataset_id')
        missing_strategy = data.get('missing_strategy', 'drop')
        remove_duplicates = data.get('remove_duplicates', False)
        
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df'].copy()
        
        # Handle missing values
        df = DataProcessor.handle_missing_values(df, missing_strategy)
        
        # Remove duplicates
        if remove_duplicates:
            df = DataProcessor.remove_duplicates(df)
        
        # Update dataset
        datasets[dataset_id]['df'] = df
        datasets[dataset_id]['info'] = DataProcessor.get_dataset_info(df)
        
        return jsonify({
            'success': True,
            'info': datasets[dataset_id]['info'],
            'preview': DataProcessor.get_preview(df)
        })
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/eda/<dataset_id>', methods=['GET'])
def run_eda(dataset_id):
    """Run automated EDA on a dataset"""
    try:
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        engine = EDAEngine(df)
        
        result = {
            'descriptive_stats': engine.get_descriptive_statistics(),
            'missing_values': engine.get_missing_value_analysis(),
            'correlations': engine.get_correlation_matrix(),
            'outliers': engine.detect_outliers(),
            'insights': engine.generate_insights()
        }
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/eda/<dataset_id>/distribution/<column>', methods=['GET'])
def get_distribution(dataset_id, column):
    """Get distribution data for a column"""
    try:
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        engine = EDAEngine(df)
        
        return jsonify(engine.get_distribution_data(column))
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/eda/<dataset_id>/groupby', methods=['POST'])
def get_groupby(dataset_id):
    """Get group-by analysis"""
    try:
        data = request.json
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        engine = EDAEngine(df)
        
        result = engine.get_group_by_analysis(
            data.get('group_col'),
            data.get('agg_col'),
            data.get('agg_func', 'mean')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== VISUALIZATION API ==============

@app.route('/api/chart/bar', methods=['POST'])
def create_bar_chart():
    """Create a bar chart"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_bar_chart(
            df,
            x=data.get('x'),
            y=data.get('y'),
            title=data.get('title', 'Bar Chart'),
            color=data.get('color'),
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/line', methods=['POST'])
def create_line_chart():
    """Create a line chart"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_line_chart(
            df,
            x=data.get('x'),
            y=data.get('y'),
            title=data.get('title', 'Line Chart'),
            color=data.get('color'),
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/histogram', methods=['POST'])
def create_histogram():
    """Create a histogram"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_histogram(
            df,
            column=data.get('column'),
            bins=data.get('bins', 30),
            title=data.get('title'),
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/box', methods=['POST'])
def create_box_plot():
    """Create a box plot"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_box_plot(
            df,
            columns=data.get('columns'),
            title=data.get('title', 'Box Plot'),
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/heatmap', methods=['POST'])
def create_heatmap():
    """Create a correlation heatmap"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_correlation_heatmap(
            df,
            title=data.get('title', 'Correlation Matrix'),
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/scatter', methods=['POST'])
def create_scatter_plot():
    """Create a scatter plot"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_scatter_plot(
            df,
            x=data.get('x'),
            y=data.get('y'),
            color=data.get('color'),
            size=data.get('size'),
            title=data.get('title', 'Scatter Plot'),
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chart/missing', methods=['POST'])
def create_missing_chart():
    """Create a missing values chart"""
    try:
        data = request.json
        datasets = get_datasets()
        
        dataset_id = data.get('dataset_id')
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        engine = EDAEngine(df)
        missing_data = engine.get_missing_value_analysis()
        dark_mode = data.get('dark_mode', False)
        
        chart_json = VisualizationEngine.create_missing_value_chart(
            missing_data,
            dark_mode=dark_mode
        )
        
        return jsonify({'chart': json.loads(chart_json)})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ============== REPORT API ==============

@app.route('/api/report/html/<dataset_id>', methods=['GET'])
def generate_html_report(dataset_id):
    """Generate and download HTML report"""
    try:
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        data = datasets[dataset_id]
        df = data['df']
        engine = EDAEngine(df)
        
        output_path = os.path.join(
            Config.EXPORT_FOLDER,
            f"eda_report_{dataset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        )
        
        ReportGenerator.generate_html_report(
            title=f"EDA Report: {data['name']}",
            dataset_info=data['info'],
            descriptive_stats=engine.get_descriptive_statistics(),
            correlation_data=engine.get_correlation_matrix(),
            insights=engine.generate_insights(),
            output_path=output_path
        )
        
        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/report/json/<dataset_id>', methods=['GET'])
def generate_json_report(dataset_id):
    """Generate and download JSON report"""
    try:
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        data = datasets[dataset_id]
        df = data['df']
        engine = EDAEngine(df)
        
        output_path = os.path.join(
            Config.EXPORT_FOLDER,
            f"eda_report_{dataset_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        
        ReportGenerator.generate_summary_json(
            dataset_info=data['info'],
            descriptive_stats=engine.get_descriptive_statistics(),
            correlation_data=engine.get_correlation_matrix(),
            insights=engine.generate_insights(),
            output_path=output_path
        )
        
        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/export/csv/<dataset_id>', methods=['GET'])
def export_csv(dataset_id):
    """Export cleaned dataset as CSV"""
    try:
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        data = datasets[dataset_id]
        output_path = os.path.join(
            Config.EXPORT_FOLDER,
            f"cleaned_{data['name']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )
        
        data['df'].to_csv(output_path, index=False)
        
        return send_file(output_path, as_attachment=True)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/overview/stats', methods=['GET'])
def get_overview_stats():
    """Get overview statistics for home dashboard"""
    datasets = get_datasets()
    
    total_rows = 0
    total_cols = 0
    source_types = set()
    
    for data in datasets.values():
        total_rows += data['info']['rows']
        total_cols += data['info']['columns']
        source_types.add(data.get('source_type', 'Unknown'))
    
    return jsonify({
        'total_datasets': len(datasets),
        'total_rows': total_rows,
        'total_columns': total_cols,
        'source_types': list(source_types)
    })


@app.route('/api/health-score/<dataset_id>', methods=['GET'])
def get_health_score(dataset_id):
    """Get data health score for a dataset"""
    try:
        datasets = get_datasets()
        
        if dataset_id not in datasets:
            return jsonify({'error': 'Dataset not found'}), 404
        
        df = datasets[dataset_id]['df']
        health_score = DataProcessor.calculate_health_score(df)
        
        return jsonify(health_score)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("=" * 50)
    print("🚀 Starting EDA Application")
    print("=" * 50)
    print(f"📂 Upload Folder: {Config.UPLOAD_FOLDER}")
    print(f"📂 Export Folder: {Config.EXPORT_FOLDER}")
    print(f"📂 Sample Data: {Config.SAMPLE_DATA_FOLDER}")
    print("=" * 50)
    print("🌐 Open http://localhost:5000 in your browser")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)

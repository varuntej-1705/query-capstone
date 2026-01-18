/**
 * EDA Application - Chart Utilities
 * Plotly-based chart rendering with theme support
 */

// ============== CHART THEME ==============
const chartTheme = {
    light: {
        bg: '#F5F7FA',
        paper: '#FFFFFF',
        text: '#2D3748',
        grid: '#E2E8F0'
    },
    dark: {
        bg: '#1A1F3C',
        paper: '#252B48',
        text: '#E2E8F0',
        grid: '#3D4566'
    },
    colors: [
        '#3B5998', '#00ACC1', '#FF6D00', '#9C27B0',
        '#4CAF50', '#FF5722', '#607D8B', '#E91E63',
        '#00BCD4', '#8BC34A', '#FFC107', '#795548'
    ]
};

// ============== DEFAULT LAYOUT ==============
function getChartLayout(title = '', darkMode = false) {
    const theme = darkMode ? chartTheme.dark : chartTheme.light;

    return {
        title: {
            text: title,
            font: { size: 16, color: theme.text },
            x: 0.5,
            xanchor: 'center'
        },
        paper_bgcolor: theme.paper,
        plot_bgcolor: theme.bg,
        font: {
            color: theme.text,
            family: 'Inter, system-ui, sans-serif'
        },
        margin: { l: 60, r: 40, t: 60, b: 60 },
        xaxis: {
            gridcolor: theme.grid,
            zerolinecolor: theme.grid,
            tickfont: { color: theme.text }
        },
        yaxis: {
            gridcolor: theme.grid,
            zerolinecolor: theme.grid,
            tickfont: { color: theme.text }
        },
        legend: {
            bgcolor: 'rgba(0,0,0,0)',
            font: { color: theme.text }
        },
        colorway: chartTheme.colors
    };
}

// ============== CHART RENDERING ==============
function renderPlotlyChart(containerId, chartData) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const darkMode = window.EDA.darkMode;
    const layout = getChartLayout(chartData.layout?.title?.text || '', darkMode);

    // Merge with chart-specific layout
    const finalLayout = { ...layout, ...chartData.layout };

    // Update theme colors
    finalLayout.paper_bgcolor = darkMode ? chartTheme.dark.paper : chartTheme.light.paper;
    finalLayout.plot_bgcolor = darkMode ? chartTheme.dark.bg : chartTheme.light.bg;

    const config = {
        responsive: true,
        displayModeBar: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        toImageButtonOptions: {
            format: 'png',
            filename: 'eda_chart',
            height: 600,
            width: 800,
            scale: 2
        }
    };

    Plotly.newPlot(container, chartData.data, finalLayout, config);
}

// ============== UPDATE CHARTS THEME ==============
function updateChartsTheme(darkMode) {
    // Find all Plotly charts and update their theme
    document.querySelectorAll('.js-plotly-plot').forEach(chart => {
        const theme = darkMode ? chartTheme.dark : chartTheme.light;

        Plotly.relayout(chart, {
            'paper_bgcolor': theme.paper,
            'plot_bgcolor': theme.bg,
            'font.color': theme.text,
            'xaxis.gridcolor': theme.grid,
            'yaxis.gridcolor': theme.grid,
            'xaxis.tickfont.color': theme.text,
            'yaxis.tickfont.color': theme.text
        });
    });
}

// ============== CREATE BAR CHART ==============
async function createBarChart(containerId, datasetId, x, y, title = 'Bar Chart', color = null) {
    showLoading();
    try {
        const result = await apiPost('/api/chart/bar', {
            dataset_id: datasetId,
            x: x,
            y: y,
            title: title,
            color: color,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create bar chart:', error);
    }
    hideLoading();
}

// ============== CREATE LINE CHART ==============
async function createLineChart(containerId, datasetId, x, y, title = 'Line Chart', color = null) {
    showLoading();
    try {
        const result = await apiPost('/api/chart/line', {
            dataset_id: datasetId,
            x: x,
            y: y,
            title: title,
            color: color,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create line chart:', error);
    }
    hideLoading();
}

// ============== CREATE HISTOGRAM ==============
async function createHistogram(containerId, datasetId, column, title = null, bins = 30) {
    showLoading();
    try {
        const result = await apiPost('/api/chart/histogram', {
            dataset_id: datasetId,
            column: column,
            title: title,
            bins: bins,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create histogram:', error);
    }
    hideLoading();
}

// ============== CREATE BOX PLOT ==============
async function createBoxPlot(containerId, datasetId, columns = null, title = 'Box Plot') {
    showLoading();
    try {
        const result = await apiPost('/api/chart/box', {
            dataset_id: datasetId,
            columns: columns,
            title: title,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create box plot:', error);
    }
    hideLoading();
}

// ============== CREATE HEATMAP ==============
async function createHeatmap(containerId, datasetId, title = 'Correlation Matrix') {
    showLoading();
    try {
        const result = await apiPost('/api/chart/heatmap', {
            dataset_id: datasetId,
            title: title,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create heatmap:', error);
    }
    hideLoading();
}

// ============== CREATE SCATTER PLOT ==============
async function createScatterPlot(containerId, datasetId, x, y, color = null, size = null, title = 'Scatter Plot') {
    showLoading();
    try {
        const result = await apiPost('/api/chart/scatter', {
            dataset_id: datasetId,
            x: x,
            y: y,
            color: color,
            size: size,
            title: title,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create scatter plot:', error);
    }
    hideLoading();
}

// ============== CREATE MISSING VALUES CHART ==============
async function createMissingChart(containerId, datasetId) {
    showLoading();
    try {
        const result = await apiPost('/api/chart/missing', {
            dataset_id: datasetId,
            dark_mode: window.EDA.darkMode
        });

        if (result.chart) {
            renderPlotlyChart(containerId, result.chart);
        }
    } catch (error) {
        console.error('Failed to create missing values chart:', error);
    }
    hideLoading();
}

// ============== CREATE SIMPLE CHART LOCALLY ==============
function createLocalBarChart(containerId, labels, values, title = 'Chart') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const darkMode = window.EDA.darkMode;
    const layout = getChartLayout(title, darkMode);

    const data = [{
        type: 'bar',
        x: labels,
        y: values,
        marker: {
            color: chartTheme.colors[0],
            opacity: 0.9
        }
    }];

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot(container, data, layout, config);
}

function createLocalPieChart(containerId, labels, values, title = 'Chart') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const darkMode = window.EDA.darkMode;
    const theme = darkMode ? chartTheme.dark : chartTheme.light;

    const data = [{
        type: 'pie',
        labels: labels,
        values: values,
        hole: 0.4,
        marker: {
            colors: chartTheme.colors
        },
        textfont: { color: theme.text }
    }];

    const layout = {
        title: {
            text: title,
            font: { size: 16, color: theme.text }
        },
        paper_bgcolor: theme.paper,
        font: { color: theme.text },
        showlegend: true,
        legend: {
            font: { color: theme.text }
        }
    };

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot(container, data, layout, config);
}

function createLocalLineChart(containerId, x, y, title = 'Chart') {
    const container = document.getElementById(containerId);
    if (!container) return;

    const darkMode = window.EDA.darkMode;
    const layout = getChartLayout(title, darkMode);

    const data = [{
        type: 'scatter',
        mode: 'lines+markers',
        x: x,
        y: y,
        line: { color: chartTheme.colors[0], width: 2 },
        marker: { size: 6 }
    }];

    const config = {
        responsive: true,
        displayModeBar: false
    };

    Plotly.newPlot(container, data, layout, config);
}

// ============== EXPORTS ==============
window.renderPlotlyChart = renderPlotlyChart;
window.updateChartsTheme = updateChartsTheme;
window.createBarChart = createBarChart;
window.createLineChart = createLineChart;
window.createHistogram = createHistogram;
window.createBoxPlot = createBoxPlot;
window.createHeatmap = createHeatmap;
window.createScatterPlot = createScatterPlot;
window.createMissingChart = createMissingChart;
window.createLocalBarChart = createLocalBarChart;
window.createLocalPieChart = createLocalPieChart;
window.createLocalLineChart = createLocalLineChart;
window.chartTheme = chartTheme;

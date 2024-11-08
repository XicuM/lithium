import config as p
import datetime as dt

from dash import Dash, dcc, html, Input, Output, callback
import dash_bootstrap_components as dbc
import plotly.graph_objects as go

from src.Monitor import CANMonitor, FileMonitor, ROSMonitor, ROSFileMonitor
from src.Saver import Saver

# ----------------------------------------------------------------------
# Styles

colors = {
    'background': '#FFFFFF',
    'on_background': '#1A1C1E',
    'surface': '#F9F9F9',
    'primary': '#004787',
    'primary_container': '#D5E3FF',
    'secondary': '#984715',
    'secondary_container': '#FFDBCB',
    'highlight': '#BA1A1A',
    'highlight_container': '#FFB4AB'
}

h2_style = {
    'color': colors['on_background'],
    'fontSize': '24px'
}

card_style = {
    'backgroundColor': colors['background'],
    'padding': '16px',
    'margin': '16px',
}

monitor_type = 'File'

match monitor_type:
    case 'File':
        monitor = FileMonitor('data/20240809_2013.csv')
        pass
    case 'File (ROS)':
        #m = ROSFileMonitor('data/20240508_1700.csv')
        pass
    case 'Charger (CAN)':
        #m = CANMonitor()
        pass
    case 'Car (ROS)':
        #m = ROSMonitor()
        pass
    case _:
        raise ValueError('Invalid monitor type')
    
#s = Saver(m := CANMonitor())


# ----------------------------------------------------------------------
# Layout

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])
app.layout = html.Div([
    
    # Header
    html.Header(
        [
            html.H1(
                'Lithium', 
                style={
                    'color': colors['primary'],
                    'fontSize': '32px'
                }
            ),
            dcc.Markdown(
                'Created by [Xicu Marí](hello@xicu.info)',
                style={
                    'color': colors['primary'],
                    'fontSize': '16px'
                }
            )
        ], style={
            'backgroundColor': colors['primary_container'],
            'padding': '16px'
        }
    ),

    dcc.Store(id='alert-store', data=''),

    # Configuration
    html.Div(
        [
            html.H2(
                'Configuration', 
                style={
                    'color': colors['on_background'],
                    'fontSize': '24px',
                    'padding-bottom': '8px'
                }
            ),

            html.Label('Monitor type: '),
            dcc.Dropdown(
                ['File (CAN)', 'File (ROS)', 'Car (ROS)', 'Charger (CAN)'], 
                'File'
            ),

            html.Label('Filename: '),
            dcc.Textarea(
                id='filename', 
                value=dt.datetime.now().strftime('%Y%m%d_%H%M')+'.csv'
            ), 

            html.Button(
                'Start', id='start-button', n_clicks=0
            ),
            html.Button(
                'Stop', id='stop-button', n_clicks=0
            ),
            
            dcc.Checklist(
                [' Save data']
            )
        ], style=card_style
    ),

    # Plot 1
    dcc.Graph(id='cell_voltages_plot', style=card_style),
    
    # Plot 2
    dcc.Graph(id='battery_voltages_plot', style=card_style),
    
    # Plot 3
    dcc.Graph(id='cell_temperatures_plot', style=card_style),
    
    # Plot 4
    dcc.Graph(id='battery_temperatures_plot', style=card_style),

    # Interval
    dcc.Interval(
        id='interval_component',
        interval=1000, # in milliseconds
        n_intervals=0
    )
    ], style={'backgroundColor': colors['surface']}
)


# ----------------------------------------------------------------------
# Voltage plot

voltage_plot = go.Figure()
voltage_plot.update(
    layout_title='Cell voltages',
    layout_yaxis_title='Voltage [V]',
    layout_yaxis_range=[p.V_CELL_MIN, p.V_CELL_MAX],
    layout_uirevision=True
)

@callback(
    Output('cell_voltages_plot', 'figure'),
    Input('interval_component', 'n_intervals')
)
def update_cell_voltages_plot(_):

    # Do not update if monitor is offline
    if not monitor.is_online(): return voltage_plot

    data = monitor.get_data()
    voltage_plot.data = []
    for i in p.RANGE_STACKS:
        cell_names = []
        cell_voltages = []
        for j in p.RANGE_SPIS:
            for k in p.RANGE_CELLS:
                cell_name = f'Cell{k}_s{i}_spi{j}'
                if cell_name not in [
                    'Cell14_s1_spi2',
                    'Cell14_s2_spi3',
                    'Cell14_s3_spi2',
                    'Cell14_s4_spi3',
                    'Cell14_s5_spi2'
                ]:
                    cell_names.append(cell_name)
                    cell_voltages.append(data[cell_name])
        voltage_plot.add_trace(go.Scatter(
            x=cell_names, 
            y=cell_voltages, 
            name=f'Stack {i}',
            mode='markers'
        ))
    return voltage_plot

# ----------------------------------------------------------------------
# Battery voltages plot

# @callback(
#     Output('battery_voltages_plot', 'figure'),
#     Input('interval_component', 'n_intervals')
# )
# def update_battery_voltage_plot(_):
#     data = m.get_data()
#     fig = go.Figure()
#     for i in p.RANGE_STACKS:
#         for j in p.RANGE_SPIS:
#             for k in p.RANGE_CELLS:
#                 vcell = data[f'Cell{k}_s{i}_spi{j}']
#                 if not np.isnan(vcell):
#                     fig.add_shape(type='rect',
#                         x0=0, y0=0, x1=1, y1=1,
#                         line=dict(color='RoyalBlue', width=2),
#                         fillcolor='LightSkyBlue',
#                     )
#     fig.update(
#         layout_title='Cell voltages',
#         layout_uirevision=True
#     )
#     return fig

# ----------------------------------------------------------------------
# Temperature plot

temperature_plot = go.Figure()
temperature_plot.update(
    layout_title='Cell temperatures',
    layout_yaxis_title='Temperature [ºC]',
    layout_yaxis_range=[20, 50],
    layout_uirevision=True
)

@callback(
    Output('cell_temperatures_plot', 'figure'),
    Input('interval_component', 'n_intervals')
)
def update_temperature_plot(_):

    # Do not update if monitor is offline
    if not monitor.is_online(): return temperature_plot

    data = monitor.get_data()
    temperature_plot.data = []
    for i in p.RANGE_STACKS:
        ntc_names = []
        ntc_temps = []
        for j in p.RANGE_SPIS:
            for k in range(1,5): #p.RANGE_NTCS: TODO Change when data is reliable
                ntc_name = f'ntc{k}_slave{i}_spi{j}'
                ntc_names.append(ntc_name)
                ntc_temps.append(data[ntc_name])
        temperature_plot.add_trace(go.Scatter(
            x=ntc_names,
            y=ntc_temps,
            name=f'Stack {i}',
            mode='markers'
        ))
    return temperature_plot

# ----------------------------------------------------------------------
# Battery temperatures plot

# @callback(
#     Output('battery_temperatures_plot', 'figure'),
#     Input('interval_component', 'n_intervals')
# )
# def update_battery_temperatures_plot(_):
#     pass


# ----------------------------------------------------------------------
# Buttons behavior

@callback(
    Output('alert-store', 'data'),
    Input('stop-button', 'n_clicks')
)
def start():
    if monitor is None: 
        return 'Monitor not started'
    
    match monitor_type:
        case 'File': monitor = FileMonitor('data/20240809_2013.csv')
        case 'File (ROS)': monitor = ROSFileMonitor('data/20240508_1700.csv')
        case 'Charger (CAN)': monitor = CANMonitor()
        case _: raise ValueError('Invalid monitor type')

    monitor.start()
    return None

@callback(
    Output('alert-store', 'data'),
    Input('stop-button', 'n_clicks')
)
def stop():
    if monitor is None: 
        return 'Monitor not started'
    monitor.stop()
    return None


# ----------------------------------------------------------------------
# Run

if __name__ == '__main__': app.run()
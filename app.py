"""
This APP simulates first order batch reactions
"""
from dash import Dash, dcc, html, dash_table, dependencies
import dash_bootstrap_components as dbc
from dash.exceptions import PreventUpdate
from scipy.integrate import odeint
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import os

app = Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server      #exposes server of dash app as an objective that gunicorn can pick
app.title = 'Conor\'s WebApp'  # set the title to appear in the tab

NumberofSolutionSteps = 100
StartingResults = np.zeros([NumberofSolutionSteps, 5])
ResultsDataFrame = pd.DataFrame(data=StartingResults, columns=['time', 'A', 'B', 'C', 'D'])

def BatchRXR1stOrderFun(DiffVariables, Time, ReactorConditions, RXNOrders, Parameters):
    CA = DiffVariables[0]  # mol/L
    CB = DiffVariables[1]  # mol/L
    CC = DiffVariables[2]  # mol/L
    CD = DiffVariables[3]  # mol/L

    k0 = Parameters[0]  # mol/L s
    Ea = Parameters[1]  # J/mol
    T = ReactorConditions[0] + 273.15  # K
    RateConstant = k0 * np.exp(-Ea / (8.3145 * T))  # mol/L s
    rate = RateConstant * (CA ** RXNOrders[0]) * (CB ** RXNOrders[1])

    dCAdt = -rate
    dCBdt = -rate
    dCCdt = +rate
    dCDdt = +rate
    return [dCAdt, dCBdt, dCCdt, dCDdt]

#defining styling for diffferenet components
SIDEBAR_STYLE = {
    "position": "fixed",
    "top": 0,
    "left": 0,
    "bottom": 0,
    "width": "20rem",
    "padding": "2rem 1rem",
    "background-color": "#f8f9fa",
}

CONTENT_STYLE = {
    "margin-left": "20rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

BUTTON_STYLE = {
    'background-color': '#74C042',
    'border-color': '#FFFFFF',
    'color': '#FFFFFF',
    'display': 'block'
}

TEXT_STYLE = {
    'textAlign': 'center',
    'color': '#74C042'
}

#We can define some layout items now, and then use them later on
ReactionConditionMainBody = html.Div(
    [
    #  Below we use subdivs to make text appear on the same line as the Input core component
    html.Div(['Reactor Temperature (°C)',
                  dcc.Input(id='RXRTEMP', value=50, type='number', min=-50, max=1000), ]),
    html.Div(['Simulation Duration (min):',
                  dcc.Input(id='TotalTime', value=100, type='number', min=0.001, max=1000), ]),
    html.Div(['Starting Concentration of A (mol/L):',
              dcc.Input(id='InitialConcA', value = 5, type='number', min=0.001, max=1000),]),
    html.Div(['Starting Concentration of B (mol/L):',
              dcc.Input(id='InitialConcB', value = 7, type='number', min=0.001, max=1000),]),
    html.Div(['Starting Concentration of C (mol/L)',
              dcc.Input(id='InitialConcC', value = 0.5, type='number', min=-0.001, max=1000),]),
    html.Div(['Starting Concentration of D (mol/L)',
              dcc.Input(id='InitialConcD', value = 0, type='number', min=-0.001, max=1000),]),
    html.Br()
    ]
)

ReactionConditionCollapse = html.Div(
    [
        dbc.Button(
           "Reactor Conditions",
            id='Collapse_button_RXNCondition',
            className='mb-3',
            style=BUTTON_STYLE,
        ),
        dbc.Collapse(
            ReactionConditionMainBody,
            id="collapse_body_RXNCondition",
        ),
    ]
)

ReactionOrdersMainBody = html.Div(
    [
    html.Div(['Reaction Order of Species A',
            dcc.RadioItems(
                id='RXNOrderA',
                options=[
                    {'label': '0th Order    ', 'value': 0},
                    {'label': '1st Order    ', 'value': 1},
                    {'label': '2nd Order    ', 'value': 2}
                      ],
                value=1,
                labelStyle={'display': 'inline-block'},
                inputStyle={"margin-left": "10px"}  #adds spacing around radio options
                    )
                ]),
    html.Div(['Reaction Order of Species B',
            dcc.RadioItems(
                id='RXNOrderB',
                options=[
                    {'label': '0th Order    ', 'value': 0},
                    {'label': '1st Order    ', 'value': 1},
                    {'label': '2nd Order    ', 'value': 2}
                      ],
                value=1,
                labelStyle={'display': 'inline-block'},
                inputStyle={"margin-left": "10px"}  #adds spacing around radio options
                )
            ]),
    ]
)

ReactionOrdersCollapse = html.Div(
    [
        dbc.Button(
           "Reactor Orders",
            id='Collapse_button_RXNCOrders',
            className='mb-3',
            style=BUTTON_STYLE,
        ),
        dbc.Collapse(
            ReactionOrdersMainBody,
            id="collapse_body_RXNOrders",
        ),
    ]
)

KineticParametersMainBody = html.Div(
    [
    html.Div(['Preexponential Factor',
            dcc.Slider(
                id='PreExpSlider',
                min=-6,
                max=6,
                step=0.01,
                value=2,
                marks={i: '{}'.format(10 ** i) for i in [-6, -3, 0, 3, 6]},
                ),
    html.Div(id='PreExpslider-output-container'),
              ]),
    html.Div(['Activation Energy',
            dcc.Slider(
                id='EaSlider',
                min=0,
                max=100,
                step=0.1,
                value=30,
                marks={
                    0:{'label':'0 kJ/mol'},
                    50:{'label':'50 kJ/mol'},
                    100:{'label':'100 kJ/mol'}
                }
                ),
    html.Div(id='Easlider-output-container'),
              ]),
    ]
)

KineticParametersCollapse = html.Div(
    [
        dbc.Button(
           "Kinetic Parameters",
            id='Collapse_button_KineticParameters',
            className='mb-3',
            style=BUTTON_STYLE,
        ),
        dbc.Collapse(
            KineticParametersMainBody,
            id="collapse_body_KineticParameters",
        ),
    ]
)

DashTableMainBody = html.Div(
    [
    dash_table.DataTable(
        id='ResultsTable',
        columns=[{"name": i, "id": i} for i in ResultsDataFrame.columns],
        data=ResultsDataFrame.to_dict('records'),
        )
    ]
)

DashTableCollapse = html.Div(
    [
        dbc.Button(
            "Show/Hide Table Results on Screen",
            id='Collapse_button_Table',
            className='mb-3',
            style=BUTTON_STYLE,
        ),
        dbc.Collapse(
            DashTableMainBody,
            id="collapse_body_Table",
        ),
    ]
)

APC_info_card = dbc.Card(
    html.Div(
        [
            dbc.CardBody(
                [
                html.P("To find out more about Conor's kinetic modelling capabilities, visit the link below", className="card-text"),
                dbc.CardLink("Conor's Google Scholar", href="https://scholar.google.co.uk/citations?user=Rno4e94AAAAJ&hl=en&oi=ao"),
                ]
            ),
            #dbc.CardImg(src="https://i.postimg.cc/YqYtPMNP/IMG-4262.jpg", top=True, style={'height': '65%', 'width': '65%'}),
            dbc.CardImg(src="assets/conor.jfif", top=True, style={'height': '65%', 'width': '65%'}),
        ],
        style={'textAlign': 'center'},
    )
)

# you can provide images from local files or url to the internet
instruct_tab = dbc.Card(
        html.Div(
            [
            #dbc.CardImg(src="https://i.postimg.cc/wBxrRxy9/batch-reactor-image.png", top=True, style={'height':'65%', 'width':'65%'}),
            dbc.CardImg(src='assets/batch-reactor-image.png', top=True, style={'height':'65%', 'width':'65%'}),
            dbc.CardBody(html.P("Diagram and photo of typical batch reactors", className="card-text")),
            ],
            style={'textAlign': 'center'},
        )
)

sidebar = html.Div(
    [
    ReactionConditionCollapse,
    ReactionOrdersCollapse,
    KineticParametersCollapse,
    APC_info_card
    ],
    style=SIDEBAR_STYLE,
)

content = html.Div(
    [
    html.H2("WebApp for Simulating Batch Reactions", style=TEXT_STYLE),
    html.Br(),
    html.Div(
        [
            html.P('Show the following Species in the Plot'),
            dcc.Checklist(
                id='PlotCheckBoxes',
                options=[
                    {'label': 'Species A', 'value': 'A'},
                    {'label': 'Species B', 'value': 'B'},
                    {'label': 'Species C', 'value': 'C'},
                    {'label': 'Species D', 'value': 'D'},
                ],
                inputStyle={"margin-left": "20px", "margin-right": "5px"},  # adds spacing around radio options

                value=['A', 'B']
            ),
        ]
    ),

    html.Br(),
    html.Div(
        [
            html.Button(id='UpdateButton', n_clicks=0, children='Update Graph & Table'),
            html.Button(id='DownLoadButton', n_clicks=0, children='Download Table'),
        ]
    ),
    dcc.Graph(id='kineticgraph'),  # here you are passing figure object to dcc.Graph
    dcc.Download(id="download"),
    DashTableCollapse,
    instruct_tab,

    ],
    style=CONTENT_STYLE,
)

app.layout = html.Div([sidebar, content])

@app.callback(
    dependencies.Output(component_id='collapse_body_KineticParameters', component_property='is_open'),
    [dependencies.Input(component_id='Collapse_button_KineticParameters', component_property='n_clicks')],
    [dependencies.State(component_id='collapse_body_KineticParameters', component_property='is_open')],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    dependencies.Output(component_id='collapse_body_RXNCondition', component_property='is_open'),
    [dependencies.Input(component_id='Collapse_button_RXNCondition', component_property='n_clicks')],
    [dependencies.State(component_id='collapse_body_RXNCondition', component_property='is_open')],
)

def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    dependencies.Output(component_id='collapse_body_RXNOrders', component_property='is_open'),
    [dependencies.Input(component_id='Collapse_button_RXNCOrders', component_property='n_clicks')],
    [dependencies.State(component_id='collapse_body_RXNOrders', component_property='is_open')],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    dependencies.Output(component_id='collapse_body_Table', component_property='is_open'),
    [dependencies.Input(component_id='Collapse_button_Table', component_property='n_clicks')],
    [dependencies.State(component_id='collapse_body_Table', component_property='is_open')],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open

@app.callback(
    dependencies.Output(component_id='PreExpslider-output-container', component_property='children'),
    [dependencies.Input(component_id='PreExpSlider', component_property='value')])
def UpdatePreExpSlider(value):
    transfromedvalue = 10 ** value
    return 'You have selected "{}" mol/L s'.format(transfromedvalue)

@app.callback(
    dependencies.Output(component_id='Easlider-output-container', component_property='children'),
    [dependencies.Input(component_id='EaSlider', component_property='value')])
def UpdateEaSlider(value):
    return 'You have selected "{}" kJ/mol'.format(value)

@app.callback(
    dependencies.Output(component_id='kineticgraph', component_property='figure'),
    dependencies.Output(component_id='ResultsTable', component_property='data'),
    dependencies.Input(component_id='UpdateButton', component_property='n_clicks'),
    dependencies.State(component_id='InitialConcA', component_property='value'),
    dependencies.State(component_id='InitialConcB', component_property='value'),
    dependencies.State(component_id='InitialConcC', component_property='value'),
    dependencies.State(component_id='InitialConcD', component_property='value'),
    dependencies.State(component_id='RXRTEMP', component_property='value'),
    dependencies.State(component_id='TotalTime', component_property='value'),
    dependencies.State(component_id='RXNOrderA', component_property='value'),
    dependencies.State(component_id='RXNOrderB', component_property='value'),
    dependencies.State(component_id='PreExpSlider', component_property='value'),
    dependencies.State(component_id='EaSlider', component_property='value'),
    dependencies.State(component_id='PlotCheckBoxes', component_property='value'),
)
def Mycallbackfunction(nclickslocal, Ca0, Cb0, Cc0, Cd0, TRXR, SimTime, OrderA, OrderB, PreExpFlinear, EaValuekJmol, CheckBoxValues):
    ExpTimes = np.linspace(0, SimTime, NumberofSolutionSteps) #min
    InitialConcentrations = [Ca0, Cb0, Cc0, Cd0] #mol/L
    Temp=[TRXR] #oC
    RXNO = [OrderA, OrderB]
    KineticP = [10**PreExpFlinear, EaValuekJmol*1000] #mol/L s, J/mol
    soln = odeint(BatchRXR1stOrderFun, InitialConcentrations, ExpTimes, args=(Temp, RXNO, KineticP,))
    fig1 = go.Figure()
    for i in range(0, len(CheckBoxValues)):
        if CheckBoxValues[i] == 'A':
            fig1.add_trace(go.Scatter(x=ExpTimes, y=soln[:,0], mode='lines', name='Conc A'))
        elif CheckBoxValues[i] == 'B':
            fig1.add_trace(go.Scatter(x=ExpTimes, y=soln[:,1], mode='lines', name='Conc B'))
        elif CheckBoxValues[i] == 'C':
            fig1.add_trace(go.Scatter(x=ExpTimes, y=soln[:,2], mode='lines', name='Conc C'))
        elif CheckBoxValues[i] == 'D':
            fig1.add_trace(go.Scatter(x=ExpTimes, y=soln[:,3], mode='lines', name='Conc D'))
    UpdatedResults = np.zeros([NumberofSolutionSteps, 5])
    for i in range(0, NumberofSolutionSteps):
        UpdatedResults[i]=[ExpTimes[i], soln[i,0], soln[i,1], soln[i,2], soln[i,3]]
    MyDataSetLocal = pd.DataFrame(data=UpdatedResults, columns = ['time', 'A', 'B', 'C', 'D'])

    return fig1, MyDataSetLocal.to_dict('records')

@app.callback(
    dependencies.Output(component_id="download", component_property="data"),
    dependencies.Input(component_id="DownLoadButton", component_property="n_clicks"),
    dependencies.State(component_id='InitialConcA', component_property='value'),
    dependencies.State(component_id='InitialConcB', component_property='value'),
    dependencies.State(component_id='InitialConcC', component_property='value'),
    dependencies.State(component_id='InitialConcD', component_property='value'),
    dependencies.State(component_id='RXRTEMP', component_property='value'),
    dependencies.State(component_id='TotalTime', component_property='value'),
    dependencies.State(component_id='RXNOrderA', component_property='value'),
    dependencies.State(component_id='RXNOrderB', component_property='value'),
    dependencies.State(component_id='PreExpSlider', component_property='value'),
    dependencies.State(component_id='EaSlider', component_property='value'),
)
def func(nclickslocal, Ca0, Cb0, Cc0, Cd0, TRXR, SimTime, OrderA, OrderB, PreExpFlinear, EaValuekJmol):
    if nclickslocal == 0:
        raise PreventUpdate
    else:
        ExpTimes = np.linspace(0, SimTime, NumberofSolutionSteps)  # min
        InitialConcentrations = [Ca0, Cb0, Cc0, Cd0]  # mol/L
        Temp = [TRXR]  # oC
        RXNO = [OrderA, OrderB]
        KineticP = [10 ** PreExpFlinear, EaValuekJmol * 1000]  # mol/L s, J/mol
        soln = odeint(BatchRXR1stOrderFun, InitialConcentrations, ExpTimes, args=(Temp, RXNO, KineticP,))

        UpdatedResults = np.zeros([NumberofSolutionSteps, 5])
        for i in range(0, NumberofSolutionSteps):
            UpdatedResults[i] = [ExpTimes[i], soln[i, 0], soln[i, 1], soln[i, 2], soln[i, 3]]
        MyDataSetLocal = pd.DataFrame(data=UpdatedResults, columns=['time (min)', 'A (mol/L)', 'B (mol/L)', 'C (mol/L)', 'D (mol/L'])
        return dcc.send_data_frame(MyDataSetLocal.to_excel, "WebApp_Batch_Simulation.xls")

if __name__ == '__main__':
    #app.run_server()  # Set debug to true makes webapp automatically update, when user clicks refresh
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
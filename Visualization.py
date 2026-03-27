from dash import Dash, html, dash_table, dcc, Input, Output, callback
import dash_ag_grid as dag
import pandas as pd

# Incorporate data
df = pd.read_csv('https://raw.githubusercontent.com/julianikitina-14/Junior-DE-test-task/refs/heads/main/countries_data.csv')

columnDefs = [
    {"field": "country_name"},
    {"field": "country_official_name"},
    {"field": "capital"},
    {"field": "continents"},
    {"field": "flag_desc"},
    {"field": "flag_png"},
    {"field": "population"},
]

# Initialize the app
app = Dash()

# App layout
app.layout = html.Div([# The main one
    html.Div([ # for Flexbox to display table and flag image in one row
          
        # Table with countries
        html.Div([
            dcc.Markdown("### Countries Data"),
            dag.AgGrid(
                id="countries_table",
                columnDefs=columnDefs,
                rowData=df.to_dict("records"),
                columnSize="sizeToFit",
                style={"height": "800px", "width": "100%"},
                defaultColDef={"filter": True,
                               "wrapText": True, 
                               "autoHeight": True,
                                 "cellStyle": {"lineHeight": "1.2", "paddingTop": "5px", "paddingBottom": "5px"}}, #set up Text Wrapping for all the columns & auto row hight
                dashGridOptions={"rowHeight": None, 
                                 "pagination": True, 
                                 "paginationPageSize": 20,
                                 "animateRows": False, 
                                 "rowSelection": {'mode': 'singleRow'}}, #here we enable row selection
            ),
         ], style={
            "height": "850px", 
            "width": "70%",
            "marginLeft": "0",    
            "marginRight": "auto" 
        }),

        # Flag Image
        html.Div([
            html.H3("Flag of selected country:", style={'textAlign': 'center'}),
            html.Div(id='flag-container', children=[

                # The image which updates by Callback                
                html.Img(
                    id='country-flag-img', 
                    src='', # Empty first
                    style={
                        'maxWidth': '100%', 
                        'height': 'auto', 
                        'display': 'block', 
                        'marginLeft': 'auto', 
                        'marginRight': 'auto',
                        'border': '1px solid #ccc',
                        'marginTop': '20px'
                        }
                    ),
                    
                    html.Div(id='flag-placeholder-text')
                ]),
        ], style={'width': '25%', 'padding': '20px'}), # Flag style

    ], style={'display': 'flex', 'flexDirection': 'row', 'alignItems': 'flex-start'}) # Flexbox container close

], style={'padding': '20px'}) # Main container close

# 3. Callback for Flag Image update
flag_column = 'flag_png'

@app.callback(
    [Output('country-flag-img', 'src'),
     Output('country-flag-img', 'style'),
     Output('flag-placeholder-text', 'children')],
    Input('countries_table', 'selectedRows') 
)
def update_flag(selected_rows):
    if not selected_rows:
        return '', {'display': 'none'}, "Select a row from table"

    selected_country_data = selected_rows[0]
    flag_url = selected_country_data.get(flag_column)
    
    img_style = {
        'maxWidth': '100%', 'height': 'auto', 
        'display': 'block', 'marginLeft': 'auto', 
        'marginRight': 'auto', 'border': '1px solid #ccc', 'marginTop': '20px'
    }
    return flag_url, img_style, ''

if __name__ == '__main__':
    app.run(debug=True)
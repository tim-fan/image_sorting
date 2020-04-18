import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc

import flask
import glob
import os

image_directory = '/home/tim/Pictures'
list_of_images = [os.path.basename(x) for x in glob.glob('{}*.jpg'.format(image_directory))]
static_image_route = '/static/'

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dbc.Row(
        dbc.Col(
            dcc.Dropdown(
                id='image-dropdown',
                options=[{'label': i, 'value': i} for i in list_of_images],
                value=list_of_images[0]
            ),
        )

    ),
    dbc.Row(
        dbc.Col([
            html.Img(id='image_a',style={'width':'50%'}),
            html.Img(id='image_b',style={'width':'50%'})
        ])
        
    ),
    dcc.Store(id='memory'),
])

@app.callback(
    [dash.dependencies.Output('image_b', 'src')],
    [dash.dependencies.Input('image-dropdown', 'value')])
def update_image_src(value):
    return [static_image_route + value]

@app.callback(
    [dash.dependencies.Output('image_a', 'src'),
     dash.dependencies.Output('memory', 'data')],
    [dash.dependencies.Input('image_a', 'n_clicks'),
     dash.dependencies.Input('image_b', 'n_clicks')],
    [dash.dependencies.State('memory', 'data')])
def image_a_click(image_a_clicks, image_b_clicks, data):
    print("click")
    default_zero = lambda x : x if x else 0
    image_a_clicks = default_zero(image_a_clicks)
    image_b_clicks = default_zero(image_b_clicks)

    if data is None:
        data = dict(
            image_a_clicks=0,
            image_b_clicks=0
        )
    
    # check which image was clicked
    a_clicked = image_a_clicks > data['image_a_clicks']
    b_clicked = image_b_clicks > data['image_b_clicks']

    print(data)
    print('a clicks: {}'.format(image_a_clicks))
    print('b clicks: {}'.format(image_b_clicks))

    print('a clicked: {}'.format(a_clicked))
    print('b clicked: {}'.format(b_clicked))

    data['image_a_clicks'] = image_a_clicks
    data['image_b_clicks'] = image_b_clicks
    
    print(data)

    i = image_a_clicks if image_a_clicks else 0
    return (static_image_route + list_of_images[i], data)

# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
@app.server.route('{}<image_path>.jpg'.format(static_image_route))
def serve_image(image_path):
    image_name = '{}.jpg'.format(image_path)
    if image_name not in list_of_images:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_name)

if __name__ == '__main__':
    app.run_server(debug=True)
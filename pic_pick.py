#!/usr/bin/env python 
'''Pic Pick
Usage: pic_pick.py IMAGE_DIR [--port=PORT] [--set-seed] [--reset-comp]

Run dash app to help pick the best photo from the given directory IMAGE_DIR.

Options:
-p PORT, --port=PORT   the port to use for the server [default: 8080]
--set-seed             fix random seed for repeatable image shuffling
--reset-comp           start the competition from scratch (don't reload from db)
'''
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Output, Input, State
from dash.exceptions import PreventUpdate
import flask
import glob
import os
import sqlitedict
import random
import pandas as pd
from docopt import docopt

from competition_management import start_competition, get_next_match, process_result

arguments = docopt(__doc__)
image_directory = arguments['IMAGE_DIR']
port = arguments['--port']
reset_comp = arguments['--reset-comp']
if arguments['--set-seed']:
    random.seed(123)

#todo: better way of serving all image types
list_of_images = [os.path.basename(x) for x in glob.glob('{}*.jpg'.format(image_directory))]
list_of_images.extend( os.path.basename(x) for x in glob.glob('{}*.png'.format(image_directory)))
assert len(list_of_images) > 0, "No images found in directory {}".format(image_directory)
static_image_route = '/static/'

db = sqlitedict.SqliteDict('./db.sqlite', autocommit=True)

TOP_N = 20 #how many of the best images to show in the top tab
n_images = len(list_of_images)
TOP_N = min(TOP_N, n_images)

def start_new_competition():
    competitors, losers = start_competition(list_of_images)
    db['competitors'] = competitors
    db['losers'] = losers

def image_name(path):
    return None if path is None else path[len(static_image_route):]

if 'competitors' not in db.keys() or reset_comp:
    print("Start new competition")
    start_new_competition()
else:
    print("continue competition from db")

if 'match_records' not in db.keys():
    db['match_records'] = pd.DataFrame(columns= ['winner', 'loser', 'timestamp'])

def top_n(n):
    """
    Get the current top n images
    """
    competitors = db['competitors']
    losers = db['losers']
    return pd.concat([
        competitors, losers]
    ).sort_values(
        by='level',
        ascending=False
    ).iloc[0:n].name.values

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

app.layout = dbc.Container([
    dcc.Tabs([
        dcc.Tab(label='Comparisons', children=[
            dbc.Row(
                dbc.Col([
                    html.P(id='competition_state', children="Competition Starting"),
                    html.P("Click the image you prefer:")
                ])
                
            ),
            dbc.Row(
                dbc.Col([
                    html.Img(id='image_a',style={'width':'50%'}),
                    html.Img(id='image_b',style={'width':'50%'})
                ]),
            ),
        ]),
        dcc.Tab(label='Best Ones', children=[
            dbc.Row(
                dbc.Col(
                    [html.P("Your favourites:")] + 
                    [html.Img(id='best_image_{i}'.format(i=i), style={'width':'100%'}) for i in range(TOP_N)]
                ),
            ),
        ]),
    ]),

    dcc.Store(id='click_state'),
])

click_callback_outputs = [
    Output('click_state', 'data'),
    Output('image_a', 'src'),
    Output('image_b', 'src')
] + [
    Output(
        'best_image_{i}'.format(i=i),
        'src'
    ) for i in range(TOP_N)
] + [
    Output('competition_state', 'children')
]
@app.callback(
    click_callback_outputs,
    [Input('image_a', 'n_clicks'),
     Input('image_b', 'n_clicks')],
    [State('click_state', 'data'),
     State('image_a', 'src'),
     State('image_b', 'src')])
def image_clicked(image_a_clicks, image_b_clicks, click_state, image_a_src, image_b_src):
    """
    Determine which image was clicked based on stored counts of clicks.
    Based on that, determine which image 'won' the competition.
    Based on that, update the competition database and choose
    the next two images to compare.
    """

    #if click state dict not initialised, set it up
    if click_state is None:
        click_state = dict(
            image_a_clicks=0,
            image_b_clicks=0
        )

    #if n clicks is None, set to zero
    default_zero = lambda x : x if x else 0
    image_a_clicks = default_zero(image_a_clicks)
    image_b_clicks = default_zero(image_b_clicks)
    
    # check which image was clicked
    a_clicked = image_a_clicks > click_state['image_a_clicks']
    b_clicked = image_b_clicks > click_state['image_b_clicks']

    #update click state record
    click_state['image_a_clicks'] = image_a_clicks
    click_state['image_b_clicks'] = image_b_clicks
    
    # determine winner and loser image
    a_name = image_name(image_a_src)
    b_name = image_name(image_b_src)
    if a_clicked:
        winner = a_name
        loser = b_name
    elif b_clicked:
        winner = b_name
        loser = a_name
    else:
        # raise PreventUpdate
        winner = None
        loser = None
    print(pd.Timestamp.now())
    print("winner: {}".format(winner))
    print("loser:  {}".format(loser))

    competitors = db['competitors']
    losers = db['losers']

    #process result and determine next images
    if (winner is not None) and (loser is not None):
        competitors, losers = process_result(winner, loser, competitors, losers)
        db['competitors'] = competitors
        db['losers'] = losers

        #update record of all results
        match_records = db['match_records']
        record = pd.DataFrame([[winner, loser, pd.Timestamp.now()]], columns=['winner', 'loser', 'timestamp'])
        match_records.append(record)
        db['match_records'] = match_records
    


    best_images = [
        static_image_route + name for name in top_n(TOP_N)
    ]

    next_image_names = get_next_match(db['competitors'])

    if next_image_names is None:
        #No more matches in competiton
        next_images = ['', '']
        competition_state = 'Competition complete'
    else:
        next_images = [
            static_image_route + name for name in next_image_names
        ]
        competition_state = 'Competition running. Remaining comparisons: {}'.format(len(competitors.index))
    
    outputs = [click_state] + next_images + best_images + [competition_state]
    return  outputs

# Add a static image route that serves images from desktop
# Be *very* careful here - you don't want to serve arbitrary files
# from your computer or server
@app.server.route('{}<image_path>.jpg'.format(static_image_route))
def serve_jpg(image_path):
    image_name = '{}.jpg'.format(image_path)
    if image_name not in list_of_images:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_name)
@app.server.route('{}<image_path>.png'.format(static_image_route))
def serve_png(image_path):
    image_name = '{}.png'.format(image_path)
    if image_name not in list_of_images:
        raise Exception('"{}" is excluded from the allowed static files'.format(image_path))
    return flask.send_from_directory(image_directory, image_name)

if __name__ == '__main__':
    app.run_server(debug=True,host="0.0.0.0", port=port)

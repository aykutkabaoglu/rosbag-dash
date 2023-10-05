# Author : Aykut Kabaoglu
# Initial Date: October, 2023
# License: MIT License

#   Permission is hereby granted, free of charge, to any person obtaining
#   a copy of this software and associated documentation files
#   (the "Software"), to deal in the Software without restriction, including
#   without limitation the rights to use, copy, modify, merge, publish,
#   distribute, sublicense, and/or sell copies of the Software, and to
#   permit persons to whom the Software is furnished to do so, subject
#   to the following conditions:

#   The above copyright notice and this permission notice shall be
#   included in all copies or substantial portions of the Software.

#   THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF
#   ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
#   TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#   PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
#   SHALL THE AUTHORS, COPYRIGHT HOLDERS OR ARIZONA BOARD OF REGENTS
#   BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#   AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#   OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
#   OR OTHER DEALINGS IN THE SOFTWARE.

__author__ = 'Aykut Kabaoglu'
__email__  = 'aykutkabaoglu@gmail.com'

import dash
from dash import dcc, html, dash_table
from dash.dependencies import Input, Output, State
import uuid
import copy
import numpy  as np
import plotly.graph_objects as go

from .bagplot import BagPlot

class BagDash(BagPlot):
    def __init__(self, bagfile):
        super().__init__(bagfile)
        self.app = dash.Dash(__name__)
        self.selected_time = None
        self.app.layout = html.Div(children=[])
        
    def run(self):
        self.app.run(debug=False)

    def add_dash_graph(self, msg_dict, **kwargs):
        fig = self.create_figure(msg_dict, **kwargs)
        self.app.layout.children.append(dcc.Graph(id=str(uuid.uuid4()), figure=fig))

    def add_dash_dataTable(self, dataframe):
        '''
        create dash datatable from pandas dataframe
        the selected row's timestamp will be shown on any other graphs to indicate same moment by drawing vertical line
        '''
        table_id = 'table' + str(uuid.uuid4())
        self.app.layout.children.append(
            dash_table.DataTable(
              id= table_id,
              columns=[{'name': str(col), 'id': str(col)} for col in dataframe.columns],
              data=dataframe.to_dict('records'),
              style_table={'height': '400px', 'overflowY': 'auto'},
              style_cell={'minWidth': 0, 'maxWidth': 100, 'whiteSpace': 'normal'},
              editable=False,
              filter_action="native",
            ),
        )
        # get all Graph objects in the layout
        output_figure_list = []
        for component in self.app.layout.children:
            if isinstance(component, dcc.Graph):
                output_figure_list.append(Output(component.id, 'figure', allow_duplicate=True))
        # Callback to update the selected data
        @self.app.callback(
            output_figure_list,
            Input(table_id, 'active_cell'),
            prevent_initial_call=True)
        def update_graphs(active_cell):
            # add a vertical line to each graph in the layout addressing the timestamp selected from datatable
            self.selected_time = dataframe.iloc[active_cell['row']].Time if active_cell else None
            output_figure_list = []
            figures_list = []
            for component in self.app.layout.children:
                if isinstance(component, dcc.Graph):
                    output_figure_list.append(Output(component.id, 'figure'))
                    graph_element = self.app.layout[component.id]
                    graph_element.figure.layout.shapes = []
                    graph_element.figure.add_vline(x = self.selected_time, line_dash="dash", line_color="red")
                    figures_list.append(graph_element.figure)
            return figures_list

    def add_diagnostics_dash(self, topic_name="/diagnostics", name_filter=[], annotate_names=False):
        fig = self.create_diagnostics_figure(topic_name=topic_name, name_filter=name_filter, annotate_names=annotate_names)    
        self.app.layout.children.append(dcc.Graph(id=topic_name, figure=fig))

    def add_rosout_dash(self, topic_name="/rosout", name_filter=[], annotate_names=False):
        fig = self.create_rosout_figure(topic_name=topic_name, name_filter=name_filter, annotate_names=annotate_names)
        self.app.layout.children.append(dcc.Graph(id=topic_name, figure=fig))
        
    def add_laserscan_dash(self, laser_topic=''):
        '''
        plots the laserscan in polar coordinates as an interactive graph and the viewing message can be updated by slider
        
        Parameters
        ----------
        laser_topic: `str` (optional)
          topic name can be given otherwise it plots the first laserScan message in the topic_table if there is
        '''
        if laser_topic and (not self.update_topic_dataframe(topic=laser_topic) or not self.is_topic_type_valid(laser_topic, 'sensor_msgs/LaserScan')):
            return
        else:
            topic_list = self.get_same_type_of_topics("sensor_msgs/LaserScan")
            if topic_list:
                laser_topic = topic_list[0]
                self.update_topic_dataframe(topic=laser_topic)
            else:
                print("There is no LaserScan message")
                return
        
        fig = go.Figure()
        fig.update_polars(radialaxis_range=[0,self.bag_df_dict[laser_topic].range_max[0]])
        fig.layout['title'] = laser_topic

        msg_size = len(self.bag_df_dict[laser_topic])
        self.app.layout.children.append(dcc.Graph(id='laserscan-plot', figure=fig))
        self.app.layout.children.append(dcc.Slider(
              id='slider',
              min=1,
              max=msg_size,
              step=1,
              value=1,
              tooltip={"placement": "bottom", "always_visible": True},
              marks={i: str(i) for i in range(0, msg_size, msg_size//10)},
              updatemode='drag')
        )
      
        @self.app.callback(
        Output('laserscan-plot', 'figure'),
        [Input('slider', 'value')],
        [State('laserscan-plot', 'relayoutData')]
        )
        def update_figure(selected_value, relayout_data):
            '''
            slider callback: updates figure whenever slider is moved and keeps the zoom value
            '''
            row = self.bag_df_dict[laser_topic].loc[selected_value]
            new_figure = copy.deepcopy(fig) # to deal with the concurrent requests
            new_figure.data = []
            angles = np.arange(row.angle_min, row.angle_max, row.angle_increment)
            new_figure.add_trace(
                go.Scatterpolargl(
                    r = row.ranges,
                    theta = angles,
                    thetaunit = 'radians',
                    mode = "markers",
                    marker = dict(size=2),
                    name = 'Timestamp:' + str(row.Time),
                    showlegend = True
                ))
            if relayout_data and 'polar.radialaxis.range' in relayout_data:
                new_figure['layout.polar.radialaxis.range'] = relayout_data['polar.radialaxis.range']
            return new_figure
          
        update_figure(0, fig['layout'])

    def add_pointcloud_dash(self, pointcloud_topic=''):
        '''
        plots the pointcloud in cartesian coordinates as an interactive graph and the viewing message can be updated by slider
        
        Parameters
        ----------
        pointcloud_topic: `str` (optional)
          topic name can be given otherwise it plots the first pointcloud message in the topic_table if there is
        '''      
        if pointcloud_topic and (not self.update_topic_dataframe(topic=pointcloud_topic) or not self.is_topic_type_valid(pointcloud_topic, 'sensor_msgs/PointCloud')):
            return
        else:
            topic_list = self.get_same_type_of_topics("sensor_msgs/PointCloud")
            if topic_list:
                pointcloud_topic = topic_list[0]
                self.update_topic_dataframe(topic=pointcloud_topic)
            else:
                print("There is no PointCloud message")
                return
        
        # declare axis range before plotting the data. causes additional iteration but provides static and easy visualization
        min_x, min_y, min_z, max_x, max_y, max_z = 10000, 10000, 10000, 0, 0, 0
        for points in self.bag_df_dict[pointcloud_topic].points:
            x_values = [point.x for point in points]
            y_values = [point.y for point in points]
            z_values = [point.z for point in points]
            min_x, max_x = min(min(x_values), min_x), max(max(x_values), max_x)
            min_y, max_y = min(min(y_values), min_y), max(max(y_values), max_y)
            min_z, max_z = min(min(z_values), min_z), max(max(z_values), max_z)
            
        fig = go.Figure()
        fig.layout['title'] = pointcloud_topic
        
        msg_size = len(self.bag_df_dict[pointcloud_topic])
        self.app.layout.children.append(dcc.Graph(id='pointcloud-plot', figure=fig))
        self.app.layout.children.append(dcc.Slider(
              id='slider',
              min=1,
              max=msg_size,
              step=1,
              value=1,
              tooltip={"placement": "bottom", "always_visible": True},
              marks={i: str(i) for i in range(0, msg_size, msg_size//10)},
              updatemode='drag')
        )
      
        @self.app.callback(
        Output('pointcloud-plot', 'figure'),
        Input('slider', 'value'),
        State('pointcloud-plot', 'relayoutData')
        )
        def update_figure(selected_value, relayout_data):
            '''
            slider callback: updates figure whenever slider is moved and keeps the zoom value
            '''
            row = self.bag_df_dict[pointcloud_topic].loc[selected_value]
            new_figure = copy.deepcopy(fig)
            new_figure.data = []
            new_figure.add_trace(
                go.Scatter3d(
                    x = [point.x for point in row.points],
                    y = [point.y for point in row.points],
                    z = [point.z for point in row.points],
                    mode = "markers",
                    marker = dict(size=2),
                    name = 'Timestamp:' + str(row.Time),
                    showlegend = True
                ))

            if relayout_data:
                new_figure['layout'] = relayout_data
                
            new_figure.update_layout(scene=dict(
                aspectmode='manual',
                aspectratio={'x':abs(max_x-min_x), 'y':abs(max_y-min_y), 'z':abs(max_z-min_z)},
                xaxis = dict(range=[min_x, max_x], ticks='outside', tickwidth=5, tickcolor='red'),
                yaxis = dict(range=[min_y, max_y], ticks='outside', tickwidth=5, tickcolor='green'),
                zaxis = dict(range=[min_z, max_z], ticks='outside', tickwidth=5, tickcolor='blue'),
            ))
                
            return new_figure
          
        update_figure(0, fig['layout'])
        
    def add_pointcloud2_dash(self, pointcloud2_topic=''):
        raise NotImplementedError        
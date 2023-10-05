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

import plotly.graph_objects as go
import numpy  as np
import pandas as pd

from .bagreader import BagReader

class BagPlot(BagReader):
  
    def plot(self, msg_dict, **kwargs):
        self.create_figure(msg_dict, **kwargs).show()
    
    def create_figure(self, msg_dict, **kwargs):
        '''Creates and returns a figure that plots the timseries given topic and its indexes
        '''
        fig = go.Figure()
        marker_symbols = np.array(['circle', 'square', 'diamond', 'cross'])
        legend = []
        for topic_name in msg_dict:
            if not self.update_topic_dataframe(topic_name):
                return
            for msg_index in msg_dict[topic_name]:
                legend.append(msg_index)
                marker_symbols = np.roll(marker_symbols,1)
                fig.add_trace(go.Scatter(x = self.bag_df_dict[topic_name]['Time'], y = self.bag_df_dict[topic_name][msg_index].astype(float), 
                                         mode = "lines+markers", name = str(topic_name+"/"+msg_index), line=dict(width=1), marker = dict(symbol=marker_symbols[0])))
        
        # Customize the layout
        title = ' '.join([str(elem) for elem in list(msg_dict.keys())])
        fig.update_layout(
            title=title,
            xaxis_title='Time',
            yaxis_title='Message',
        )
        fig.update_traces(**kwargs)

        return fig
        
    def plot_diagnostics(self, topic_name="/diagnostics", name_filter=[], annotate_names=False):
        self.create_diagnostics_figure(topic_name=topic_name, name_filter=name_filter, annotate_names=annotate_names).show()
      
    def create_diagnostics_figure(self, topic_name="/diagnostics", name_filter=[], annotate_names=False):
        '''
        plots diagnostics messages according the their levels like OK, WARN, ERROR, STALE. it hovers the details of each message over the graph
        
        Parameters
        ----------
        topic_name: `str`
        name_filter: `list` (optional)
          list of strings that can be used to plot only the desired named messages. it acts as searching and don't have to be exact name
          if it is empty, plots all messages
        annotate_names: `bool`
          names can be viewed over the marker in addition to hover text. this is a time consuming process
        '''
        if topic_name and (not self.update_topic_dataframe(topic=topic_name) or not self.is_topic_type_valid(topic_name, 'diagnostic_msgs/DiagnosticArray')):
            return
        
        def keys_to_text(values):
            text_list = []
            for keys in values:
                text_list.append([f'{value}<br>' for value in keys])
            return text_list
        
        fig = go.Figure()
        fig.layout['title'] = topic_name
        
        # OK=0
        # WARN=1
        # ERROR=2
        # STALE=3
        levels = ['OK', 'WARN', 'ERROR', 'STALE']
        df_list = [pd.DataFrame(columns=['Time','name','message','hardware_id','values'])] * 4
        marker_symbols = np.array(['circle', 'square', 'diamond', 'cross'])
        
        for _, row in self.bag_df_dict[topic_name].iterrows():
            for state in row.status:
                if not name_filter or [name for name in name_filter if name in state.name]:
                    df_list[state.level] = df_list[state.level].append({'Time': row.Time, 'name': state.name, 'message': state.message, 'hardware_id': state.hardware_id, 'values': state.values}, ignore_index=True)

        for i in range(len(df_list)):
            hover_text = [
                f'{name}<br> {message}<br> {values}'
                for name, message, values in zip(df_list[i]['name'], df_list[i]['message'], keys_to_text(df_list[i]['values']))
            ]
            fig.add_trace(go.Scatter(x = df_list[i]['Time'], y = [-1*i] * len(df_list[i]), 
                                  mode = "lines+markers", name = levels[i], line = dict(width=1), marker = dict(symbol=marker_symbols[i]),
                                  hovertext = hover_text))

            # annotate name of the each message (it is resource consuming but go.Scatter do not provide better option)
            if annotate_names:
                for x_val, text in zip(df_list[i]['Time'], df_list[i]['name']):
                    fig.add_annotation(
                      go.layout.Annotation(
                          x=x_val,
                          y=-1*i,
                          text=text,
                          showarrow=False,
                          font=dict(size=10),
                          xref='x',
                          yref='y',
                          textangle=90,  # Rotate the text by 90 degrees
                      )
                    )

        # Customize the layout (optional)
        fig.update_layout(
            title='diagnostics',
            xaxis_title='Time',
            yaxis_title='Message',
        )
        
        return fig
        
    def plot_rosout(self, topic_name="/rosout", name_filter=[], annotate_names=False):
        self.create_rosout_figure(topic_name=topic_name, name_filter=name_filter, annotate_names=annotate_names).show()
        
    def create_rosout_figure(self, topic_name="/rosout", name_filter=[], annotate_names=False):
        '''
        plots rosout messages according the their levels like DEBUG, INFO, WARN, ERROR, FATAL. it hovers the details of each message over the graph
        
        Parameters
        ----------
        topic_name: `str`
        name_filter: `list` (optional)
          list of strings that can be used to plot only the desired named messages. it acts as searching and don't have to be exact name
          if it is empty, plots all messages
        annotate_names: `bool`
          names can be viewed over the marker in addition to hover text. this is a time consuming process
        '''
        import math
        
        if topic_name and (not self.update_topic_dataframe(topic=topic_name) or not self.is_topic_type_valid(topic_name, 'rosgraph_msgs/Log')):
            return

        fig = go.Figure()
        fig.layout['title'] = topic_name
        
        # DEBUG=1 #debug level
        # INFO=2  #general level
        # WARN=4  #warning level
        # ERROR=8 #error level
        # FATAL=16 #fatal/critical level
        levels = ['DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL']
        df_list = [pd.DataFrame(columns=['Time','name','message'])] * 5
        marker_symbols = np.array(['circle', 'square', 'diamond', 'cross','x'])
        
        for _, row in self.bag_df_dict[topic_name].iterrows():
            if not name_filter or [name for name in name_filter if name in row['name']]:
                df_list[int(math.log2(row.level))] = df_list[int(math.log2(row.level))].append({'Time': row.Time, 'name': row['name'], 'message': row.msg}, ignore_index=True)

        for i in range(len(df_list)):
            hover_text = [
                f'{name}<br> {message}'
                for name, message in zip(df_list[i]['name'], df_list[i]['message'])
            ]
            fig.add_trace(go.Scatter(x = df_list[i]['Time'], y = [-1*i] * len(df_list[i]), 
                                  mode = "lines+markers", name = levels[i], line = dict(width=1), marker = dict(symbol=marker_symbols[i]),
                                  hovertext = hover_text))

            # annotate name of the each message (it is resource consuming but go.Scatter do not provide better option)
            if annotate_names:
                for x_val, text in zip(df_list[i]['Time'], df_list[i]['name']):
                    fig.add_annotation(
                      go.layout.Annotation(
                          x=x_val,
                          y=-1*i,
                          text=text,
                          showarrow=False,
                          font=dict(size=10),
                          xref='x',
                          yref='y',
                          textangle=90,  # Rotate the text by 90 degrees
                      )
                    )

        # Customize the layout (optional)
        fig.update_layout(
            title='rosout',
            xaxis_title='Time',
            yaxis_title='Message',
        )

        return fig
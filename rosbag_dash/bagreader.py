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

import rosbag
import numpy  as np
import pandas as pd
from scipy.spatial.transform import Rotation
from .helper import divide_message

class BagReader:
    '''
    `bagreader` class provides API to read rosbag files in an effective easy manner with significant hassle.

    Parameters
    ----------
    bagfile: `string`
        Bagreader constructor takes name of a bag file as an  argument. name of the bag file can be provided as the full qualified path, relative path or just the file name.

    Attributes
    ----------   
    reader: `rosbag.Bag`
        rosbag.Bag object that 

    topic_table: `pandas.DataFrame`
        A pandas DataFrame showing list of topics, their types, frequencies and message counts

    bag_df_dict: `dictionary`
        dictionary to keep dataframes of each topic by name. it only stores the requested topics

    Example
    -------
    >>> b = bagreader('2020-03-01-23-52-11.bag') 

    '''

    def __init__(self , bagfile):

        self.reader = rosbag.Bag(bagfile)
        info = self.reader.get_type_and_topic_info() 

        self.topic_table = pd.DataFrame(list(zip(info.topics.keys(), 
                                                 [msg.msg_type for msg in info.topics.values()], 
                                                 [msg.message_count for msg in info.topics.values()], 
                                                 [msg.frequency for msg in info.topics.values()])), 
                                        columns=['Topics', 'Types', 'Message Count', 'Frequency'])

        # store all read topics' dataframe in a dictionary
        self.bag_df_dict = {}

    def is_topic_found(self, topic_name: str) -> bool:
        '''Returns whether the topic is found in bag file'''
        return bool(self.topic_table[self.topic_table['Topics'] == topic_name].index.array)

    def is_topic_type_valid(self, topic_name: str, topic_type: str) -> bool :
        '''Checks topic type is as desired'''
        return bool((self.topic_table[self.topic_table['Topics'] == topic_name].Types.array == topic_type)[0])

    def update_topic_dataframe(self, topic: str) -> bool:
        '''
        Class method `update_topic_dataframe` to extract message from the ROS Bag by topic name `topic` and
        stores it in the class's dataframe. It is intended to update the class attribute and is used a helper method like a private function
        '''
        # do not read same topics multiple time
        if topic in self.bag_df_dict.keys():
            return True
        if not self.is_topic_found(topic):
            print(topic, "is an invalid name, check topic_table")
            return False
          
        # get messages and update topic dataframe dictionary
        try:
            data = []
            time = []
            cols = []
            for topic, msg, t in self.reader.read_messages(topics=topic, start_time=None, end_time=None): 
                # get precise time from header.stamp
                time.append(t.secs + t.nsecs*1e-9)
                vals, cols = divide_message(msg)
                data.append(vals)

            df = pd.DataFrame(data, columns=cols)
            # add roll, pitch, yaw columns to dataframe when quaternion message found
            df = self.quaternion_to_euler(df)
            # convert seconds to human readable date and time
            df['Time'] = pd.to_datetime(time, unit='s')
            # store newly generated dataframe
            self.bag_df_dict[topic] = df
            return True
        except:
            print("Couldn't get the message from bag file:", topic)
            return False

    def get_message_by_topic(self, topics: list) -> dict:
        '''
        Gets single topic name as a string or list of topic names and returns single dataframe or dataframe dictionary that it's keys are topic names
        :param topics: list or single str of topic names
        '''
        if type(topics) is list:
            for topic in topics:
               if not self.update_topic_dataframe(topic):
                  return
            return {k: self.bag_df_dict[k] for k in topics}
        elif self.update_topic_dataframe(topics):
            return self.bag_df_dict[topics]

    def get_same_type_of_topics(self, type_to_look: str="") -> list:
        '''Collects the same type of topics and returns the list of topic names'''
        table_rows = self.topic_table[self.topic_table['Types']==type_to_look]
        topics_to_read = table_rows['Topics'].values
        
        return topics_to_read

    def quaternion_to_euler(self, df: pd.DataFrame) -> pd.DataFrame:
        '''Convert quaternions to euler if there is a quaternion type message
        
        checks '.w' or 'w' pattern in the end of columns and adds 'Roll', 'Pitch', 'Yaw' columns to given dataframe
        '''
        quaternion_indices = ''
        for column in df.columns:
            if len(column) == 1 and column == 'w':
                quaternion_indices = column
                break
            elif '.w' == column[-2::]:
                quaternion_indices = column
                break
        if not quaternion_indices:
            return df

        orient_vec = [str(quaternion_indices[:-1] + 'x'), str(quaternion_indices[:-1] + 'y'), 
                      str(quaternion_indices[:-1] + 'z'), str(quaternion_indices[:-1] + 'w')]
        try:
            df['Roll'],df['Pitch'],df['Yaw'] = np.transpose(Rotation.from_quat(df[orient_vec]).as_euler("xyz",degrees=True))
        except:
            print("Quaternion transform error")
        return(df)



        

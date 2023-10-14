# rosbag_dash
rosbag_dash package provides three modules as bagreader, bagplot and bagdash. 

* **BagReader** class is responsible for the reading of a bag file and creates pandas dataframe dictionary for each addressed topic.

* **BagPlot** class provides methods to plot figures with bunch of topics together. Except the array like topics, you can draw any topics by passing target indexes. You can also plot /rosout and /diagnostics topics according to their levels.

* **BagDash** class allows users to create dash applications. It can use the capabilities of BagPlot by adding the feature of drawing sensor_msgs/LaserScan and sensor_msgs/PointCloud topics. These graphs are dynamic and you can view the instantaneous data by dragging the slider. Additionally, you can create dataTables to view all messages of any topic in a table, it is especially useful for text based topics. The rows of these tables are selectable and all the figures are annotated according to selected timestamp (it is slow).

## Installation
```
pip install rosbag-dash
```
or
```
git clone https://github.com/aykutkabaoglu/rosbag-dash.git
python3 -m pip install rosbag-dash
```

## Usage

##### BagReader
```
from rosbag_dash import BagReader

bag_reader = BagReader('/path/to/bag_file.bag')
bag_reader.topic_table
bag_reader.get_message_by_topic('/topic_name_1)
bag_reader.bag_df_dict['/topic_name_1']
bag_reader.is_topic_type_valid('/gps_fix','sensor_msgs/NavSatFix')
bag_reader.is_topic_found('/gps_fix')
bag_reader.get_same_type_of_topics("nav_msgs/Odometry")
```

##### BagPlot
```
from rosbag_dash import BagPlot
bag_plot = BagPlot('/path/to/bag_file.bag')

plot_dict = {
             "/catvehicle/cmd_vel": ["linear.x", "linear.y"],
             "/catvehicle/vel": ["linear.x", "linear.y"],
             "/catvehicle/distanceEstimator/angle": ["data"],
             }
bag_plot.plot(plot_dict)

plot_dict = {"/gps_odom": ["Roll", "Pitch", 'Yaw']}
bag_plot.plot(plot_dict)

bag_plot.plot_rosout()
bag_plot.plot_diagnostics()

```

##### BagDash
```
from rosbag_dash import BagDash
bag_dash = BagDash('/path/to/bag_file.bag')

plot_dict = {
             "/catvehicle/cmd_vel": ["linear.x", "linear.y"],
             "/catvehicle/vel": ["linear.x", "linear.y"],
             "/catvehicle/distanceEstimator/angle": ["data"],
             }
bag_dash.add_dash_graph(plot_dict)

plot2_dict = {
             "/catvehicle/brake": ["force.x", "force.y"],
             "/catvehicle/accelerator":["force.z"]
             }
bag_dash.add_dash_graph(plot2_dict)

bag_dash.add_rosout_dash()
bag_dash.add_diagnostics_dash()
bag_dash.add_laserscan_dash()

bag_dash.run()

```

**Check notebooks and scripts for different kind of usages.

**Some Samples (not same as the examples above)**
![Multiple Topic](https://github.com/aykutkabaoglu/rosbag-dash/assets/12614433/cfe9ea4e-ce45-491c-b0be-a1ac6829a365)
![Same Topic Different Index](https://github.com/aykutkabaoglu/rosbag-dash/assets/12614433/fca433a1-f51a-4f8c-9e34-7323d0a70e64)
![Annotated Timestamp](https://github.com/aykutkabaoglu/rosbag-dash/assets/12614433/b8df0520-7fd0-4143-a089-5a98a8bbfd29)
![Annotated Diagnostics Message](https://github.com/aykutkabaoglu/rosbag-dash/assets/12614433/35bc7c48-ae3d-4073-b6ac-f8522d5714db)
![PointCloud Slider](https://github.com/aykutkabaoglu/rosbag-dash/assets/12614433/9a285381-ef60-4770-992c-3dc71784e70c)
![LaserScan Slider](https://github.com/aykutkabaoglu/rosbag-dash/assets/12614433/988ff812-790e-4633-8e44-2c5903aa5fa1)



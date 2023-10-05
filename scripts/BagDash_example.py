from rosbag_dash import BagDash
import os
 
 
dir = os.path.dirname(os.getcwd())
path = os.path.join(dir, 'notebook/2016-06-01-14-57-13.bag')
b = BagDash(path)

plot_dict = {
             "/catvehicle/cmd_vel": ["linear.x", "linear.y"],
             "/catvehicle/vel": ["linear.x", "linear.y"],
             "/catvehicle/distanceEstimator/angle": ["data"],
             }
b.add_dash_graph(plot_dict)

plot2_dict = {
             "/catvehicle/brake": ["force.x", "force.y"],
             "/catvehicle/accelerator":["force.z"]
             }
b.add_dash_graph(plot2_dict)

b.add_rosout_dash()
b.add_diagnostics_dash()
b.add_laserscan_dash()

b.run()

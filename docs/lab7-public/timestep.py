import time

import mujoco
from mujoco import viewer

TIMESTEP = 1e-4

XML = rf"""
<mujoco>
  <option timestep="{TIMESTEP}" integrator="Euler"/>

  <asset>
    <texture name="grid" type="2d" builtin="checker" rgb1=".1 .2 .3" rgb2=".2 .3 .4" width="300" height="300"/>
    <material name="grid" texture="grid" texrepeat="8 8" reflectance=".2"/>
    <texture name="ball" type="cube" builtin="checker" rgb1=".3 .3 .3" rgb2="1 1 1" width="300" height="300"/>
    <material name="ball" texture="ball" texrepeat="8 8"/>
  </asset>

  <worldbody>
    <geom name="floor" size=".2 .2 .01" type="plane" material="grid"/>
    <geom name="wall" size=".2 .2 .01" type="plane" material="grid" pos=".2 0 .2" zaxis="-1 0 0"/>
    <light pos="0 0 .6"/>
    <light pos="-.6 0 .6" dir="1 0 -1"/>
    <body name="ball" pos="-.1 0 .2">
      <freejoint/>
      <geom name="ball" type="sphere" size=".02" material="ball" mass=".001"/>
    </body>
  </worldbody>

  <default>
    <pair solref="-100000 0" />
  </default>

  <contact>
    <pair geom1="floor" geom2="ball"/>
    <pair geom1="wall" geom2="ball"/>
  </contact>

</mujoco>
"""

model = mujoco.MjModel.from_xml_string(XML)
data = mujoco.MjData(model)

viewer = viewer.launch_passive(model, data)

start_time = time.time()

timestep = TIMESTEP

while True:
    step_start = time.time()
    mujoco.mj_step(model, data)
    viewer.sync()
    time_until_next_step = model.opt.timestep - (time.time() - step_start)
    if time_until_next_step > 0:
        time.sleep(time_until_next_step)

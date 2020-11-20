#!/usr/bin/env python
# coding: utf-8

# In[5]:


import pumpy
import ERV_driver as erv
import time


# In[6]:


p33 = pumpy.Pump33('/dev/ttyUSB0',verbose = False)
v = erv.ERV()
p33.set_mode(p33.modes[1])
p33.set_diameter(1,4.5)


# In[18]:

p33.set_flow_rate(1,600)
p33.set_direction(1,'Refill')
v.movePosition(1)
p33.start()
time.sleep(5)
p33.stop()
p33.set_flow_rate(1,300)
p33.set_direction(1,'Infuse')
v.movePosition(2)
p33.start()
time.sleep(2)
p33.stop()
v.movePosition(1)


# In[ ]:





# In[ ]:





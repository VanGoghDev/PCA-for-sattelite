# PCA-for-sattelite
My course project at institute. I should to create a PCA algorhitm in order to estimate an orbit of satellite

based on apriory analysis

# Model

A sattelite which moves around the Earth orbit under _normal Gravity Field_ 

__Initial data__

Initial data are specified in the osculating elements

1. Orbital Inclination is 42° 

2. Semimajor axis we can count from specified axes of ellips 

```python
re = 6371  # Earth radius, km
h_pi = 21000
h_alpha = 970
r_pi = h_pi + re
self.a = (r_pi + r_alpha) / 2  # Semimajor axis, km
```
3. True Anomaly is 160°



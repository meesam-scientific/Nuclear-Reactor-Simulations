"""
===============================================================================
Project : Pin-cell geometry plot (companion script for the OpenMC simulation)
Author  : Meesam Raza
Purpose : Creates pin_cell_plot.png, a cross-section view of the UO2 pin cell
          (fuel = red, cladding = grey, moderator = blue).

Usage
    1. Run openmc_uo2_pin_cell_simulation.py first. It writes materials.xml
       and geometry.xml in the working directory.
    2. Run this script in the same directory:
           python plot_geometry.py
===============================================================================
"""

import openmc
import matplotlib.pyplot as plt

# Read the materials written by the main simulation script
materials = openmc.Materials.from_xml('materials.xml')
material_by_name = {m.name: m for m in materials}

# Plot settings
plot = openmc.Plot()
plot.filename = 'pin_cell_plot'
plot.width = (1.5, 1.5)    # plot size in cm
plot.pixels = (400, 400)   # resolution
plot.color_by = 'material'

# Colors: fuel = red, cladding = grey, water = blue
plot.colors = {
    material_by_name['UO2 fuel']: 'red',
    material_by_name['Zircaloy']: 'gray',
    material_by_name['Water']: 'blue',
}

# Export the plot settings and let OpenMC generate the image
plots = openmc.Plots([plot])
plots.export_to_xml()
openmc.plot_geometry()

# Show the picture on screen (e.g. in Google Colab)
plt.figure(figsize=(6, 6))
img = plt.imread('pin_cell_plot.png')
plt.imshow(img)
plt.axis('off')
plt.title('UO2 Pin-Cell Geometry')
plt.show()

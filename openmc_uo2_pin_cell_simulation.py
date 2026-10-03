"""
===============================================================================
Project: Automated UO2 Pin-Cell Simulation using OpenMC
Author: Meesam Raza
Date: October 2026
Description: This script sets up a basic neutron transport eigenvalue 
             simulation for a UO2 fuel pin with Zircaloy cladding.
             It automatically downloads the required nuclear data, 
             generates the XML files, and runs the simulation.
===============================================================================
"""

import openmc
import openmc_data_downloader as odd
import os

# Clear any existing cross-section environment variables to avoid path conflicts
if 'OPENMC_CROSS_SECTIONS' in os.environ:
    del os.environ['OPENMC_CROSS_SECTIONS']
openmc.config.pop('cross_sections', None)

# =============================================================================
# 1. MATERIALS DEFINITION
# =============================================================================

# Define UO2 Fuel (Using explicit nuclides to avoid missing U234 trace errors)
uo2 = openmc.Material(name='UO2 fuel')
uo2.add_nuclide('U235', 0.03)  # 3% U-235
uo2.add_nuclide('U238', 0.97)  # 97% U-238
uo2.add_element('O', 2.0)
uo2.set_density('g/cm3', 10.5)

# Define Zircaloy Cladding
zirconium = openmc.Material(name='Zircaloy')
zirconium.add_element('Zr', 1.0)
zirconium.set_density('g/cm3', 6.6)

# Define Light Water Coolant / Moderator
water = openmc.Material(name='Water')
water.add_element('H', 2.0)
water.add_element('O', 1.0)
water.set_density('g/cm3', 0.74)
water.add_s_alpha_beta('c_H_in_H2O') # Thermal scattering for water

materials = openmc.Materials([uo2, zirconium, water])

# =============================================================================
# 2. AUTOMATIC DATA DOWNLOADING
# =============================================================================
print("Downloading required nuclear cross-sections...")
odd.download_cross_section_data(
    materials, 
    set_OPENMC_CROSS_SECTIONS=True
)
materials.export_to_xml()

# =============================================================================
# 3. GEOMETRY DEFINITION
# =============================================================================

# Define cylindrical surfaces for fuel and cladding
fuel_outer_radius = openmc.ZCylinder(r=0.39)
clad_outer_radius = openmc.ZCylinder(r=0.46)

# Define square lattice boundaries (Reflective for infinite lattice approximation)
pitch = 1.26
left = openmc.XPlane(x0=-pitch/2, boundary_type='reflective')
right = openmc.XPlane(x0=pitch/2, boundary_type='reflective')
bottom = openmc.YPlane(y0=-pitch/2, boundary_type='reflective')
top = openmc.YPlane(y0=pitch/2, boundary_type='reflective')

# Define regions
fuel_region = -fuel_outer_radius
clad_region = +fuel_outer_radius & -clad_outer_radius
water_region = +clad_outer_radius & +left & -right & +bottom & -top

# Create cells
fuel_cell = openmc.Cell(name='fuel', fill=uo2, region=fuel_region)
clad_cell = openmc.Cell(name='clad', fill=zirconium, region=clad_region)
mod_cell = openmc.Cell(name='moderator', fill=water, region=water_region)

# Export geometry to XML
root_universe = openmc.Universe(cells=(fuel_cell, clad_cell, mod_cell))
geometry = openmc.Geometry(root_universe)
geometry.export_to_xml()

# =============================================================================
# 4. SIMULATION SETTINGS & EXECUTION
# =============================================================================

settings = openmc.Settings()
settings.batches = 100
settings.inactive = 10
settings.particles = 1000
settings.export_to_xml()

print("Setup complete. Starting OpenMC simulation...")
openmc.run()

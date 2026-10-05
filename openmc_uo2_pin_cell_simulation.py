"""
===============================================================================
Project : Automated UO2 Pin-Cell Simulation using OpenMC
Author  : Meesam Raza
Date    : October 2026
Purpose : Monte Carlo neutron-transport eigenvalue (k-effective) calculation
          for an infinite square lattice of UO2 fuel pins with Zircaloy-type
          cladding and light-water moderator.

What this script does
    1. Defines the materials (UO2 fuel, cladding, light water)
    2. Downloads only the required nuclear cross-section data automatically
    3. Builds the pin-cell geometry (reflective boundaries = infinite lattice)
    4. Runs the OpenMC eigenvalue calculation
    5. Reads the final statepoint file, prints k-effective and saves it to
       results.txt

All model inputs are collected in the PARAMETERS block below, so a study
(e.g. a different enrichment or water density) only needs one value changed.
===============================================================================
"""

import os

import openmc
import openmc_data_downloader as odd

# =============================================================================
# PARAMETERS  (change values here only)
# =============================================================================

# Fuel
ENRICHMENT_ATOM_PERCENT = 3.0   # U-235 in total uranium, in atom % (~2.96 wt%)
FUEL_DENSITY = 10.5             # g/cm3

# Cladding (modelled as pure Zr, a simplification of Zircaloy)
CLAD_DENSITY = 6.6              # g/cm3

# Moderator / coolant (light water)
WATER_DENSITY = 0.74            # g/cm3 (hot operating condition)

# Geometry (all in cm)
FUEL_RADIUS = 0.39
CLAD_RADIUS = 0.46
PITCH = 1.26                    # pin-to-pin distance of the square lattice

# Monte Carlo settings
BATCHES = 150                   # total batches
INACTIVE = 30                   # batches discarded for source convergence
PARTICLES = 10000               # neutron histories per batch
SEED = 1                        # fixed seed -> reproducible results

# =============================================================================
# SETUP
# =============================================================================

# Clear any existing cross-section environment variables to avoid path conflicts
if 'OPENMC_CROSS_SECTIONS' in os.environ:
    del os.environ['OPENMC_CROSS_SECTIONS']
openmc.config.pop('cross_sections', None)

# =============================================================================
# 1. MATERIALS DEFINITION
# =============================================================================

# UO2 fuel (explicit nuclides are used to avoid missing U234 trace errors)
u235_fraction = ENRICHMENT_ATOM_PERCENT / 100.0
uo2 = openmc.Material(name='UO2 fuel')
uo2.add_nuclide('U235', u235_fraction)
uo2.add_nuclide('U238', 1.0 - u235_fraction)
uo2.add_element('O', 2.0)
uo2.set_density('g/cm3', FUEL_DENSITY)

# Cladding
zirconium = openmc.Material(name='Zircaloy')
zirconium.add_element('Zr', 1.0)
zirconium.set_density('g/cm3', CLAD_DENSITY)

# Light-water coolant / moderator
water = openmc.Material(name='Water')
water.add_element('H', 2.0)
water.add_element('O', 1.0)
water.set_density('g/cm3', WATER_DENSITY)
water.add_s_alpha_beta('c_H_in_H2O')  # thermal scattering of H in water

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

# Cylindrical surfaces for fuel and cladding
fuel_outer_radius = openmc.ZCylinder(r=FUEL_RADIUS)
clad_outer_radius = openmc.ZCylinder(r=CLAD_RADIUS)

# Square lattice boundaries (reflective -> infinite lattice approximation)
left = openmc.XPlane(x0=-PITCH / 2, boundary_type='reflective')
right = openmc.XPlane(x0=PITCH / 2, boundary_type='reflective')
bottom = openmc.YPlane(y0=-PITCH / 2, boundary_type='reflective')
top = openmc.YPlane(y0=PITCH / 2, boundary_type='reflective')

# Regions
fuel_region = -fuel_outer_radius
clad_region = +fuel_outer_radius & -clad_outer_radius
water_region = +clad_outer_radius & +left & -right & +bottom & -top

# Cells
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
settings.batches = BATCHES
settings.inactive = INACTIVE
settings.particles = PARTICLES
settings.seed = SEED
settings.export_to_xml()

print("Setup complete. Starting OpenMC simulation...")
openmc.run()

# =============================================================================
# 5. RESULTS
# =============================================================================

statepoint_file = f"statepoint.{BATCHES}.h5"

if os.path.exists(statepoint_file):
    with openmc.StatePoint(statepoint_file) as sp:
        keff = sp.keff  # combined k-effective with its standard deviation

    active_histories = (BATCHES - INACTIVE) * PARTICLES
    summary = (
        f"Combined k-effective = {keff.n:.5f} +/- {keff.s:.5f}\n"
        f"Batches = {BATCHES} ({INACTIVE} inactive), "
        f"particles/batch = {PARTICLES}, "
        f"active histories = {active_histories}\n"
    )
    print("\n" + summary)

    with open("results.txt", "w") as f:
        f.write(summary)
else:
    print(f"Statepoint file {statepoint_file} not found - check the OpenMC output above.")

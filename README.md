# Nuclear Reactor Simulations using OpenMC

Welcome to my computational physics portfolio! 

### About Me
I am **Meesam Raza**, a Mathematics graduate from Virtual University of Pakistan, currently transitioning into the field of Nuclear Reactor Physics and Computational Simulations. This repository showcases my ability to model nuclear systems using Python-based APIs and computational tools.

---

## Project 1: UO2 Fuel Pin-Cell Simulation
**File:** `openmc_uo2_pin_cell_simulation.py`

This script sets up a basic neutron transport eigenvalue (k-effective) simulation for a standard Uranium Dioxide (UO2) fuel pin. 

### Key Technical Features:
* **Materials Defined:** 3% enriched UO2 fuel, Zircaloy cladding, and Light Water (H2O) moderator/coolant.
* **Geometry Setup:** Cylindrical fuel pin surrounded by cladding, with reflective square lattice boundaries to approximate an infinite lattice structure.
* **Simulation Settings:** Configured for 100 batches (10 inactive) using 1000 particles per batch.
* **Automation:** This script is fully automated. It uses openmc_data_downloader to automatically fetch only the required nuclear cross-sections on the fly, making it completely plug-and-play for Google Colab or any local environment.

**Output:** 
Executing this Python script automatically generates the necessary `materials.xml`, `geometry.xml`, and `settings.xml` files required by the OpenMC engine to run the Monte Carlo simulation.

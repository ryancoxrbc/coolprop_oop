"""
CoolProp-OOP: An object-oriented wrapper for CoolProp thermodynamic properties.

This package provides an intuitive, object-oriented interface to CoolProp's thermodynamic
property calculations for both humid air and pure fluids. It simplifies property access
and calculations through two main classes: StateHA for humid air properties and StateProps
for pure fluid properties.

Features:
    - Object-oriented interface with property-based getters and setters
    - Automatic property validation to prevent physically impossible states
    - State constraint management to prevent overconstraining the system
    - All thermodynamic properties are directly settable (enthalpy, entropy, viscosity, etc.)
    - Automatic property calculation and caching for better performance
    - Support for both humid air and pure fluid calculations
    - Consistent unit system (SI units)
    - Simple property constraint management

Example Usage:
    >>> from coolprop_oop import StateHA, StateProps
    
    # Humid Air Example (20°C, 1 atm, 50% RH)
    >>> state = StateHA('P', 101325, 'T', 293.15, 'R', 0.5)
    >>> print(f"{state.get('T')-273.15:.1f}°C, {state.get('R')*100:.0f}% RH")
    20.0°C, 50% RH
    >>> humidity = state.get('W')  # Get humidity ratio
    
    # Pure Fluid Example (Water at 100°C, 1 atm)
    >>> water = StateProps('P', 101325, 'T', 373.15, 'water')
    >>> print(f"Density: {water.get('D'):.2f} kg/m³")
    Density: 0.58 kg/m³
    
    # Changing constraints
    >>> water.reset('T', 393.15)  # Change temperature to 120°C
    >>> water.replace('P', 'D', 1.0)  # Replace pressure with density constraint

For more examples, see the examples directory in the package repository.
"""

from .coolprop_oop import StateHA, StateProps

__version__ = "2.0.0"
__all__ = ['StateHA', 'StateProps'] 
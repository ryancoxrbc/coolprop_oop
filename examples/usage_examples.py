#!/usr/bin/env python3
"""
CoolProp-OOP Usage Examples
"""

from coolprop_oop import StateHA, StateProps


def example_humid_air_basic():
    """
    Basic example of using StateHA for humid air properties
    """
    print("\n=== Basic Humid Air Properties ===")

    # Create a state for humid air at 20°C, 1 atm, 50% RH
    state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)

    # Access and print properties using get() method
    print(f"Temperature: {state.get('T')-273.15:.2f}°C")
    print(f"Pressure: {state.get('P'):.0f} Pa")
    print(f"Relative Humidity: {state.get('R') * 100:.1f}%")

    # Get multiple properties in one call
    w, b, d = state.get('W', 'B', 'D')
    print(f"Humidity Ratio: {w:.6f} kg/kg")
    print(f"Wet Bulb Temperature: {b - 273.15:.2f}°C")
    print(f"Dew Point: {d - 273.15:.2f}°C")

    # Get more properties
    h, s, v = state.get('H', 'S', 'V')
    print(f"Enthalpy: {h:.2f} J/kg")
    print(f"Entropy: {s:.2f} J/kg-K")
    print(f"Specific Volume: {v:.4f} m³/kg")

    # Show constraints
    print("\nConstraints:")
    print(state.constraints())

    # Update a constraint
    print("\n--- Updating Temperature to 30°C ---")
    state.reset('T', 303.15)
    print(f"New Temperature: {state.get('T')-273.15:.2f}°C")
    print(f"New Humidity Ratio: {state.get('W'):.6f} kg/kg")

    # Replace a constraint
    print("\n--- Replacing Relative Humidity with Humidity Ratio ---")
    humidity_ratio = state.get('W')
    state.replace('R', 'W', humidity_ratio)
    print("New Constraints:")
    print(state.constraints())


def example_humid_air_error_handling():
    """
    Example of error handling and input validation in humid air calculations
    """
    print("\n=== Humid Air Error Handling and Validation ===")

    # Example of trying to set an invalid temperature (below absolute zero)
    try:
        StateHA('T', -300, 'P', 101325, 'R', 0.5)
    except ValueError as e:
        print(f"Error setting invalid temperature: {e}")

    # Example of trying to set an invalid relative humidity (greater than 1)
    try:
        StateHA('T', 293.15, 'P', 101325, 'R', 1.5)
    except ValueError as e:
        print(f"Error setting invalid relative humidity: {e}")

    # Example of trying to create a state with too many constraints
    try:
        # Attempt to create a state with 4 constraints (only 3 allowed)
        StateHA('T', 298.15, 'P', 101325, 'R', 0.5, 'B', 290)
    except Exception as e:
        print(f"Error over-constraining the system: {e}")

    # Example of setting inconsistent properties
    try:
        # Setting a dew point higher than dry bulb is physically impossible
        StateHA('T', 298.15, 'P', 101325, 'D', 303.15)  # 30°C dew point, which is > 25°C dry bulb
    except ValueError as e:
        print(f"Error setting inconsistent properties: {e}")


def example_pure_fluid_basic():
    """
    Basic example of using StateProps for pure fluid properties
    """
    print("\n=== Basic Pure Fluid Properties (Water) ===")

    # Create a state for water at 100°C, 1 atm
    water = StateProps('T', 373.15, 'P', 101325, 'water')

    # Access and print properties using get() method
    print(f"Temperature: {water.get('T')-273.15:.2f}°C")
    print(f"Pressure: {water.get('P'):.0f} Pa")

    # Get multiple properties in one call
    d, h, s = water.get('D', 'H', 'S')
    print(f"Density: {d:.4f} kg/m³")
    print(f"Enthalpy: {h:.2f} J/kg")
    print(f"Entropy: {s:.2f} J/kg-K")

    # Get more properties
    c, o, q = water.get('C', 'O', 'Q')
    print(f"Specific Heat Capacity (cp): {c:.2f} J/kg-K")
    print(f"Specific Heat Capacity (cv): {o:.2f} J/kg-K")
    print(f"Vapor Quality: {q}")

    # Show constraints
    print("\nConstraints:")
    print(water.constraints())

    # Update a constraint
    print("\n--- Updating Temperature to 120°C ---")
    water.reset('T', 393.15)
    print(f"New Temperature: {water.get('T')-273.15:.2f}°C")
    print(f"New Density: {water.get('D'):.4f} kg/m³")

    # Replace a constraint
    print("\n--- Replacing Pressure with Density ---")
    density = water.get('D')
    water.replace('P', 'D', density)
    print("New Constraints:")
    print(water.constraints())

    # Test refrigerant properties (R134a at 25°C, 10 bar)
    print("\n--- Testing Refrigerant (R134a) ---")
    r134a = StateProps('T', 298.15, 'P', 1000000, 'R134a')
    print(f"Temperature: {r134a.get('T')-273.15:.2f}°C")
    print(f"Pressure: {r134a.get('P')/100000:.2f} bar")
    print(f"Density: {r134a.get('D'):.2f} kg/m³")
    try:
        quality = r134a.get('Q')
        print(f"Quality: {quality}")
    except ValueError:
        print("Quality: Not in two-phase region")


def example_property_info():
    """
    Example showing property codes and their meanings
    """
    print("\n=== Property Information ===")

    print("Humid Air Property Codes (StateHA):")
    print("  'T': Dry Bulb Temperature [K]")
    print("  'B': Wet bulb temperature [K]")
    print("  'D': Dew point temperature [K]")
    print("  'P': Pressure [Pa]")
    print("  'V': Mixture volume [m³/kg dry air]")
    print("  'R': Relative humidity [0-1]")
    print("  'W': Humidity ratio [kg water/kg dry air]")
    print("  'H': Mixture enthalpy [J/kg dry air]")
    print("  'S': Mixture entropy [J/kg dry air/K]")
    print("  'C': Mixture specific heat [J/kg dry air/K]")
    print("  'M': Mixture viscosity [Pa-s]")
    print("  'K': Mixture thermal conductivity [W/m/K]")

    print("\nPure Fluid Property Codes (StateProps):")
    print("  'T': Temperature [K]")
    print("  'P': Pressure [Pa]")
    print("  'D': Density [kg/m³]")
    print("  'H': Specific enthalpy [J/kg]")
    print("  'S': Specific entropy [J/kg-K]")
    print("  'Q': Vapor quality [-]")
    print("  'C': Specific heat capacity at constant pressure [J/kg-K]")
    print("  'O': Specific heat capacity at constant volume [J/kg-K]")
    print("  'U': Specific internal energy [J/kg]")


if __name__ == "__main__":
    print("Testing CoolProp-OOP Package v2.0.0")
    example_humid_air_basic()
    example_humid_air_error_handling()
    example_pure_fluid_basic()
    example_property_info()
    print("\nAll examples completed successfully!")

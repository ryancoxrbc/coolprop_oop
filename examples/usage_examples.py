#!/usr/bin/env python3

from coolprop_oop import StateHA, StateProps

def test_humid_air():
    print("\n=== Testing Humid Air Properties ===")
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

def test_pure_fluid():
    print("\n=== Testing Pure Fluid Properties ===")
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
    except ValueError as e:
        print(f"Quality: Not in two-phase region")

def test_property_info():
    print("\n=== Property Information ===")
    ha = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
    
    props = StateProps('T', 373.15, 'P', 101325, 'water')

if __name__ == "__main__":
    print("Testing CoolProp-OOP Package v0.2.0")
    test_humid_air()
    test_pure_fluid()
    test_property_info()
    print("\nAll tests completed successfully!") 
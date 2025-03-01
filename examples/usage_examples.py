#!/usr/bin/env python3

from coolprop_oop import StateHA, StatePROPS

def test_humid_air():
    print("\n=== Testing Humid Air Properties ===")
    # Create a state for humid air at 20°C, 1 atm, 50% RH
    state = StateHA()
    state.press = 101325
    state.tempc = 20
    state.relhum = 0.5
    
    # Access and print properties
    print(f"Temperature: {state.tempc:.2f}°C")
    print(f"Pressure: {state.press:.0f} Pa")
    print(f"Relative Humidity: {state.relhum * 100:.1f}%")
    print(f"Humidity Ratio: {state.humrat:.6f} kg/kg")
    
    # Handle potential None values
    if state.wetbulb is not None:
        print(f"Wet Bulb Temperature: {state.wetbulb - 273.15:.2f}°C")
    else:
        print("Wet Bulb Temperature: Not available")
        
    if state.dewpoint is not None:
        print(f"Dew Point: {state.dewpoint - 273.15:.2f}°C")
    else:
        print("Dew Point: Not available")
        
    if state.enthalpy is not None:
        print(f"Enthalpy: {state.enthalpy:.2f} J/kg")
    else:
        print("Enthalpy: Not available")
        
    if state.density is not None:
        print(f"Density: {state.density:.4f} kg/m³")
    else:
        print("Density: Not available")

def test_pure_fluid():
    print("\n=== Testing Pure Fluid Properties ===")
    # Create a state for water at 100°C, 1 atm
    state = StatePROPS()
    state.fluid = 'water'
    state.tempc = 100
    state.press = 101325
    
    # Access and print properties
    print(f"Temperature: {state.tempc:.2f}°C")
    print(f"Pressure: {state.press:.0f} Pa")
    
    # Handle potential None values
    if state.dens is not None:
        print(f"Density: {state.dens:.2f} kg/m³")
    else:
        print("Density: Not available")
        
    if state.enthalpy is not None:
        print(f"Enthalpy: {state.enthalpy:.2f} J/kg")
    else:
        print("Enthalpy: Not available")
        
    if state.entropy is not None:
        print(f"Entropy: {state.entropy:.2f} J/kg-K")
    else:
        print("Entropy: Not available")
        
    if state.cp is not None:
        print(f"Specific Heat Capacity (cp): {state.cp:.2f} J/kg-K")
    else:
        print("Specific Heat Capacity (cp): Not available")
    
    # Display state constraints information including status and edition
    print("\n--- State Constraint Information ---")
    constraints = state.constraints
    print(f"Set properties: {', '.join(constraints['properties'])}")
    print(f"Fluid: {constraints['fluid']}")
    print(f"Is complete: {constraints['is_complete']}")
    print(f"Status: {constraints['status'] if constraints['status'] is not None else 'Not available'}")
    print(f"Edition: {constraints['edition'] if constraints['edition'] is not None else 'Not available'}")
    
    # Test refrigerant properties (R134a at 25°C, 10 bar)
    print("\n--- Testing Refrigerant (R134a) ---")
    r134a = StatePROPS()
    r134a.fluid = 'R134a'
    r134a.tempc = 25
    r134a.press = 1000000
    
    print(f"Temperature: {r134a.tempc:.2f}°C")
    print(f"Pressure: {r134a.press/100000:.2f} bar")
    
    if r134a.dens is not None:
        print(f"Density: {r134a.dens:.2f} kg/m³")
    else:
        print("Density: Not available")
        
    if r134a.quality is not None:
        print(f"Quality: {r134a.quality}")
    else:
        print("Quality: Not available")
    
    # Display state constraints for R134a
    constraints = r134a.constraints
    print(f"\nR134a Status: {constraints['status'] if constraints['status'] is not None else 'Not available'}")
    print(f"R134a Edition: {constraints['edition'] if constraints['edition'] is not None else 'Not available'}")

if __name__ == "__main__":
    print("Testing CoolProp-OOP Package")
    test_humid_air()
    test_pure_fluid()
    print("\nAll tests completed successfully!") 
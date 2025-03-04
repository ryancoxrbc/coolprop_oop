from CoolProp.CoolProp import HAPropsSI, PropsSI
import warnings
from functools import wraps

def validate_input_ha(func):
    """
    Decorator for validating physical constraints of humid air property inputs.
    
    Checks that input values are within physically reasonable ranges before
    allowing them to be set. This runs before state_setter_ha to ensure
    basic physical validity before attempting CoolProp calculations.
    """
    @wraps(func)
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        
        # Basic type checking
        if not isinstance(value, (int, float)):
            raise TypeError(f"{prop_name} must be a number")
            
        # Property-specific validation
        if prop_name in ['tempk', 'wetbulb', 'dewpoint']:
            if value <= 0:
                raise ValueError(f"{prop_name} must be above absolute zero")
            if value > 473.15:  # ~200°C - reasonable upper limit for humid air
                raise ValueError(f"{prop_name} exceeding reasonable range (> 200°C)")
                
        elif prop_name == 'tempc':
            if value < -273.15:
                raise ValueError("Temperature cannot be below absolute zero")
            if value > 200:  # Reasonable upper limit for humid air
                raise ValueError("Temperature exceeding reasonable range (> 200°C)")
                
        elif prop_name == 'press':
            if value <= 0:
                raise ValueError("Pressure must be positive")
            if value < 1000:  # 1 kPa - very low pressure
                raise ValueError("Pressure below reasonable range (< 1 kPa)")
            if value > 1e7:  # 100 bar - very high pressure
                raise ValueError("Pressure exceeding reasonable range (> 100 bar)")
                
        elif prop_name == 'relhum':
            if value < 0:
                raise ValueError("Relative humidity cannot be negative")
            if value > 1:
                raise ValueError("Relative humidity cannot exceed 1 (100%)")
                
        elif prop_name == 'humrat':
            if value < 0:
                raise ValueError("Humidity ratio cannot be negative")
            if value > 1:  # Extremely high - likely an error
                raise ValueError("Humidity ratio exceeding reasonable range (> 1 kg/kg)")
        
        # Validation for newly settable properties
        elif prop_name == 'vol':
            if value <= 0:
                raise ValueError("Specific volume must be positive")
            if value > 1000:  # Very high specific volume
                raise ValueError("Specific volume exceeding reasonable range (> 1000 m³/kg)")
                
        elif prop_name == 'enthalpy':
            # No strict limits on enthalpy, but should be reasonable
            if abs(value) > 1e7:  # Very high enthalpy
                raise ValueError("Enthalpy exceeding reasonable range (|h| > 10,000,000 J/kg)")
                
        elif prop_name == 'entropy':
            # No strict limits on entropy, but should be reasonable
            if abs(value) > 1e5:  # Very high entropy
                raise ValueError("Entropy exceeding reasonable range (|s| > 100,000 J/kg-K)")
                
        elif prop_name == 'density':
            if value <= 0:
                raise ValueError("Density must be positive")
            if value > 50:  # Very high density for humid air
                raise ValueError("Density exceeding reasonable range (> 50 kg/m³)")
                
        elif prop_name == 'cp':
            if value <= 0:
                raise ValueError("Specific heat capacity must be positive")
            if value > 10000:  # Very high cp
                raise ValueError("Specific heat capacity exceeding reasonable range (> 10,000 J/kg-K)")
        
        elif prop_name == 'viscosity':
            if value <= 0:
                raise ValueError("Viscosity must be positive")
            if value > 1:  # Very high viscosity for air
                raise ValueError("Viscosity exceeding reasonable range (> 1 Pa⋅s)")
                
        elif prop_name == 'conductivity':
            if value <= 0:
                raise ValueError("Thermal conductivity must be positive")
            if value > 1:  # Very high thermal conductivity for air
                raise ValueError("Thermal conductivity exceeding reasonable range (> 1 W/m-K)")
                
        elif prop_name == 'prandtl':
            if value <= 0:
                raise ValueError("Prandtl number must be positive")
            if value > 1000:  # Very high Prandtl number
                raise ValueError("Prandtl number exceeding reasonable range (> 1000)")
        
        return func(self, value)
    return wrapper

def state_setter_ha(func):
    """
    Decorator for property setters that manages state constraints for humid air properties.
    
    Checks if this property is already set before allowing the property to be set.
    Property state validity is handled by CoolProp, and exceptions are passed to user.
    Also tracks which properties have been set for state validation.
    """
    @wraps(func)
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        
        # Initialize constraints set if not exists
        if not hasattr(self, '_constraints_set'):
            self._constraints_set = set()
        
        # Always allow setting if we have 0 or 1 constraint or if this property is already set
        if len(self._constraints_set) < 2 or prop_name in self._constraints_set:
            func(self, value)
            self._constraints_set.add(prop_name)
            return
            
        # If we have 2+ constraints, try setting the new property
        # CoolProp will validate state and throw error if invalid
        try:
            # Try to set the property
            func(self, value)
            # If successful, add to constraints
            self._constraints_set.add(prop_name)
        except Exception as e:
            # Pass along any CoolProp errors to the user
            raise ValueError(f"Cannot set {prop_name} - {str(e)}")
            
    return wrapper

def validate_input_props(func):
    """
    Decorator for validating physical constraints of pure fluid property inputs.
    
    Checks that input values are within physically reasonable ranges before
    allowing them to be set. This runs before state_setter_PROPS to ensure
    basic physical validity before attempting CoolProp calculations.
    """
    @wraps(func)
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        
        # Basic type checking
        if not isinstance(value, (int, float)):
            raise TypeError(f"{prop_name} must be a number")
            
        # Property-specific validation
        if prop_name in ['tempk']:
            if value <= 0:
                raise ValueError(f"{prop_name} must be above absolute zero")
            if value > 2000:  # Very high temperature limit for general fluids
                raise ValueError(f"{prop_name} exceeding reasonable range (> 1726.85°C)")
                
        elif prop_name == 'tempc':
            if value < -273.15:
                raise ValueError("Temperature cannot be below absolute zero")
            if value > 1726.85:  # Very high temperature limit for general fluids
                raise ValueError("Temperature exceeding reasonable range (> 1726.85°C)")
                
        elif prop_name == 'press':
            if value <= 0:
                raise ValueError("Pressure must be positive")
            if value > 1e9:  # 10000 bar - very high pressure
                raise ValueError("Pressure exceeding reasonable range (> 10000 bar)")
                
        elif prop_name == 'dens':
            if value <= 0:
                raise ValueError("Density must be positive")
            if value > 1e5:  # Very high density
                raise ValueError("Density exceeding reasonable range (> 100000 kg/m³)")
                
        elif prop_name == 'quality':
            if value < 0 or value > 1:
                raise ValueError("Quality must be between 0 and 1")
                
        # Validation for newly settable properties
        elif prop_name == 'enthalpy':
            # No strict limits on enthalpy, but should be reasonable
            if abs(value) > 1e8:  # Very high enthalpy
                raise ValueError("Enthalpy exceeding reasonable range (|h| > 100,000,000 J/kg)")
                
        elif prop_name == 'entropy':
            # No strict limits on entropy, but should be reasonable
            if abs(value) > 1e6:  # Very high entropy
                raise ValueError("Entropy exceeding reasonable range (|s| > 1,000,000 J/kg-K)")
                
        elif prop_name == 'cp':
            if value <= 0:
                raise ValueError("Specific heat capacity at constant pressure must be positive")
            if value > 1e5:  # Very high cp
                raise ValueError("Specific heat capacity exceeding reasonable range (> 100,000 J/kg-K)")
                
        elif prop_name == 'cv':
            if value <= 0:
                raise ValueError("Specific heat capacity at constant volume must be positive")
            if value > 1e5:  # Very high cv
                raise ValueError("Specific heat capacity exceeding reasonable range (> 100,000 J/kg-K)")
        
        return func(self, value)
    return wrapper

def state_setter_PROPS(func):
    """
    Decorator for property setters that manages state constraints for pure fluid properties.
    
    Checks if fluid is set before allowing properties to be set.
    Checks if this property is already set before allowing changes.
    Property state validity is handled by CoolProp, and exceptions are passed to user.
    Also tracks which properties have been set for state validation.
    """
    @wraps(func)
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        
        # Check if fluid is set before allowing any property to be set
        if not hasattr(self, '_fluid') or self._fluid is None:
            raise ValueError(f"Cannot set {prop_name} - fluid type must be set first with state.fluid = 'fluid_name'")
        
        # Initialize constraints set if not exists
        if not hasattr(self, '_constraints_set'):
            self._constraints_set = set()
        
        # Always allow setting if we have 0 or 1 constraint or if this property is already set
        if len(self._constraints_set) < 2 or prop_name in self._constraints_set:
            func(self, value)
            self._constraints_set.add(prop_name)
            return
            
        # If we already have 2 constraints, try to set the property
        # CoolProp will validate state and throw error if invalid
        try:
            # Try to set the property
            func(self, value)
            # If successful, add to constraints
            self._constraints_set.add(prop_name)
        except Exception as e:
            # Pass along any CoolProp errors to the user
            raise ValueError(f"Cannot set {prop_name} - {str(e)}")
            
    return wrapper

def cached_property(func):
    """
    Decorator for property getters that implements version-based caching.
    
    If the property is part of the constraints set, returns the directly set value.
    Otherwise, checks if the cached value is from the current state version before returning it.
    If not current, recalculates the property and updates the cache.
    """
    @wraps(func)
    def getter(self):
        prop_name = func.__name__
        version_attr = f"_{prop_name}_version"
        value_attr = f"_{prop_name}"
        
        # If we don't have 3 constraints yet, can't calculate anything
        if not hasattr(self, '_constraints_set') or len(self._constraints_set) < 3:
            return getattr(self, value_attr)
        
        # If this property is one of our constraints, return the set value
        if prop_name in self._constraints_set:
            return getattr(self, value_attr)
        
        # Otherwise, check if we need to update the cached value
        if (not hasattr(self, version_attr) or 
            getattr(self, version_attr) != self._version):
            # Get the CoolProp property name from our mapping
            coolprop_name = self._prop_map[prop_name]
            # Calculate and store the new value
            value = self.get_prop(coolprop_name)
            setattr(self, value_attr, value)
            # Update the version
            setattr(self, version_attr, self._version)
        
        return getattr(self, value_attr)
    
    return getter

class StateHA:
    """
    A class representing the thermodynamic state of humid air.
    
    This class provides an object-oriented interface to CoolProp's HAPropsSI function
    for humid air properties. It automatically calculates and caches common properties
    for easy access.
    
    Property codes used in this class are compatible with CoolProp version 6.7.0.
    
    Property Codes:
        'T': Dry Bulb Temperature [K]
        'B': Wet bulb temperature [K]
        'D': Dew point temperature [K]
        'P': Pressure [Pa]
        'V': Mixture volume [m³/kg dry air]
        'R': Relative humidity [0-1]
        'W': Humidity ratio [kg water/kg dry air]
        'H': Mixture enthalpy [J/kg dry air]
        'S': Mixture entropy [J/kg dry air/K]
        'C': Mixture specific heat [J/kg dry air/K]
        'M': Mixture viscosity [Pa-s]
        'K': Mixture thermal conductivity [W/m/K]
        
    Properties are accessed using the get() method rather than direct attributes.
    
    Example:
        >>> # Create state at 25°C, 1 atm, 60% RH
        >>> state = StateHA('P', 101325, 'T', 298.15, 'R', 0.6)
        >>> print(f"Humidity ratio: {state.get('W'):.4f} kg/kg")
        Humidity ratio: 0.0120 kg/kg
        >>> print(f"Dew point: {state.get('D')-273.15:.1f}°C")
        Dew point: 16.7°C
    """

    def __init__(self, *args):
        """
        Initialize a StateHA object for humid air properties.
        
        Args:
            *args: Six arguments in the order: prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value
                  where prop_name is a CoolProp property code (str) and value is a float.
                  This format follows the HAPropsSI's parameter order.
        
        Example:
            >>> # Create state at 25°C, 1 atm, 60% RH
            >>> state = StateHA('P', 101325, 'T', 298.15, 'R', 0.6)
        """
        self._constraints = {}
        
        if args:
            if len(args) != 6:
                raise ValueError("StateHA requires exactly 6 arguments: prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value")
            
            # Check that odd-indexed arguments are strings (property codes)
            if not all(isinstance(args[i], str) for i in range(0, 6, 2)):
                raise ValueError("Property names must be strings")
            
            # Check that even-indexed arguments are numeric (property values)
            if not all(isinstance(args[i], (int, float)) for i in range(1, 6, 2)):
                raise ValueError("Property values must be numeric")
            
            # Store constraints
            self._constraints[args[0]] = args[1]
            self._constraints[args[2]] = args[3]
            self._constraints[args[4]] = args[5]
    
    def replace(self, old_prop, new_prop, value):
        """
        Replace one constraint with a new constraint.
        
        This method updates the state by replacing one constraint with a new one.
        
        Args:
            old_prop (str): The property code to remove from constraints
            new_prop (str): The property code to add as a constraint
            value (float): The value for the new property constraint
        
        Returns:
            StateHA: The current object for method chaining.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> state.replace('R', 'W', 0.01)  # Replace RH with humidity ratio
        """
        if old_prop not in self._constraints:
            raise ValueError(f"Property '{old_prop}' is not a current constraint")
        
        if not isinstance(new_prop, str):
            raise ValueError("New property name must be a string")
            
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Remove old constraint and add new one
        del self._constraints[old_prop]
        self._constraints[new_prop] = value
        
        return self
    
    def reset(self, prop, value):
        """
        Reset a single property constraint to a new value.
        
        This method updates an existing property constraint with a new value.
        
        Args:
            prop (str): The property code to reset
            value (float): The new value for the property constraint
        
        Returns:
            StateHA: The current object for method chaining.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> state.reset('T', 303.15)  # Update temperature to 30°C
        """
        if prop not in self._constraints:
            raise ValueError(f"Property '{prop}' is not a current constraint")
        
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Update the constraint value
        self._constraints[prop] = value
        
        return self
    
    def get(self, *props):
        """
        Get specific properties from the current state.
        
        Args:
            *props: One or more property codes to retrieve.
                Valid options include (compatible with CoolProp 6.7.0):
                'T': Dry Bulb Temperature [K]
                'B': Wet bulb temperature [K]
                'D': Dew point temperature [K]
                'P': Pressure [Pa]
                'V': Mixture volume [m³/kg dry air]
                'R': Relative humidity [0-1]
                'W': Humidity ratio [kg water/kg dry air]
                'H': Mixture enthalpy [J/kg dry air]
                'S': Mixture entropy [J/kg dry air/K]
                'C': Mixture specific heat [J/kg dry air/K]
                'M': Mixture viscosity [Pa-s]
                'K': Mixture thermal conductivity [W/m/K]
            
        Returns:
            float or list: The value(s) of the requested properties. If a single property 
                  is requested, returns a float; otherwise, returns a list of floats.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> h = state.get('H')  # Get specific enthalpy
            >>> h, s = state.get('H', 'S')  # Get enthalpy and entropy
        """
        if not props:
            raise ValueError("At least one property must be specified")
        
        if len(self._constraints) != 3:
            raise ValueError("State is not fully defined. Need exactly 3 constraints.")
        
        # Extract constraints for HAPropsSI call
        props_list = []
        for k, v in self._constraints.items():
            props_list.extend([k, v])
        
        # Calculate requested properties
        result = []
        for prop in props:
            value = HAPropsSI(prop, *props_list)
            result.append(value)
        
        # Return single value if only one property requested
        if len(props) == 1:
            return result[0]
        
        return result

    def constraints(self):
        """
        Returns the current set of properties constraining the state with their values.
        
        Returns:
            dict: A dictionary of property names and their values that are currently set as constraints.
        
        Example:
            >>> state = StateHA('T', 293.15, 'P', 101325, 'R', 0.5)
            >>> state.constraints()
            {'T': 293.15, 'P': 101325, 'R': 0.5}
        """
        return self._constraints.copy()

class StateProps:
    """
    A class representing the thermodynamic state of a pure fluid.
    
    This class provides an object-oriented interface to CoolProp's PropsSI function
    for pure fluid properties. It automatically calculates and caches common properties
    for easy access.
    
    Property codes used in this class are compatible with CoolProp version 6.7.0.
    
    Property Codes:
        'T': Temperature [K]
        'P': Pressure [Pa]
        'D': Density [kg/m³]
        'H': Specific enthalpy [J/kg]
        'S': Specific entropy [J/kg-K]
        'U': Specific internal energy [J/kg]
        'Q': Vapor quality [-]
        'C': Specific heat capacity at constant pressure [J/kg-K]
        'O': Specific heat capacity at constant volume [J/kg-K]
    
    Properties are accessed using the get() method rather than direct attributes.
    
    Example:
        >>> # Create state for water at 100°C, 1 atm
        >>> water = StateProps('P', 101325, 'T', 373.15, 'water')
        >>> print(f"Density: {water.get('D'):.1f} kg/m³")
        Density: 0.6 kg/m³
        >>> # Get information about available properties
    """
    
    def __init__(self, *args):
        """
        Initialize a StateProps object for pure fluid properties.
        
        Args:
            *args: Five arguments in the order: prop1_name, prop1_value, prop2_name, prop2_value, fluid_name
                  where prop_name is a CoolProp property code (str), value is a float, and fluid_name is a string.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
        """
        self._constraints = {}
        self._fluid = None
        
        if args:
            if len(args) != 5:
                raise ValueError("StateProps requires exactly 5 arguments: prop1_name, prop1_value, prop2_name, prop2_value, fluid_name")
            
            # Check that property names are strings
            if not isinstance(args[0], str) or not isinstance(args[2], str):
                raise ValueError("Property names must be strings")
            
            # Check that property values are numeric
            if not isinstance(args[1], (int, float)) or not isinstance(args[3], (int, float)):
                raise ValueError("Property values must be numeric")
            
            # Check that fluid name is a string
            if not isinstance(args[4], str):
                raise ValueError("Fluid name must be a string")
            
            # Store constraints and fluid
            self._constraints[args[0]] = args[1]
            self._constraints[args[2]] = args[3]
            self._fluid = args[4]

    def replace(self, old_prop, new_prop, value):
        """
        Replace one constraint with a new constraint.
        
        This method updates the state by replacing one constraint with a new one.
        
        Args:
            old_prop (str): The property code to remove from constraints
            new_prop (str): The property code to add as a constraint
            value (float): The value for the new property constraint
        
        Returns:
            StateProps: The current object for method chaining.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> state.replace('P', 'D', 958.4)  # Replace pressure with density
        """
        if old_prop not in self._constraints:
            raise ValueError(f"Property '{old_prop}' is not a current constraint")
        
        if not isinstance(new_prop, str):
            raise ValueError("New property name must be a string")
            
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Remove old constraint and add new one
        del self._constraints[old_prop]
        self._constraints[new_prop] = value
        
        return self
    
    def reset(self, prop, value):
        """
        Reset a single property constraint to a new value.
        
        This method updates an existing property constraint with a new value,
        without changing the fluid type.
        
        Args:
            prop (str): The property code to reset
            value (float): The new value for the property constraint
        
        Returns:
            StateProps: The current object for method chaining.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> state.reset('T', 393.15)  # Update temperature to 120°C
        """
        if prop not in self._constraints:
            raise ValueError(f"Property '{prop}' is not a current constraint")
        
        if not isinstance(value, (int, float)):
            raise ValueError("Property value must be numeric")
        
        # Update the constraint value
        self._constraints[prop] = value
        
        return self
    
    def get(self, *props):
        """
        Get specific properties from the current state.
        
        Args:
            *props: One or more property codes to retrieve.
                Valid options include (compatible with CoolProp 6.7.0):
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'D': Density [kg/m³]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'Q': Vapor quality [-]
                - 'C': Specific heat capacity at constant pressure [J/kg-K]
                - 'O': Specific heat capacity at constant volume [J/kg-K]
            
        Returns:
            float or list: The value(s) of the requested properties. If a single property 
                  is requested, returns a float; otherwise, returns a list of floats.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> h = state.get('H')  # Get specific enthalpy
            >>> h, s = state.get('H', 'S')  # Get enthalpy and entropy
        """
        if not props:
            raise ValueError("At least one property must be specified")
        
        if len(self._constraints) != 2:
            raise ValueError("State is not fully defined. Need exactly 2 constraints.")
        
        if not self._fluid:
            raise ValueError("Fluid not specified")
        
        # Extract constraints for PropsSI call
        input_props = []
        input_vals = []
        for k, v in self._constraints.items():
            input_props.append(k)
            input_vals.append(v)
        
        # Calculate requested properties
        result = []
        for prop in props:
            value = PropsSI(prop, input_props[0], input_vals[0], input_props[1], input_vals[1], self._fluid)
            result.append(value)
        
        # Return single value if only one property requested
        if len(props) == 1:
            return result[0]
        
        return result
    
    def constraints(self):
        """
        Returns the current set of properties constraining the state with their values.
        
        Returns:
            dict: A dictionary of property names and their values that are currently 
                 set as constraints, including the fluid name.
        
        Example:
            >>> state = StateProps('T', 373.15, 'P', 101325, 'water')
            >>> state.constraints()
            {'T': 373.15, 'P': 101325, 'fluid': 'water'}
        """
        constraints = self._constraints.copy()
        if self._fluid:
            constraints['fluid'] = self._fluid
        return constraints
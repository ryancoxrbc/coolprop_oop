from CoolProp.CoolProp import HAPropsSI, PropsSI

def state_setter_HA(func):
    """
    Decorator for property setters that manages state constraints for humid air properties.
    
    Checks the number of constraints and version before allowing property to be set.
    Prevents overconstraining the system while allowing property updates when version changes.
    Also tracks which properties have been set for state validation.
    """
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        
        # Initialize constraints set if not exists
        if not hasattr(self, '_constraints_set'):
            self._constraints_set = set()
        
        # Initialize version if not exists
        if not hasattr(self, '_version'):
            self._version = 0
        
        # Allow setting if we have 0 or 1 constraint
        if len(self._constraints_set) < 2:
            func(self, value)
            self._constraints_set.add(prop_name)
            return
            
        # If we have 2 constraints, test validity before adding third
        if len(self._constraints_set) == 2:
            try:
                self.test_state_validity(self._constraints_set, prop_name, value)
                func(self, value)
                self._constraints_set.add(prop_name)
                # Increment version when third property is successfully set
                self._version += 1
            except ValueError as e:
                raise ValueError(f"Cannot set {prop_name} - {str(e)}")
            return
            
        # If we have 3 constraints, only allow if property was previously set
        if len(self._constraints_set) == 3:
            if prop_name not in self._constraints_set:
                raise ValueError(f"Cannot set {prop_name} - system is already fully constrained. "
                               "Setting this property would overconstrain the state.")
            # Create a set of the other two properties (excluding the one being updated)
            other_props = self._constraints_set - {prop_name}
            # Test if the new value creates a valid state with the other two properties
            try:
                self.test_state_validity(other_props, prop_name, value)
                func(self, value)
                # Increment version when property is successfully updated
                self._version += 1
            except ValueError as e:
                raise ValueError(f"Cannot set {prop_name} - {str(e)}")
            return
            
    return wrapper

def unsettable_property(func):
    """
    Decorator for properties that should not be settable.
    
    Raises an AttributeError if an attempt is made to set the property.
    Used for properties that are calculated from other state variables and
    should not be directly set.
    """
    def wrapper(self, value):
        prop_name = func.__name__.replace('_setter', '')
        raise AttributeError(f"{prop_name} cannot be set directly as it is calculated "
                           "from other state properties.")
    return wrapper

class StateHA:
    """
    A class representing the thermodynamic state of humid air.
    
    This class provides an object-oriented interface to CoolProp's HAPropsSI function
    for humid air properties. It automatically calculates and caches common properties
    for easy access.
    
    Attributes:
        tempk (float): Temperature in Kelvin
        tempc (float): Temperature in Celsius
        press (float): Pressure in Pa
        humrat (float): Humidity ratio in kg/kg
        wetbulb (float): Wet bulb temperature in K
        relhum (float): Relative humidity (0-1)
        vol (float): Specific volume in m³/kg
        enthalpy (float): Specific enthalpy in J/kg
        entropy (float): Specific entropy in J/kg-K
        dewpoint (float): Dew point temperature in K
        density (float): Density in kg/m³
        cp (float): Specific heat capacity at constant pressure in J/kg-K
    
    Example:
        >>> # Create state at 25°C, 1 atm, 60% RH
        >>> state = StateHA(['P', 101325, 'T', 298.15, 'R', 0.6])
        >>> print(f"Humidity ratio: {state.humrat:.4f} kg/kg")
        Humidity ratio: 0.0120 kg/kg
        >>> print(f"Dew point: {state.dewpoint-273.15:.1f}°C")
        Dew point: 16.7°C
    """
    
    _prop_map = {
        'tempk': 'T',
        'tempc': 'T',  # Will need special handling for Celsius conversion
        'press': 'P',
        'humrat': 'W',
        'wetbulb': 'B',
        'relhum': 'R',
        'dewpoint': 'D',
        'vol': 'V',
        'enthalpy': 'H', 
        'entropy': 'S',
        'density': 'D',
        'cp': 'C',
        'viscosity': 'M',
        'conductivity': 'K',
        'compressibility': 'Z',
        'prandtl': 'L'
    }

    def __init__(self):
        """
        Initialize a StateHA object for humid air properties.
        
        Args:
            props (list, optional): Property inputs for HAPropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value]
                where prop_name can be:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'R': Relative humidity [-]
                - 'W': Humidity ratio [kg/kg]
                - 'B': Wet bulb temperature [K]
                - 'D': Dew point temperature [K]
                If provided, properties are calculated immediately.
        
        Example:
            >>> state = StateHA(['T', 293.15, 'P', 101325, 'R', 0.5])
        """
        self._tempk = None
        self._tempc = None
        self._press = None
        self._humrat = None
        self._wetbulb = None
        self._relhum = None
        self._vol = None
        self._enthalpy = None
        self._entropy = None
        self._dewpoint = None
        self._density = None
        self._cp = None
        
        self._version = None
        self._constraints_set = set()

    @property
    def tempk(self):
        return self._tempk

    @state_setter_HA
    @tempk.setter
    def tempk(self, value):
        self._tempk = value

    @property
    def tempc(self):
        return self._tempc if self._tempc is not None else (self._tempk - 273.15 if self._tempk is not None else None)

    @state_setter_HA
    @tempc.setter
    def tempc(self, value):
        self._tempc = value
        self._tempk = value + 273.15

    @property
    def press(self):
        return self._press

    @state_setter_HA
    @press.setter
    def press(self, value):
        self._press = value

    @property
    def humrat(self):
        return self._humrat

    @state_setter_HA
    @humrat.setter
    def humrat(self, value):
        self._humrat = value

    @property
    def wetbulb(self):
        return self._wetbulb

    @state_setter_HA
    @wetbulb.setter
    def wetbulb(self, value):
        self._wetbulb = value

    @property
    def relhum(self):
        return self._relhum

    @state_setter_HA
    @relhum.setter
    def relhum(self, value):
        self._relhum = value

    @property
    def dewpoint(self):
        return self._dewpoint

    @state_setter_HA
    @dewpoint.setter
    def dewpoint(self, value):
        self._dewpoint = value

    @property
    def vol(self):
        return self._vol

    @unsettable_property
    @vol.setter
    def vol(self, value):
        self._vol = value

    @property
    def enthalpy(self):
        return self._enthalpy

    @unsettable_property
    @enthalpy.setter
    def enthalpy(self, value):
        self._enthalpy = value

    @property
    def entropy(self):
        return self._entropy

    @unsettable_property
    @entropy.setter
    def entropy(self, value):
        self._entropy = value

    @property
    def density(self):
        return self._density

    @unsettable_property
    @density.setter
    def density(self, value):
        self._density = value

    @property
    def cp(self):
        return self._cp

    @unsettable_property
    @cp.setter
    def cp(self, value):
        self._cp = value

    
    def set(self, props):
        """
        Set the properties of the StateHA object using the provided inputs.
        
        This method calculates all state properties based on the three input properties
        provided. It uses CoolProp's HAPropsSI function internally.
        
        Args:
            props (list): Property inputs for HAPropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, prop3_name, prop3_value]
        
        Returns:
            StateHA: The current object for method chaining.
        
        Example:
            >>> state = StateHA()
            >>> state.set(['T', 293.15, 'P', 101325, 'R', 0.5])
            >>> print(f"{state.tempc:.1f}°C")
            20.0°C
        """
        self.props = props
        self.tempk = self.get_prop("T")
        self.tempc = self.tempk - 273.15
        self.press = self.get_prop("P")
        self.humrat = self.get_prop("W")
        self.wetbulb = self.get_prop("B")
        self.relhum = self.get_prop("R")
        self.vol = self.get_prop("V")
        self.enthalpy = self.get_prop("H")
        self.entropy = self.get_prop("S")
        self.dewpoint = self.get_prop("D")
        self.density = 1/self.vol
        self.cp = self.get_prop("C")
        
        return self
    
    def get_prop(self, prop):
        """
        Get a specific property using HAPropsSI.
        
        Args:
            prop (str): The property to retrieve. Valid options include:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'W': Humidity ratio [kg/kg]
                - 'R': Relative humidity [-]
                - 'B': Wet bulb temperature [K]
                - 'D': Dew point temperature [K]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'V': Specific volume [m³/kg]
                - 'C': Specific heat capacity [J/kg-K]
            
        Returns:
            float: The value of the requested property.
        
        Example:
            >>> state = StateHA(['T', 293.15, 'P', 101325, 'R', 0.5])
            >>> h = state.get_prop('H')  # Get specific enthalpy
        """
        return HAPropsSI(prop, *self.props)

    def test_state_validity(self, current_props, new_prop, new_value):
        """
        Test if the current state properties are physically valid using HAPropsSI.
        
        Args:
            current_props (set): Set of currently set property names
            new_prop (str): Name of the new property being set
            new_value (float): Value of the new property
        
        Returns:
            bool: True if the state is valid, False otherwise.
        
        Raises:
            ValueError: If the combination of properties would create an invalid state,
                      with the specific error message from CoolProp.
        """
        try:
            # Build a test props list with current properties and new value
            test_props = []
            for prop in current_props:
                coolprop_name = self._prop_map[prop]
                value = getattr(self, f"_{prop}")
                # Handle Celsius conversion
                if prop == 'tempc':
                    value = value + 273.15
                test_props.extend([coolprop_name, value])
            
            # Add the new property
            coolprop_new_prop = self._prop_map[new_prop]
            new_value_converted = new_value + 273.15 if new_prop == 'tempc' else new_value
            test_props.extend([coolprop_new_prop, new_value_converted])
            
            # Try to calculate any property (e.g., enthalpy) with these inputs
            HAPropsSI('H', *test_props)
            return True
            
        except ValueError as e:
            # Re-raise with the CoolProp error message for better explanation
            raise ValueError(f"Invalid state: {str(e)}") from None

class StatePROPS:
    """
    A class representing the thermodynamic state of a pure fluid.
    
    This class provides an object-oriented interface to CoolProp's PropsSI function
    for pure fluid properties. It automatically calculates and caches common properties
    for easy access.
    
    Attributes:
        tempk (float): Temperature in Kelvin
        tempc (float): Temperature in Celsius
        press (float): Pressure in Pa
        dens (float): Density in kg/m³
        enthalpy (float): Specific enthalpy in J/kg
        entropy (float): Specific entropy in J/kg-K
        quality (float): Vapor quality (0-1), or None if not in two-phase region
        cp (float): Specific heat capacity at constant pressure in J/kg-K
        cv (float): Specific heat capacity at constant volume in J/kg-K
    
    Example:
        >>> # Create state for water at 100°C, 1 atm
        >>> water = StatePROPS(['P', 101325, 'T', 373.15, 'water'])
        >>> print(f"Density: {water.dens:.1f} kg/m³")
        Density: 0.6 kg/m³
        >>> # Create state for R134a at 25°C, 10 bar
        >>> r134a = StatePROPS(['P', 1e6, 'T', 298.15, 'R134a'])
        >>> print(f"Density: {r134a.dens:.1f} kg/m³")
        Density: 1209.0 kg/m³
    """
    
    def __init__(self, props=None):
        """
        Initialize a StatePROPS object for pure fluid properties.
        
        Args:
            props (list, optional): Property inputs for PropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, fluid_name]
                where prop_name can be:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'D': Density [kg/m³]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'Q': Vapor quality [-]
                If provided, properties are calculated immediately.
        
        Example:
            >>> state = StatePROPS(['T', 373.15, 'P', 101325, 'water'])
        """
        self.props = None
        self.tempk = None
        self.tempc = None
        self.press = None
        self.dens = None
        self.enthalpy = None
        self.entropy = None
        self.quality = None
        self.cp = None
        self.cv = None
        
        if props is not None:
            self.set(props)
    
    def set(self, props):
        """
        Set the properties of the StatePROPS object using the provided inputs.
        
        This method calculates all state properties based on the two input properties
        and fluid name provided. It uses CoolProp's PropsSI function internally.
        
        Args:
            props (list): Property inputs for PropsSI in the format
                [prop1_name, prop1_value, prop2_name, prop2_value, fluid_name]
        
        Returns:
            StatePROPS: The current object for method chaining.
        
        Example:
            >>> state = StatePROPS()
            >>> state.set(['T', 373.15, 'P', 101325, 'water'])
            >>> print(f"{state.tempc:.1f}°C")
            100.0°C
        """
        self.props = props
        self.tempk = self.get_prop("T")
        self.tempc = self.tempk - 273.15
        self.press = self.get_prop("P")
        self.dens = self.get_prop("D")
        self.enthalpy = self.get_prop("H")
        self.entropy = self.get_prop("S")
        self.quality = self.get_prop("Q")
        self.cp = self.get_prop("C")
        self.cv = self.get_prop("O")
        
        return self
    
    def get_prop(self, prop):
        """
        Get a specific property using PropsSI.
        
        Args:
            prop (str): The property to retrieve. Valid options include:
                - 'T': Temperature [K]
                - 'P': Pressure [Pa]
                - 'D': Density [kg/m³]
                - 'H': Specific enthalpy [J/kg]
                - 'S': Specific entropy [J/kg-K]
                - 'Q': Vapor quality [-]
                - 'C': Specific heat capacity at constant pressure [J/kg-K]
                - 'O': Specific heat capacity at constant volume [J/kg-K]
            
        Returns:
            float: The value of the requested property.
        
        Example:
            >>> state = StatePROPS(['T', 373.15, 'P', 101325, 'water'])
            >>> h = state.get_prop('H')  # Get specific enthalpy
        """
        return PropsSI(prop, *self.props) 
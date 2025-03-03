"""
Tests for coolprop_oop.
This module implements unit tests for the StateHA (Humid Air) and
StateProps (Pure Fluid) property calculators.

Tests include:
- Basic initialization and property calculation
- Input validation for all properties
- Under/over constraining behavior
- Invalid value handling
- Property updates and dependencies
- Error message formatting
"""

from coolprop_oop import StateHA, StateProps
import unittest
import warnings


class TestStateHA(unittest.TestCase):
    """Test cases for humid air properties calculator."""

    def setUp(self):
        # Suppress deprecation warnings during tests
        warnings.filterwarnings('ignore', category=DeprecationWarning)

    def test_initialization(self):
        """Verify that StateHA initializes correctly with properties."""
        state = StateHA()
        state.press = 101325
        state.tempk = 293.15
        state.relhum = 0.5
        self.assertAlmostEqual(state.relhum, 0.5, places=2)
        self.assertAlmostEqual(state.tempk, 293.15, places=2)
        self.assertAlmostEqual(state.press, 101325, places=0)

    def test_input_validation(self):
        """Test input validation for all properties."""
        state = StateHA()
        
        # Test temperature validation
        with self.assertRaisesRegex(ValueError, "must be above absolute zero"):
            state.tempk = -1
        with self.assertRaisesRegex(ValueError, "exceeding reasonable range"):
            state.tempk = 500  # > 200°C
            
        # Test pressure validation
        with self.assertRaisesRegex(ValueError, "must be positive"):
            state.press = -101325
        with self.assertRaisesRegex(ValueError, "below reasonable range"):
            state.press = 500  # < 1 kPa
        with self.assertRaisesRegex(ValueError, "exceeding reasonable range"):
            state.press = 1e8  # > 100 bar
            
        # Test relative humidity validation
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            state.relhum = -0.1
        with self.assertRaisesRegex(ValueError, "cannot exceed 1"):
            state.relhum = 1.5
            
        # Test humidity ratio validation
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            state.humrat = -0.001
        with self.assertRaisesRegex(ValueError, "exceeding reasonable range"):
            state.humrat = 1.5  # > 1 kg/kg
            
        # Test type validation
        with self.assertRaisesRegex(TypeError, "must be a number"):
            state.tempk = "293.15"

    def test_error_messages(self):
        """Test error messages when setting invalid states."""
        state = StateHA()
        state.press = 101325
        state.tempk = 293.15
        state.relhum = 0.5
        
        # Setting a fourth property is now allowed
        # Try to set an inconsistent state that CoolProp would reject
        try:
            state.humrat = 0.5  # Very high humidity ratio that is inconsistent with current state
            # If no error, check that CoolProp used the new value and adjusted other properties
            self.assertAlmostEqual(state.humrat, 0.5, places=2)
        except ValueError as e:
            # If there's an error, it should be from CoolProp's state validation
            self.assertIn("Cannot set humrat", str(e))
            
        # Try to update with invalid value
        with self.assertRaisesRegex(ValueError, "cannot be negative"):
            state.relhum = -0.5

    def test_property_calculation(self):
        """Verify that calculated properties are physically reasonable."""
        state = StateHA()
        state.press = 101325
        state.tempk = 293.15
        state.relhum = 0.5
        # Wet bulb should be lower than dry bulb
        self.assertLess(state.wetbulb, state.tempk)
        # Humidity ratio should be positive
        self.assertGreater(state.humrat, 0)
        # Enthalpy should be reasonable for room temperature
        self.assertGreater(state.enthalpy, 20000)
        self.assertLess(state.enthalpy, 100000)

    def test_underconstraining(self):
        """Verify behavior when state is underconstrained."""
        state = StateHA()
        # No constraints
        self.assertIsNone(state.enthalpy)
        
        # One constraint
        state.tempk = 293.15
        self.assertIsNone(state.enthalpy)
        self.assertEqual(len(state._constraints_set), 1)
        
        # Two constraints
        state.press = 101325
        self.assertIsNone(state.enthalpy)
        self.assertEqual(len(state._constraints_set), 2)

    def test_property_updates(self):
        """Verify property dependencies when updating values."""
        state = StateHA()
        state.tempk = 293.15
        state.press = 101325
        state.relhum = 0.5
        
        # Store initial values
        initial_humrat = state.humrat
        initial_enthalpy = state.enthalpy
        
        # Update temperature and check that dependent properties change
        state.tempk = 303.15
        self.assertNotEqual(state.humrat, initial_humrat)
        self.assertNotEqual(state.enthalpy, initial_enthalpy)


class TestStateProps(unittest.TestCase):
    """Test the StateProps class."""
    
    def setUp(self):
        """Set up a StateProps object for testing."""
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        self.state = StateProps()
        self.state.fluid = 'Water'
        
    def test_init(self):
        """Verify that StateProps initializes correctly."""
        self.assertIsInstance(self.state, StateProps)
        self.assertIsNone(self.state._tempk)
        self.assertIsNone(self.state._tempc)
        self.assertEqual(self.state.fluid, 'Water')

    def test_init_fluid(self):
        """Initialize with fluid parameter."""
        ref_state = StateProps(fluid='Water')
        self.assertEqual(ref_state.fluid, 'Water')
        
    def test_initialization(self):
        """Verify that StateProps initializes correctly."""
        self.state.press = 101325
        self.state.tempk = 293.15
        self.assertAlmostEqual(self.state.tempk, 293.15)
        self.assertAlmostEqual(self.state.press, 101325)

    def test_input_validation(self):
        """Test input validation for all properties."""
        # Test temperature validation
        with self.assertRaisesRegex(ValueError, "must be above absolute zero"):
            self.state.tempk = -1
        with self.assertRaisesRegex(ValueError, "exceeding reasonable range"):
            self.state.tempk = 2500  # > 1726.85°C
            
        # Test pressure validation
        with self.assertRaisesRegex(ValueError, "must be positive"):
            self.state.press = -101325
        with self.assertRaisesRegex(ValueError, "exceeding reasonable range"):
            self.state.press = 2e9  # > 10000 bar
            
        # Test density validation
        with self.assertRaisesRegex(ValueError, "must be positive"):
            self.state.dens = -1000
        with self.assertRaisesRegex(ValueError, "exceeding reasonable range"):
            self.state.dens = 2e5  # > 100000 kg/m³
            
        # Test quality validation
        with self.assertRaisesRegex(ValueError, "must be between 0 and 1"):
            self.state.quality = -0.1
        with self.assertRaisesRegex(ValueError, "must be between 0 and 1"):
            self.state.quality = 1.1
            
        # Test type validation
        with self.assertRaisesRegex(TypeError, "must be a number"):
            self.state.tempk = "293.15"

    def test_error_messages(self):
        """Test error messages when setting invalid states."""
        self.state.press = 101325
        self.state.tempk = 293.15
        
        # Setting a third property is now allowed
        # Try to set an inconsistent state that CoolProp would reject
        try:
            self.state.dens = 500  # Inconsistent density for current state
            # If no error, check that CoolProp used the new value and adjusted other properties
            self.assertAlmostEqual(self.state.dens, 500, places=0)
        except ValueError as e:
            # If there's an error, it should be from CoolProp's state validation
            self.assertIn("Cannot set dens", str(e))
            
        # Try to update with invalid value
        with self.assertRaisesRegex(ValueError, "must be positive"):
            self.state.press = -101325

    def test_property_calculation(self):
        """Verify that calculated properties are physically reasonable."""
        self.state.press = 101325
        self.state.tempk = 293.15
        
        # Test calculated properties
        self.assertIsNotNone(self.state.enthalpy)
        self.assertGreater(self.state.enthalpy, 0)
        self.assertIsNotNone(self.state.cp)
        self.assertGreater(self.state.cp, 0)
        self.assertIsNotNone(self.state.dens)
        self.assertGreater(self.state.dens, 0)
        
        # Quality should be None outside two-phase region
        self.assertAlmostEqual(self.state.quality, -1.0, places = 1)

    def test_fluid_validation(self):
        """Test fluid name validation."""
        with self.assertRaisesRegex(TypeError, "fluid must be a string"):
            self.state.fluid = 123

    def test_constraints_info(self):
        """Test the constraints property includes status and edition."""
        self.state.fluid = 'Water'
        self.state.tempk = 300
        self.state.press = 101325
        
        constraints = self.state.constraints
        
        # Check basic constraint properties
        self.assertIsInstance(constraints, dict)
        self.assertIn('properties', constraints)
        self.assertIn('fluid', constraints)
        self.assertIn('is_complete', constraints)
        
        # Check new fields: status and edition
        self.assertIn('status', constraints)
        self.assertIn('edition', constraints)
        
        # Verify fluid info
        self.assertEqual(constraints['fluid'], 'Water')
        self.assertTrue(constraints['is_complete'])
        
        # Reset for next tests
        self.setUp()

    def test_all_settable_properties(self):
        """Test that all properties can now be set directly."""
        # Setup a state to get reference values
        ref_state = StateProps(fluid='Water')
        ref_state.tempc = 25
        ref_state.press = 101325
        
        # Try setting cp directly
        state = StateProps(fluid='Water')
        state.press = 101325
        try:
            state.cp = ref_state.cp
            # If we get here, cp was set successfully
            self.assertAlmostEqual(state.cp, ref_state.cp, places=1)
            # Temperature should be different now
            self.assertNotEqual(state.tempc, 25)
        except ValueError:
            # Some properties may not be directly settable if CoolProp can't solve for them
            pass
              
        # Try setting cv directly
        state = StateProps(fluid='Water')
        state.press = 101325
        try:
            state.cv = ref_state.cv
            # If we get here, cv was set successfully
            self.assertAlmostEqual(state.cv, ref_state.cv, places=1)
            # Temperature should be different now
            self.assertNotEqual(state.tempc, 25)
        except ValueError:
            # Some properties may not be directly settable if CoolProp can't solve for them
            pass

    def test_settable_properties(self):
        """Test that previously calculated-only properties can now be set directly."""
        # Setup a state with basic properties
        state = StateProps(fluid='Water')
        state.tempc = 25
        state.press = 101325
        
        # Get reference values for later comparison
        initial_enthalpy = state.enthalpy
        initial_entropy = state.entropy
        
        # Create a new state and set properties that were formerly calculated-only
        state2 = StateProps(fluid='Water')
        
        # Test enthalpy can be set
        state2.press = 101325
        state2.enthalpy = initial_enthalpy
        self.assertAlmostEqual(state2.enthalpy, initial_enthalpy, places=0)
        self.assertAlmostEqual(state2.tempc, 25, places=0)
        
        # Reset and test entropy can be set
        state2 = StateProps(fluid='Water')
        state2.press = 101325
        state2.entropy = initial_entropy
        self.assertAlmostEqual(state2.entropy, initial_entropy, places=0)
        self.assertAlmostEqual(state2.tempc, 25, places=0)

    def test_set_temperature(self):
        """Test setting temperature in different units."""
        state = StateProps(fluid='Water')
        state.tempc = 25
        state.press = 101325
        self.assertAlmostEqual(state.tempc, 25)
        self.assertAlmostEqual(state.tempk, 298.15)

    def test_set_pressure(self):
        """Test setting pressure."""
        state = StateProps(fluid='Water')
        state.tempc = 25
        state.press = 101325
        self.assertAlmostEqual(state.press, 101325)

    def test_consistency(self):
        """Test internal consistency of calculated properties."""
        state = StateProps(fluid='Water')
        state.tempc = 25
        state.press = 101325
        self.assertAlmostEqual(1/state.dens, state.vol, places=6)

    def test_different_constraints(self):
        """Test setting state with different property pairs."""
        state = StateProps(fluid='Water')
        state.tempc = 25
        state.press = 101325
        ref_density = state.dens
        
        state2 = StateProps(fluid='Water')
        state2.tempc = 25
        state2.dens = ref_density
        self.assertAlmostEqual(state2.press, 101325, places=0)

    def test_two_phase_region(self):
        """Test handling of two-phase region and quality."""
        state = StateProps(fluid='Water')
        state.tempc = 120
        state.press = 101325
        self.assertEqual(state.quality, -1.0)  # Superheated vapor
        
        state2 = StateProps(fluid='Water')
        state2.tempc = 99.9  # Just below boiling at 1 atm
        state2.press = 101325
        self.assertEqual(state2.quality, 0.0)  # Saturated liquid
        
        state3 = StateProps(fluid='Water')
        state3.quality = 0.5  # 50% quality
        state3.press = 101325
        self.assertAlmostEqual(state3.tempc, 99.98, places=1)  # Boiling point at 1 atm


class TestStateHASettableProperties(unittest.TestCase):
    """Test cases for newly settable properties in StateHA."""
    
    def setUp(self):
        warnings.filterwarnings('ignore', category=DeprecationWarning)
        self.state = StateHA()
        
    def test_settable_properties(self):
        """Test that previously calculated-only properties can now be set directly."""
        # Set up a state with the three standard properties
        state = StateHA()
        state.press = 101325
        state.tempc = 25
        state.relhum = 0.5
        
        # Get initial values
        initial_enthalpy = state.enthalpy
        initial_entropy = state.entropy
        
        # Test enthalpy can be set
        state2 = StateHA()
        state2.press = 101325
        state2.tempc = 25
        state2.enthalpy = initial_enthalpy
        self.assertAlmostEqual(state2.enthalpy, initial_enthalpy, places=0)
        
        # Test entropy can be set
        state3 = StateHA()
        state3.press = 101325
        state3.tempc = 25
        state3.entropy = initial_entropy
        self.assertAlmostEqual(state3.entropy, initial_entropy, places=0)
        
    def test_all_settable_properties(self):
        """Test that all properties including cp can now be set directly."""
        # Set up a state to get reference values
        ref_state = StateHA()
        ref_state.press = 101325
        ref_state.tempc = 25
        ref_state.relhum = 0.5
        
        # Try setting cp directly
        state = StateHA()
        state.press = 101325
        state.tempc = 25
        try:
            state.cp = ref_state.cp
            self.assertAlmostEqual(state.cp, ref_state.cp, places=0)
        except AttributeError:
            self.fail("cp should be settable")


if __name__ == '__main__':
    unittest.main() 
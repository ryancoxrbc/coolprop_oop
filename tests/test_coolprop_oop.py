"""
Test suite for CoolProp OOP wrapper classes.

This module contains comprehensive tests for both StateHA (Humid Air) and 
StatePROPS (Pure Fluid) property calculators.

Tests include:
- Basic initialization and property calculation
- Under/over constraining behavior
- Invalid value handling
- Property updates and dependencies
- Extreme condition handling
"""

from coolprop_oop import StateHA, StatePROPS
import unittest


class TestStateHA(unittest.TestCase):
    """Test cases for humid air properties calculator."""

    def test_initialization(self):
        """Verify that StateHA initializes correctly with properties."""
        state = StateHA(['P', 101325, 'T', 293.15, 'R', 0.5])
        self.assertAlmostEqual(state.relhum, 0.5, places=2)
        self.assertAlmostEqual(state.tempk, 293.15, places=2)
        self.assertAlmostEqual(state.press, 101325, places=0)

    def test_property_calculation(self):
        """Verify that calculated properties are physically reasonable."""
        state = StateHA(['P', 101325, 'T', 293.15, 'R', 0.5])
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

    def test_overconstraining(self):
        """Verify that overconstraining raises appropriate errors."""
        state = StateHA()
        state.tempk = 293.15
        state.press = 101325
        state.relhum = 0.5
        
        # Try to set a fourth property
        with self.assertRaises(ValueError):
            state.wetbulb = 290
        
        # Verify original constraints remain unchanged
        self.assertEqual(len(state._constraints_set), 3)
        self.assertAlmostEqual(state.tempk, 293.15)

    def test_invalid_values(self):
        """Verify handling of invalid property values."""
        state = StateHA()
        
        # Test negative pressure
        with self.assertRaises(ValueError):
            state.press = -101325
            
        # Test relative humidity > 1
        state.tempk = 293.15
        state.press = 101325
        with self.assertRaises(ValueError):
            state.relhum = 1.5
            
        # Test temperature below freezing
        state = StateHA()
        with self.assertRaises(ValueError):
            state.tempk = 263.15  # -10°C

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

    def test_extreme_conditions(self):
        """Verify behavior at extreme but valid conditions."""
        # Test high temperature condition
        state = StateHA()
        state.tempk = 323.15  # 50°C
        state.press = 101325
        state.relhum = 0.8
        self.assertGreater(state.humrat, 0.05)  # High humidity ratio expected
        
        # Test low humidity condition
        state = StateHA()
        state.tempk = 293.15
        state.press = 101325
        state.relhum = 0.1
        self.assertLess(state.humrat, 0.002)  # Low humidity ratio expected


class TestStatePROPS(unittest.TestCase):
    """Test cases for pure fluid properties calculator."""

    def test_initialization(self):
        """Verify that StatePROPS initializes correctly."""
        state = StatePROPS(['P', 101325, 'T', 293.15])
        self.assertAlmostEqual(state.tempk, 293.15)
        self.assertAlmostEqual(state.press, 101325)

    def test_property_calculation(self):
        """Verify that calculated properties are physically reasonable."""
        state = StatePROPS(['P', 101325, 'T', 293.15])
        self.assertGreater(state.enthalpy, 0)
        self.assertGreater(state.cp, 0)
        self.assertGreater(state.density, 0)


if __name__ == '__main__':
    unittest.main() 
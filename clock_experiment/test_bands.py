import unittest
import numpy as np
from .run_bands import reconstruct

class TestBands(unittest.TestCase):
    def test_energy_identity(self):
        power=np.random.default_rng(4).uniform(size=(10,1008))
        bands=np.sqrt(power.reshape(10,4,252).sum(2))
        np.testing.assert_allclose(reconstruct(bands),np.sqrt(power.sum(1)))
    def test_negative_forecast_not_negative_energy(self):
        np.testing.assert_array_equal(reconstruct([[-3,4,0,0]]),[4])
    def test_invalid(self):
        with self.assertRaises(ValueError): reconstruct([[np.nan]])

if __name__=='__main__': unittest.main()

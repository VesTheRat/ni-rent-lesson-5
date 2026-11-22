import pytest

from src.models import Apartment
from src.manager import Manager
from src.models import Parameters


def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs('invalid-key', 2025, 1) is None
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0

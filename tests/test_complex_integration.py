import pytest

from src.models import Apartment
from src.manager import Manager
from src.models import Parameters
from src.models import Bill
from src.models import ApartmentSettlement
from src.models import TenantSettlement


def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)
    assert manager.get_apartment_costs('invalid-key', 2025, 1) is None
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0.0
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    costs = manager.get_apartment_costs('apartment-1', 2024, 1)
    assert costs is None

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0

def test_create_apartment_settlement():
    parameters = Parameters()
    manager = Manager(parameters)

    settlement_with_bills = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    assert isinstance(settlement_with_bills, ApartmentSettlement)
    assert settlement_with_bills.apartment == 'apart-polanka'
    assert settlement_with_bills.year == 2025
    assert settlement_with_bills.month == 1
    assert settlement_with_bills.total_rent_pln == 0.0
    assert settlement_with_bills.total_bills_pln == 910.0
    assert settlement_with_bills.total_due_pln == 910.0

    settlement_without_bills = manager.create_apartment_settlement('apart-polanka', 2025, 2)
    assert isinstance(settlement_without_bills, ApartmentSettlement)
    assert settlement_without_bills.apartment == 'apart-polanka'
    assert settlement_without_bills.year == 2025
    assert settlement_without_bills.month == 2
    assert settlement_without_bills.total_rent_pln == 0.0
    assert settlement_without_bills.total_bills_pln == 0.0
    assert settlement_without_bills.total_due_pln == 0.0


def test_create_tenant_settlements():
    parameters = Parameters()
    manager = Manager(parameters)

    apt_settlement_multi = manager.create_apartment_settlement('apart-polanka', 2025, 1)
    multi_tenants = [k for k, t in manager.tenants.items() if t.apartment == 'apart-polanka']
    assert len(multi_tenants) >= 2

    settlements_multi = manager.create_tenant_settlements(apt_settlement_multi)
    assert len(settlements_multi) == len(multi_tenants)
    assert all(isinstance(s, TenantSettlement) for s in settlements_multi)
    expected_share_multi = apt_settlement_multi.total_bills_pln / len(multi_tenants)
    for s in settlements_multi:
        assert s.bills_pln == expected_share_multi
        assert s.month == 1
        assert s.year == 2025

    apt_keys = list(manager.apartments.keys())
    single_apt_key = apt_keys[1] if len(apt_keys) > 1 else apt_keys[0]
    first_tenant = next(iter(manager.tenants.values()))
    first_tenant.apartment = single_apt_key
    for other_key, other_tenant in list(manager.tenants.items())[1:]:
        if other_tenant.apartment == single_apt_key:
            other_tenant.apartment = 'other-apt'

    apt_settlement_single = manager.create_apartment_settlement(single_apt_key, 2025, 1)
    settlements_single = manager.create_tenant_settlements(apt_settlement_single)
    assert len(settlements_single) == 1
    assert settlements_single[0].bills_pln == apt_settlement_single.total_bills_pln
    assert settlements_single[0].total_due_pln == apt_settlement_single.total_due_pln

    empty_apt_key = apt_keys[-1]
    for tenant in manager.tenants.values():
        if tenant.apartment == empty_apt_key:
            tenant.apartment = 'other-apt'

    apt_settlement_empty = manager.create_apartment_settlement(empty_apt_key, 2025, 1)
    settlements_empty = manager.create_tenant_settlements(apt_settlement_empty)
    assert settlements_empty == []

"""
Unit tests for InventoryService.

All repository interactions are replaced with MagicMock — no database required.
"""
import pytest
from unittest.mock import MagicMock, call

from medistock.domain.models.medication import Medication
from medistock.domain.models.stock_item import StockItem, LOW_STOCK_THRESHOLD
from medistock.domain.services import InventoryService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def medication():
    return Medication(name="Aspirin", description="Pain reliever", unit="tablet")


@pytest.fixture
def mock_repo():
    return MagicMock()


@pytest.fixture
def service(mock_repo):
    return InventoryService(mock_repo)


# ---------------------------------------------------------------------------
# add_stock
# ---------------------------------------------------------------------------

def test_add_stock_creates_new_entry_when_none_exists(service, mock_repo, medication):
    mock_repo.get_by_medication.return_value = None

    item = service.add_stock(medication, amount=100, location="Shelf A")

    assert item.quantity == 100
    assert item.location == "Shelf A"
    assert item.medication is medication
    mock_repo.save.assert_called_once()


def test_add_stock_increments_existing_quantity(service, mock_repo, medication):
    existing = StockItem(medication=medication, quantity=50, location="Shelf A")
    mock_repo.get_by_medication.return_value = existing

    item = service.add_stock(medication, amount=25, location="Shelf A")

    assert item.quantity == 75
    mock_repo.save.assert_called_once_with(item)


def test_add_stock_zero_amount_raises(service, mock_repo, medication):
    mock_repo.get_by_medication.return_value = None

    with pytest.raises(ValueError, match="greater than zero"):
        service.add_stock(medication, amount=0, location="Shelf A")


def test_add_stock_negative_amount_raises(service, mock_repo, medication):
    mock_repo.get_by_medication.return_value = None

    with pytest.raises(ValueError, match="greater than zero"):
        service.add_stock(medication, amount=-5, location="Shelf A")


# ---------------------------------------------------------------------------
# dispense
# ---------------------------------------------------------------------------

def test_dispense_reduces_quantity(service, mock_repo, medication):
    existing = StockItem(medication=medication, quantity=50, location="Shelf A")
    mock_repo.get_by_medication.return_value = existing

    item = service.dispense(medication, amount=10)

    assert item.quantity == 40
    mock_repo.save.assert_called_once_with(item)


def test_dispense_exact_quantity_empties_stock(service, mock_repo, medication):
    existing = StockItem(medication=medication, quantity=10, location="Shelf A")
    mock_repo.get_by_medication.return_value = existing

    item = service.dispense(medication, amount=10)

    assert item.quantity == 0
    assert item.is_out_of_stock


def test_dispense_insufficient_stock_raises(service, mock_repo, medication):
    existing = StockItem(medication=medication, quantity=5, location="Shelf A")
    mock_repo.get_by_medication.return_value = existing

    with pytest.raises(ValueError, match="Insufficient stock"):
        service.dispense(medication, amount=10)


def test_dispense_no_stock_entry_raises(service, mock_repo, medication):
    mock_repo.get_by_medication.return_value = None

    with pytest.raises(ValueError, match="No stock entry"):
        service.dispense(medication, amount=1)


def test_dispense_zero_amount_raises(service, mock_repo, medication):
    existing = StockItem(medication=medication, quantity=10, location="Shelf A")
    mock_repo.get_by_medication.return_value = existing

    with pytest.raises(ValueError, match="greater than zero"):
        service.dispense(medication, amount=0)


# ---------------------------------------------------------------------------
# get_stock
# ---------------------------------------------------------------------------

def test_get_stock_returns_item(service, mock_repo, medication):
    item = StockItem(medication=medication, quantity=20, location="Shelf A")
    mock_repo.get_by_medication.return_value = item

    result = service.get_stock(medication)

    assert result is item
    mock_repo.get_by_medication.assert_called_once_with(medication.id)


def test_get_stock_returns_none_when_not_found(service, mock_repo, medication):
    mock_repo.get_by_medication.return_value = None

    result = service.get_stock(medication)

    assert result is None


# ---------------------------------------------------------------------------
# list_all_stock and alerts
# ---------------------------------------------------------------------------

def test_list_all_stock(service, mock_repo, medication):
    items = [StockItem(medication=medication, quantity=50, location="Shelf A")]
    mock_repo.list_all.return_value = items

    result = service.list_all_stock()

    assert result == items
    mock_repo.list_all.assert_called_once()


def test_get_low_stock_alerts_returns_low_items(service, mock_repo, medication):
    low_item = StockItem(medication=medication, quantity=5, location="Shelf A")
    mock_repo.list_low_stock.return_value = [low_item]

    alerts = service.get_low_stock_alerts()

    assert len(alerts) == 1
    assert alerts[0].is_low
    mock_repo.list_low_stock.assert_called_once()


def test_get_low_stock_alerts_empty_when_none_low(service, mock_repo):
    mock_repo.list_low_stock.return_value = []

    alerts = service.get_low_stock_alerts()

    assert alerts == []


# ---------------------------------------------------------------------------
# is_out_of_stock
# ---------------------------------------------------------------------------

def test_is_out_of_stock_true_when_quantity_zero(service, mock_repo, medication):
    item = StockItem(medication=medication, quantity=0, location="Shelf A")
    mock_repo.get_by_medication.return_value = item

    assert service.is_out_of_stock(medication) is True


def test_is_out_of_stock_false_when_quantity_positive(service, mock_repo, medication):
    item = StockItem(medication=medication, quantity=5, location="Shelf A")
    mock_repo.get_by_medication.return_value = item

    assert service.is_out_of_stock(medication) is False


def test_is_out_of_stock_true_when_no_entry(service, mock_repo, medication):
    mock_repo.get_by_medication.return_value = None

    assert service.is_out_of_stock(medication) is True


# ---------------------------------------------------------------------------
# Low stock threshold boundary
# ---------------------------------------------------------------------------

def test_item_is_low_at_threshold(medication):
    item = StockItem(medication=medication, quantity=LOW_STOCK_THRESHOLD, location="X")
    assert item.is_low is True


def test_item_is_not_low_above_threshold(medication):
    item = StockItem(medication=medication, quantity=LOW_STOCK_THRESHOLD + 1, location="X")
    assert item.is_low is False

"""
Comprehensive test suite for ByteBites models.

Tests cover:
- Core functionality (CRUD operations, filtering, calculations)
- Boundary conditions (empty collections, zero/max values)
- Type safety and validation (invalid inputs)
- Edge cases (duplicates, non-existent items, etc.)
- Integration scenarios (full order lifecycle)

Run with: python -m pytest test_bytebites.py -v
"""

import pytest
from datetime import datetime
from models import Item, Menu, Transaction, Customer, Category, TransactionStatus


# =============================================================================
# ITEM TESTS
# =============================================================================

class TestItem:
    """Test suite for Item class."""

    def test_item_creation_basic(self):
        """Test creating an item with required attributes."""
        item = Item("Burger", 12.99, Category.BURGERS)
        assert item.name == "Burger"
        assert item.price == 12.99
        assert item.category == Category.BURGERS
        assert item.is_available is True
        assert item.popularity_rating == 0.0

    def test_item_auto_increment_id(self):
        """Test that item IDs are auto-incremented."""
        # Reset counter for deterministic testing
        Item._id_counter = 0

        item1 = Item("Item1", 5.0, Category.BURGERS)
        item2 = Item("Item2", 10.0, Category.DRINKS)
        item3 = Item("Item3", 7.0, Category.DESSERTS)

        assert item1.item_id == 1
        assert item2.item_id == 2
        assert item3.item_id == 3
        assert item2.item_id > item1.item_id

    def test_item_with_all_attributes(self):
        """Test creating an item with all optional attributes."""
        item = Item(
            "Spicy Burger",
            15.99,
            Category.BURGERS,
            popularity_rating=4.5,
            is_available=True
        )
        assert item.name == "Spicy Burger"
        assert item.price == 15.99
        assert item.popularity_rating == 4.5
        assert item.is_available is True

    def test_item_popularity_rating_bounds_valid(self):
        """Test that valid popularity ratings (0.0-5.0) are accepted."""
        item1 = Item("Item1", 5.0, Category.BURGERS, popularity_rating=0.0)
        assert item1.popularity_rating == 0.0

        item2 = Item("Item2", 5.0, Category.BURGERS, popularity_rating=2.5)
        assert item2.popularity_rating == 2.5

        item3 = Item("Item3", 5.0, Category.BURGERS, popularity_rating=5.0)
        assert item3.popularity_rating == 5.0

    def test_item_popularity_rating_bounds_invalid_too_high(self):
        """Test that rating > 5.0 is rejected on construction."""
        with pytest.raises(ValueError, match="Popularity rating must be between"):
            Item("Item", 5.0, Category.BURGERS, popularity_rating=5.1)

    def test_item_popularity_rating_bounds_invalid_too_low(self):
        """Test that rating < 0.0 is rejected on construction."""
        with pytest.raises(ValueError, match="Popularity rating must be between"):
            Item("Item", 5.0, Category.BURGERS, popularity_rating=-0.1)

    def test_update_rating_valid(self):
        """Test updating a rating with valid values."""
        item = Item("Item", 5.0, Category.BURGERS, popularity_rating=3.0)

        item.update_rating(4.5)
        assert item.popularity_rating == 4.5

        item.update_rating(0.0)
        assert item.popularity_rating == 0.0

        item.update_rating(5.0)
        assert item.popularity_rating == 5.0

    def test_update_rating_invalid_too_high(self):
        """Test that update_rating rejects values > 5.0."""
        item = Item("Item", 5.0, Category.BURGERS)
        with pytest.raises(ValueError, match="Rating must be between"):
            item.update_rating(5.1)

    def test_update_rating_invalid_too_low(self):
        """Test that update_rating rejects values < 0.0."""
        item = Item("Item", 5.0, Category.BURGERS)
        with pytest.raises(ValueError, match="Rating must be between"):
            item.update_rating(-0.01)

    def test_get_details_format(self):
        """Test that get_details returns properly formatted string."""
        item = Item("Spicy Burger", 12.99, Category.BURGERS, popularity_rating=4.5)
        details = item.get_details()

        # Should contain all key information
        assert item.name in details
        assert "12.99" in details
        assert "Burgers" in details
        assert "4.5" in details
        assert "[" in details and "]" in details  # ID in brackets
        assert "★" in details  # Star rating symbol

    def test_get_details_formatting_precision(self):
        """Test that get_details formats price and rating to correct precision."""
        item = Item("Item", 9.995, Category.BURGERS, popularity_rating=4.444)
        details = item.get_details()

        # Price should be formatted to 2 decimals
        assert "10.00" in details or "9.99" in details
        # Rating should be formatted to 1 decimal
        assert "4.4" in details

    def test_item_availability_flag(self):
        """Test that is_available flag can be toggled."""
        item = Item("Item", 5.0, Category.BURGERS, is_available=True)
        assert item.is_available is True

        item.is_available = False
        assert item.is_available is False

    def test_item_repr(self):
        """Test item string representation."""
        item = Item("Burger", 12.99, Category.BURGERS)
        repr_str = repr(item)
        assert "Item" in repr_str
        assert "Burger" in repr_str
        assert "12.99" in repr_str


# =============================================================================
# MENU TESTS
# =============================================================================

class TestMenu:
    """Test suite for Menu class."""

    def test_menu_creation_empty(self):
        """Test creating an empty menu."""
        menu = Menu()
        assert len(menu) == 0
        assert menu.get_all_items() == []

    def test_menu_add_item(self):
        """Test adding items to a menu."""
        menu = Menu()
        item1 = Item("Item1", 5.0, Category.BURGERS)
        item2 = Item("Item2", 10.0, Category.DRINKS)

        menu.add_item(item1)
        assert len(menu) == 1

        menu.add_item(item2)
        assert len(menu) == 2

    def test_menu_add_multiple_same_item(self):
        """Test adding the same item multiple times."""
        menu = Menu()
        item = Item("Item", 5.0, Category.BURGERS)

        menu.add_item(item)
        menu.add_item(item)  # Add same item twice

        # Menu stores both references (doesn't deduplicate)
        items = menu.get_all_items()
        assert len(items) == 2

    def test_menu_remove_item(self):
        """Test removing items from a menu."""
        menu = Menu()
        item1 = Item("Item1", 5.0, Category.BURGERS)
        item2 = Item("Item2", 10.0, Category.DRINKS)

        menu.add_item(item1)
        menu.add_item(item2)
        assert len(menu) == 2

        menu.remove_item(item1)
        assert len(menu) == 1
        assert item1 not in menu.get_all_items()

    def test_menu_remove_nonexistent_item(self):
        """Test that removing a non-existent item raises error."""
        menu = Menu()
        item1 = Item("Item1", 5.0, Category.BURGERS)
        item2 = Item("Item2", 10.0, Category.DRINKS)

        menu.add_item(item1)

        with pytest.raises(ValueError, match="not found in menu"):
            menu.remove_item(item2)

    def test_menu_remove_from_empty_menu(self):
        """Test that removing from an empty menu raises error."""
        menu = Menu()
        item = Item("Item", 5.0, Category.BURGERS)

        with pytest.raises(ValueError):
            menu.remove_item(item)

    def test_menu_filter_by_category_single_match(self):
        """Test filtering by category with single matching item."""
        menu = Menu()
        burger = Item("Burger", 12.99, Category.BURGERS)
        soda = Item("Soda", 3.49, Category.DRINKS)

        menu.add_item(burger)
        menu.add_item(soda)

        burgers = menu.filter_by_category(Category.BURGERS)
        assert len(burgers) == 1
        assert burgers[0].name == "Burger"

    def test_menu_filter_by_category_multiple_matches(self):
        """Test filtering by category with multiple matching items."""
        menu = Menu()
        burger1 = Item("Burger1", 12.99, Category.BURGERS)
        burger2 = Item("Burger2", 14.99, Category.BURGERS)
        soda = Item("Soda", 3.49, Category.DRINKS)

        menu.add_item(burger1)
        menu.add_item(burger2)
        menu.add_item(soda)

        burgers = menu.filter_by_category(Category.BURGERS)
        assert len(burgers) == 2
        assert all(item.category == Category.BURGERS for item in burgers)

    def test_menu_filter_by_category_no_matches(self):
        """Test filtering by category with no matches."""
        menu = Menu()
        burger = Item("Burger", 12.99, Category.BURGERS)
        soda = Item("Soda", 3.49, Category.DRINKS)

        menu.add_item(burger)
        menu.add_item(soda)

        desserts = menu.filter_by_category(Category.DESSERTS)
        assert len(desserts) == 0

    def test_menu_filter_excludes_unavailable_items(self):
        """Test that filter_by_category excludes unavailable items."""
        menu = Menu()
        burger1 = Item("Burger1", 12.99, Category.BURGERS, is_available=True)
        burger2 = Item("Burger2", 14.99, Category.BURGERS, is_available=False)

        menu.add_item(burger1)
        menu.add_item(burger2)

        burgers = menu.filter_by_category(Category.BURGERS)
        assert len(burgers) == 1
        assert burgers[0].name == "Burger1"

    def test_menu_filter_empty_menu(self):
        """Test filtering on an empty menu."""
        menu = Menu()
        burgers = menu.filter_by_category(Category.BURGERS)
        assert burgers == []

    def test_menu_get_all_items_returns_copy(self):
        """Test that get_all_items returns a copy, not a reference."""
        menu = Menu()
        item = Item("Item", 5.0, Category.BURGERS)
        menu.add_item(item)

        items_list = menu.get_all_items()
        items_list.append(Item("Fake", 1.0, Category.DRINKS))

        # Menu should still have 1 item
        assert len(menu.get_all_items()) == 1

    def test_menu_repr(self):
        """Test menu string representation."""
        menu = Menu()
        repr_str = repr(menu)
        assert "Menu" in repr_str
        assert "items=0" in repr_str

        item = Item("Item", 5.0, Category.BURGERS)
        menu.add_item(item)
        repr_str = repr(menu)
        assert "items=1" in repr_str


# =============================================================================
# TRANSACTION TESTS
# =============================================================================

class TestTransaction:
    """Test suite for Transaction class."""

    def test_transaction_creation(self):
        """Test creating a transaction for a customer."""
        # Reset counter for deterministic testing
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        assert tx.transaction_id == 1
        assert tx.customer is customer
        assert tx.status == TransactionStatus.PENDING
        assert isinstance(tx.timestamp, datetime)
        assert len(tx.get_items()) == 0

    def test_transaction_auto_increment_id(self):
        """Test that transaction IDs are auto-incremented."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx1 = Transaction(customer)
        tx2 = Transaction(customer)
        tx3 = Transaction(customer)

        assert tx1.transaction_id == 1
        assert tx2.transaction_id == 2
        assert tx3.transaction_id == 3

    def test_transaction_add_item_single(self):
        """Test adding a single item to a transaction."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        tx.add_item(item)
        items = tx.get_items()

        assert len(items) == 1
        assert items[item] == 1

    def test_transaction_add_item_with_quantity(self):
        """Test adding items with specific quantities."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        tx.add_item(item, quantity=3)
        items = tx.get_items()

        assert items[item] == 3

    def test_transaction_add_same_item_multiple_times(self):
        """Test that adding the same item multiple times increases quantity."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        tx.add_item(item, quantity=2)
        tx.add_item(item, quantity=3)

        items = tx.get_items()
        assert items[item] == 5  # 2 + 3

    def test_transaction_add_item_invalid_quantity_zero(self):
        """Test that quantity of 0 is rejected."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            tx.add_item(item, quantity=0)

    def test_transaction_add_item_invalid_quantity_negative(self):
        """Test that negative quantities are rejected."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        with pytest.raises(ValueError, match="Quantity must be at least 1"):
            tx.add_item(item, quantity=-5)

    def test_transaction_compute_total_single_item(self):
        """Test total calculation with a single item."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        tx.add_item(item, quantity=1)
        assert abs(tx.compute_total() - 12.99) < 0.001

    def test_transaction_compute_total_multiple_quantities(self):
        """Test total calculation with multiple quantities of same item."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Burger", 12.99, Category.BURGERS)

        tx.add_item(item, quantity=3)
        expected = 12.99 * 3
        assert abs(tx.compute_total() - expected) < 0.001

    def test_transaction_compute_total_multiple_items(self):
        """Test total calculation with multiple different items."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        burger = Item("Burger", 12.99, Category.BURGERS)
        soda = Item("Soda", 3.49, Category.DRINKS)
        fries = Item("Fries", 4.99, Category.SIDES)

        tx.add_item(burger, quantity=2)
        tx.add_item(soda, quantity=1)
        tx.add_item(fries, quantity=2)

        expected = (2 * 12.99) + (1 * 3.49) + (2 * 4.99)
        assert abs(tx.compute_total() - expected) < 0.001

    def test_transaction_compute_total_empty(self):
        """Test that total of empty transaction is 0."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        assert tx.compute_total() == 0.0

    def test_transaction_compute_total_precision(self):
        """Test that total calculation handles floating point precision."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        # Items with prices that might cause floating point errors
        item1 = Item("Item1", 10.10, Category.BURGERS)
        item2 = Item("Item2", 20.20, Category.DRINKS)
        item3 = Item("Item3", 30.30, Category.DESSERTS)

        tx.add_item(item1, quantity=1)
        tx.add_item(item2, quantity=1)
        tx.add_item(item3, quantity=1)

        # Should be 60.60
        assert abs(tx.compute_total() - 60.60) < 0.001

    def test_transaction_remove_item(self):
        """Test removing an item from a transaction."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        item1 = Item("Burger", 12.99, Category.BURGERS)
        item2 = Item("Soda", 3.49, Category.DRINKS)

        tx.add_item(item1)
        tx.add_item(item2)
        assert len(tx.get_items()) == 2

        tx.remove_item(item1)
        assert len(tx.get_items()) == 1
        assert item2 in tx.get_items()
        assert item1 not in tx.get_items()

    def test_transaction_remove_nonexistent_item(self):
        """Test that removing a non-existent item is safe (no-op)."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item1 = Item("Item1", 5.0, Category.BURGERS)
        item2 = Item("Item2", 10.0, Category.DRINKS)

        tx.add_item(item1)
        tx.remove_item(item2)  # Safe, no exception

        assert len(tx.get_items()) == 1

    def test_transaction_mark_completed(self):
        """Test marking a transaction as completed."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        assert tx.status == TransactionStatus.PENDING
        tx.mark_completed()
        assert tx.status == TransactionStatus.COMPLETED

    def test_transaction_mark_cancelled(self):
        """Test marking a transaction as cancelled."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        assert tx.status == TransactionStatus.PENDING
        tx.mark_cancelled()
        assert tx.status == TransactionStatus.CANCELLED

    def test_transaction_get_items_returns_copy(self):
        """Test that get_items returns a copy, not a reference."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Item", 5.0, Category.BURGERS)

        tx.add_item(item, quantity=1)
        items_dict = tx.get_items()
        items_dict[item] = 999  # Modify the copy

        # Original should be unchanged
        assert tx.get_items()[item] == 1

    def test_transaction_repr(self):
        """Test transaction string representation."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        item = Item("Burger", 12.99, Category.BURGERS)
        tx.add_item(item)

        repr_str = repr(tx)
        assert "Transaction" in repr_str
        assert "Alice" in repr_str
        assert "items=1" in repr_str


# =============================================================================
# CUSTOMER TESTS
# =============================================================================

class TestCustomer:
    """Test suite for Customer class."""

    def test_customer_creation(self):
        """Test creating a customer."""
        Customer._id_counter = 0

        customer = Customer("Alice", "alice@example.com")

        assert customer.customer_id == 1
        assert customer.name == "Alice"
        assert customer.email == "alice@example.com"
        assert customer.is_verified is False
        assert len(customer.get_purchase_history()) == 0

    def test_customer_auto_increment_id(self):
        """Test that customer IDs are auto-incremented."""
        Customer._id_counter = 0

        customer1 = Customer("Alice", "alice@example.com")
        customer2 = Customer("Bob", "bob@example.com")
        customer3 = Customer("Charlie", "charlie@example.com")

        assert customer1.customer_id == 1
        assert customer2.customer_id == 2
        assert customer3.customer_id == 3

    def test_verify_user_valid_email(self):
        """Test verifying a customer with a valid email."""
        Customer._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        result = customer.verify_user()

        assert result is True
        assert customer.is_verified is True

    def test_verify_user_valid_email_various_formats(self):
        """Test verification with various valid email formats."""
        Customer._id_counter = 0

        valid_emails = [
            "user@domain.com",
            "john.doe@company.co.uk",
            "test+tag@example.org",
            "123@456.net",
        ]

        for i, email in enumerate(valid_emails):
            customer = Customer(f"User{i}", email)
            result = customer.verify_user()
            assert result is True, f"Should verify: {email}"
            assert customer.is_verified is True

    def test_verify_user_invalid_email_no_at_symbol(self):
        """Test that email without @ symbol fails verification."""
        Customer._id_counter = 0

        customer = Customer("Alice", "aliceexample.com")
        result = customer.verify_user()

        assert result is False
        assert customer.is_verified is False

    def test_verify_user_invalid_email_no_domain_extension(self):
        """Test that email without domain extension (no .) fails."""
        Customer._id_counter = 0

        customer = Customer("Alice", "alice@nodomain")
        result = customer.verify_user()

        assert result is False
        assert customer.is_verified is False

    def test_verify_user_invalid_email_no_domain_part(self):
        """Test that email without domain fails."""
        Customer._id_counter = 0

        customer = Customer("Alice", "alice@")
        result = customer.verify_user()

        assert result is False
        assert customer.is_verified is False

    def test_verify_user_invalid_email_empty_string(self):
        """Test that empty email fails verification."""
        Customer._id_counter = 0

        customer = Customer("Alice", "")
        result = customer.verify_user()

        assert result is False
        assert customer.is_verified is False

    def test_add_transaction(self):
        """Test adding a transaction to customer history."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        customer.add_transaction(tx)
        history = customer.get_purchase_history()

        assert len(history) == 1
        assert history[0] is tx

    def test_add_multiple_transactions(self):
        """Test adding multiple transactions to history."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx1 = Transaction(customer)
        tx2 = Transaction(customer)
        tx3 = Transaction(customer)

        customer.add_transaction(tx1)
        customer.add_transaction(tx2)
        customer.add_transaction(tx3)

        history = customer.get_purchase_history()
        assert len(history) == 3
        assert history[0] is tx1
        assert history[1] is tx2
        assert history[2] is tx3

    def test_get_purchase_history_returns_copy(self):
        """Test that get_purchase_history returns a copy, not a reference."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        customer.add_transaction(tx)

        history = customer.get_purchase_history()
        history.append(None)  # Modify the copy

        # Original should still have 1 item
        assert len(customer.get_purchase_history()) == 1

    def test_customer_repr(self):
        """Test customer string representation."""
        Customer._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        repr_str = repr(customer)

        assert "Customer" in repr_str
        assert "Alice" in repr_str
        assert "verified=False" in repr_str

        customer.verify_user()
        repr_str = repr(customer)
        assert "verified=True" in repr_str


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestIntegration:
    """Integration tests for complete workflows."""

    def test_full_order_workflow(self):
        """Test complete workflow: menu -> customer -> transaction -> history."""
        Customer._id_counter = 0
        Item._id_counter = 0
        Transaction._id_counter = 0

        # Step 1: Create items and menu
        menu = Menu()
        burger = Item("Spicy Burger", 12.99, Category.BURGERS, popularity_rating=4.5)
        soda = Item("Large Soda", 3.49, Category.DRINKS, popularity_rating=3.8)
        cake = Item("Lava Cake", 6.99, Category.DESSERTS, popularity_rating=4.9)

        menu.add_item(burger)
        menu.add_item(soda)
        menu.add_item(cake)

        # Step 2: Create and verify customer
        customer = Customer("Alice", "alice@example.com")
        assert customer.verify_user() is True

        # Step 3: Create transaction and add items
        tx = Transaction(customer)
        tx.add_item(burger, quantity=2)
        tx.add_item(soda, quantity=1)

        # Step 4: Verify total calculation
        expected_total = (2 * 12.99) + (1 * 3.49)
        assert abs(tx.compute_total() - expected_total) < 0.001

        # Step 5: Record transaction in history
        customer.add_transaction(tx)
        history = customer.get_purchase_history()
        assert len(history) == 1
        assert history[0].customer is customer

    def test_multiple_customers_multiple_transactions(self):
        """Test system with multiple customers and transactions."""
        Customer._id_counter = 0
        Item._id_counter = 0
        Transaction._id_counter = 0

        # Create items
        burger = Item("Burger", 12.99, Category.BURGERS)
        soda = Item("Soda", 3.49, Category.DRINKS)

        # Create customers
        alice = Customer("Alice", "alice@example.com")
        bob = Customer("Bob", "bob@example.com")

        alice.verify_user()
        bob.verify_user()

        # Create transactions
        tx1 = Transaction(alice)
        tx1.add_item(burger, quantity=1)
        alice.add_transaction(tx1)

        tx2 = Transaction(bob)
        tx2.add_item(soda, quantity=2)
        bob.add_transaction(tx2)

        tx3 = Transaction(alice)
        tx3.add_item(burger, quantity=3)
        tx3.add_item(soda, quantity=1)
        alice.add_transaction(tx3)

        # Verify histories
        assert len(alice.get_purchase_history()) == 2
        assert len(bob.get_purchase_history()) == 1

        # Each transaction should reference correct customer
        assert tx1.customer is alice
        assert tx2.customer is bob
        assert tx3.customer is alice

    def test_category_filtering_across_large_menu(self):
        """Test category filtering with many items."""
        menu = Menu()
        Item._id_counter = 0

        # Add items across categories
        for i in range(5):
            menu.add_item(Item(f"Burger{i}", 10.0 + i, Category.BURGERS))
            menu.add_item(Item(f"Drink{i}", 3.0 + i, Category.DRINKS))
            menu.add_item(Item(f"Dessert{i}", 5.0 + i, Category.DESSERTS))

        # Filter and verify counts
        burgers = menu.filter_by_category(Category.BURGERS)
        drinks = menu.filter_by_category(Category.DRINKS)
        desserts = menu.filter_by_category(Category.DESSERTS)

        assert len(burgers) == 5
        assert len(drinks) == 5
        assert len(desserts) == 5

    def test_transaction_with_all_categories(self):
        """Test transaction containing items from multiple categories."""
        Customer._id_counter = 0
        Item._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        burger = Item("Burger", 12.99, Category.BURGERS)
        soda = Item("Soda", 3.49, Category.DRINKS)
        cake = Item("Cake", 6.99, Category.DESSERTS)
        fries = Item("Fries", 4.99, Category.SIDES)

        tx.add_item(burger, quantity=1)
        tx.add_item(soda, quantity=1)
        tx.add_item(cake, quantity=1)
        tx.add_item(fries, quantity=1)

        expected_total = 12.99 + 3.49 + 6.99 + 4.99
        assert abs(tx.compute_total() - expected_total) < 0.001

    def test_status_tracking_through_lifecycle(self):
        """Test transaction status changes through lifecycle."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        # Initially pending
        assert tx.status == TransactionStatus.PENDING

        # Add items
        item = Item("Burger", 12.99, Category.BURGERS)
        tx.add_item(item)

        # Mark completed
        tx.mark_completed()
        assert tx.status == TransactionStatus.COMPLETED

        # Can still modify (no enforcement of read-only after completion)
        tx.mark_cancelled()
        assert tx.status == TransactionStatus.CANCELLED


# =============================================================================
# EDGE CASE & BOUNDARY TESTS
# =============================================================================

class TestEdgeCasesAndBoundaries:
    """Test edge cases and boundary conditions."""

    def test_item_with_zero_price(self):
        """Test creating an item with zero price."""
        item = Item("Free Item", 0.0, Category.BURGERS)
        assert item.price == 0.0

    def test_item_with_very_large_price(self):
        """Test creating an item with very large price."""
        item = Item("Expensive", 999999.99, Category.BURGERS)
        assert item.price == 999999.99

    def test_transaction_with_large_quantity(self):
        """Test transaction with very large quantity."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)
        item = Item("Item", 1.0, Category.BURGERS)

        tx.add_item(item, quantity=1000000)
        total = tx.compute_total()
        assert total == 1000000.0

    def test_transaction_with_many_items(self):
        """Test transaction with many different items."""
        Customer._id_counter = 0
        Item._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        total_expected = 0.0
        for i in range(100):
            item = Item(f"Item{i}", float(i + 1), Category.BURGERS)
            tx.add_item(item, quantity=1)
            total_expected += float(i + 1)

        assert len(tx.get_items()) == 100
        assert abs(tx.compute_total() - total_expected) < 0.01

    def test_empty_transaction_operations(self):
        """Test operations on an empty transaction."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")
        tx = Transaction(customer)

        # Operations on empty transaction
        assert tx.compute_total() == 0.0
        assert len(tx.get_items()) == 0

        item = Item("Item", 5.0, Category.BURGERS)
        tx.remove_item(item)  # Remove non-existent item

        assert tx.compute_total() == 0.0

    def test_customer_with_many_transactions(self):
        """Test customer with many transactions."""
        Customer._id_counter = 0
        Transaction._id_counter = 0

        customer = Customer("Alice", "alice@example.com")

        for i in range(100):
            tx = Transaction(customer)
            item = Item(f"Item{i}", float(i), Category.BURGERS)
            tx.add_item(item)
            customer.add_transaction(tx)

        assert len(customer.get_purchase_history()) == 100

    def test_rating_boundary_exact_values(self):
        """Test popularity rating at exact boundaries."""
        item = Item("Item", 5.0, Category.BURGERS, popularity_rating=0.0)
        assert item.popularity_rating == 0.0

        item.update_rating(5.0)
        assert item.popularity_rating == 5.0

        # Just inside boundaries
        item.update_rating(0.00001)
        assert item.popularity_rating == pytest.approx(0.00001)

        item.update_rating(4.99999)
        assert item.popularity_rating == pytest.approx(4.99999)

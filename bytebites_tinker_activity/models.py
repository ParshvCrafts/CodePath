"""
ByteBites Backend OOP Models

Implements Customer, Item, Menu, and Transaction classes with proper
type hints, validation, and business logic as specified in the design.

Gap fixes from spec:
- Auto-incremented unique IDs (customer_id, item_id, transaction_id)
- Transaction holds reference to Customer (bidirectional)
- Item quantities tracked via dict[Item, int]
- Category as strict Enum (no loose strings)
- TransactionStatus for order lifecycle
- Timestamp on all transactions
- Email validation for user verification
- Bounds checking on popularity rating (0.0-5.0)
"""

from enum import Enum
from datetime import datetime
from typing import Dict, List


class Category(Enum):
    """Enumeration of menu categories to prevent string-based category errors."""
    BURGERS = "Burgers"
    DRINKS = "Drinks"
    DESSERTS = "Desserts"
    SIDES = "Sides"


class TransactionStatus(Enum):
    """Enumeration of transaction lifecycle states."""
    PENDING = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class Item:
    """
    Represents a food/drink item on the menu.

    Attributes:
        item_id: Unique identifier (auto-incremented)
        name: Item name (e.g., "Spicy Burger")
        price: Price in dollars (e.g., 12.99)
        category: Category enum (BURGERS, DRINKS, DESSERTS, SIDES)
        popularity_rating: Float between 0.0-5.0 representing item popularity
        is_available: Boolean indicating if item is currently available for purchase
    """

    _id_counter: int = 0

    def __init__(
        self,
        name: str,
        price: float,
        category: Category,
        popularity_rating: float = 0.0,
        is_available: bool = True
    ) -> None:
        Item._id_counter += 1
        self.item_id: int = Item._id_counter
        self.name: str = name
        self.price: float = price
        self.category: Category = category
        self.popularity_rating: float = popularity_rating
        self.is_available: bool = is_available

        # Validate popularity_rating on construction
        if not 0.0 <= popularity_rating <= 5.0:
            raise ValueError("Popularity rating must be between 0.0 and 5.0")

    def update_rating(self, new_rating: float) -> None:
        """
        Update the popularity rating with bounds validation.

        Args:
            new_rating: New rating value (must be between 0.0 and 5.0)

        Raises:
            ValueError: If rating is outside valid range [0.0, 5.0]
        """
        if not 0.0 <= new_rating <= 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        self.popularity_rating = new_rating

    def get_details(self) -> str:
        """
        Return a formatted string representation of the item.

        Returns:
            String with format: [ID] Name | $Price | Category | ★ Rating
        """
        return (
            f"[{self.item_id}] {self.name} | "
            f"${self.price:.2f} | {self.category.value} | "
            f"★ {self.popularity_rating:.1f}"
        )

    def __repr__(self) -> str:
        return f"Item(id={self.item_id}, name='{self.name}', price=${self.price:.2f})"


class Menu:
    """
    Manages a collection of items, supporting filtering and mutation.

    The menu acts as a mutable catalog of items that can be filtered by
    category and searched by properties.
    """

    def __init__(self) -> None:
        """Initialize an empty menu."""
        self._items: List[Item] = []

    def add_item(self, item: Item) -> None:
        """
        Add an item to the menu.

        Args:
            item: Item object to add
        """
        self._items.append(item)

    def remove_item(self, item: Item) -> None:
        """
        Remove an item from the menu.

        Args:
            item: Item object to remove

        Raises:
            ValueError: If item is not in menu
        """
        if item not in self._items:
            raise ValueError(f"Item {item.name} not found in menu")
        self._items.remove(item)

    def filter_by_category(self, category: Category) -> List[Item]:
        """
        Filter menu items by category, including only available items.

        Args:
            category: Category enum to filter by

        Returns:
            List of items in the specified category that are available
        """
        return [
            item for item in self._items
            if item.category == category and item.is_available
        ]

    def get_all_items(self) -> List[Item]:
        """
        Get all items in the menu (including unavailable ones).

        Returns:
            Copy of the complete item list
        """
        return list(self._items)

    def __len__(self) -> int:
        """Return the number of items in the menu."""
        return len(self._items)

    def __repr__(self) -> str:
        return f"Menu(items={len(self._items)})"


class Transaction:
    """
    Represents a customer order grouping selected items and computing total cost.

    Attributes:
        transaction_id: Unique identifier (auto-incremented)
        customer: Reference to the Customer who placed the order
        items: Dictionary mapping Item objects to quantities ordered
        timestamp: When the transaction was created (auto-set)
        status: TransactionStatus enum (PENDING, COMPLETED, CANCELLED)
    """

    _id_counter: int = 0

    def __init__(self, customer: 'Customer') -> None:
        """
        Initialize a transaction for a customer.

        Args:
            customer: Customer object placing the order
        """
        Transaction._id_counter += 1
        self.transaction_id: int = Transaction._id_counter
        self.customer: 'Customer' = customer  # Bidirectional reference
        self._items: Dict[Item, int] = {}  # Item -> quantity mapping
        self.timestamp: datetime = datetime.now()
        self.status: TransactionStatus = TransactionStatus.PENDING

    def add_item(self, item: Item, quantity: int = 1) -> None:
        """
        Add an item to the transaction (or increase quantity if already present).

        Args:
            item: Item to add
            quantity: Number of this item to add (default: 1)

        Raises:
            ValueError: If quantity is less than 1
        """
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        self._items[item] = self._items.get(item, 0) + quantity

    def remove_item(self, item: Item) -> None:
        """
        Remove an item from the transaction.

        Args:
            item: Item to remove
        """
        self._items.pop(item, None)

    def compute_total(self) -> float:
        """
        Calculate the total cost of the transaction.

        Returns:
            Total cost (price × quantity summed across all items)
        """
        return sum(item.price * qty for item, qty in self._items.items())

    def get_items(self) -> Dict[Item, int]:
        """
        Get a copy of the items dictionary (item -> quantity).

        Returns:
            Dictionary mapping Item objects to their quantities
        """
        return dict(self._items)

    def mark_completed(self) -> None:
        """Mark this transaction as completed."""
        self.status = TransactionStatus.COMPLETED

    def mark_cancelled(self) -> None:
        """Mark this transaction as cancelled."""
        self.status = TransactionStatus.CANCELLED

    def __repr__(self) -> str:
        return (
            f"Transaction(id={self.transaction_id}, "
            f"customer={self.customer.name}, "
            f"items={len(self._items)}, "
            f"total=${self.compute_total():.2f}, "
            f"status={self.status.value})"
        )


class Customer:
    """
    Represents a customer in the ByteBites system.

    Attributes:
        customer_id: Unique identifier (auto-incremented)
        name: Customer name
        email: Customer email address (used for verification)
        is_verified: Boolean indicating if customer has been verified
        purchase_history: List of Transaction objects placed by this customer
    """

    _id_counter: int = 0

    def __init__(self, name: str, email: str) -> None:
        """
        Initialize a new customer.

        Args:
            name: Customer's name
            email: Customer's email address
        """
        Customer._id_counter += 1
        self.customer_id: int = Customer._id_counter
        self.name: str = name
        self.email: str = email
        self.is_verified: bool = False
        self._purchase_history: List[Transaction] = []

    def verify_user(self) -> bool:
        """
        Verify the customer based on email format validation.

        A valid email must contain an '@' symbol and a '.' in the domain.
        This is a minimal implementation; production systems would use
        more robust email validation and send confirmation emails.

        Returns:
            True if verification was successful, False otherwise
        """
        if "@" in self.email:
            domain = self.email.split("@")[-1]
            if "." in domain:
                self.is_verified = True
                return True
        return False

    def add_transaction(self, transaction: 'Transaction') -> None:
        """
        Record a transaction in the customer's purchase history.

        Args:
            transaction: Transaction object to add to history
        """
        self._purchase_history.append(transaction)

    def get_purchase_history(self) -> List['Transaction']:
        """
        Get a copy of the customer's transaction history.

        Returns:
            List of Transaction objects in chronological order
        """
        return list(self._purchase_history)

    def __repr__(self) -> str:
        return (
            f"Customer(id={self.customer_id}, name='{self.name}', "
            f"verified={self.is_verified}, "
            f"transactions={len(self._purchase_history)})"
        )


# =============================================================================
# VERIFICATION SCENARIO
# =============================================================================
# This scenario exercises all major methods and validates the system works
# end-to-end following the 5-step verification plan from the design.
# =============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("BYTEBITES VERIFICATION SCENARIO")
    print("=" * 70)

    # STEP 1: Build Catalog
    print("\n[STEP 1] Building catalog with sample items...")
    burger = Item("Spicy Burger", 12.99, Category.BURGERS, popularity_rating=4.5)
    soda = Item("Large Soda", 3.49, Category.DRINKS, popularity_rating=3.8)
    cake = Item("Lava Cake", 6.99, Category.DESSERTS, popularity_rating=4.9)
    fries = Item("Crispy Fries", 4.99, Category.SIDES, popularity_rating=4.2)

    print(f"  [OK] Created {burger}")
    print(f"  [OK] Created {soda}")
    print(f"  [OK] Created {cake}")
    print(f"  [OK] Created {fries}")

    # STEP 2: Populate Menu and Filter
    print("\n[STEP 2] Populating menu and testing filtering...")
    menu = Menu()
    for item in [burger, soda, cake, fries]:
        menu.add_item(item)
    print(f"  [OK] Added {len(menu)} items to menu")

    drinks = menu.filter_by_category(Category.DRINKS)
    print(f"  [OK] Filtered DRINKS category: {len(drinks)} item(s)")
    assert len(drinks) == 1, "Should find exactly 1 drink"

    desserts = menu.filter_by_category(Category.DESSERTS)
    print(f"  [OK] Filtered DESSERTS category: {len(desserts)} item(s)")
    assert len(desserts) == 1, "Should find exactly 1 dessert"

    sides = menu.filter_by_category(Category.SIDES)
    print(f"  [OK] Filtered SIDES category: {len(sides)} item(s)")
    assert len(sides) == 1, "Should find exactly 1 side"

    # STEP 3: Create Verified Customer
    print("\n[STEP 3] Creating and verifying customer...")
    alice = Customer("Alice", "alice@example.com")
    print(f"  [OK] Created {alice}")

    is_verified = alice.verify_user()
    print(f"  [OK] Verification result: {is_verified}")
    assert is_verified is True, "Should verify valid email"
    assert alice.is_verified is True, "Customer should be marked verified"

    # STEP 4: Build Transaction with Quantities
    print("\n[STEP 4] Building transaction with quantities...")
    tx = Transaction(alice)
    print(f"  [OK] Created transaction {tx.transaction_id}")

    tx.add_item(burger, quantity=2)
    print(f"  [OK] Added 2x {burger.name}")

    tx.add_item(soda, quantity=1)
    print(f"  [OK] Added 1x {soda.name}")

    tx.add_item(fries, quantity=2)
    print(f"  [OK] Added 2x {fries.name}")

    # Verify quantities are tracked correctly
    items_dict = tx.get_items()
    print(f"  [OK] Transaction items: {len(items_dict)} unique items")

    # Verify total computation
    expected_total = (2 * burger.price) + (1 * soda.price) + (2 * fries.price)
    actual_total = tx.compute_total()
    print(f"  [OK] Computed total: ${actual_total:.2f}")
    print(f"    Expected: ${expected_total:.2f}")
    assert abs(actual_total - expected_total) < 0.001, "Total computation error"

    # Verify bidirectional reference
    assert tx.customer is alice, "Transaction should reference customer"
    print(f"  [OK] Transaction correctly references customer: {tx.customer.name}")

    # STEP 5: Record in History
    print("\n[STEP 5] Recording transaction in customer history...")
    alice.add_transaction(tx)
    history = alice.get_purchase_history()
    print(f"  [OK] Added transaction to customer history")
    print(f"  [OK] Customer now has {len(history)} transaction(s)")
    assert len(history) == 1, "Should have 1 transaction"

    # STEP 6: Additional Tests
    print("\n[STEP 6] Running additional edge case tests...")

    # Test rating update with bounds
    original_rating = burger.popularity_rating
    burger.update_rating(5.0)
    assert burger.popularity_rating == 5.0
    print(f"  [OK] Updated rating to maximum (5.0)")

    burger.update_rating(0.0)
    assert burger.popularity_rating == 0.0
    print(f"  [OK] Updated rating to minimum (0.0)")

    burger.update_rating(original_rating)

    # Test invalid rating
    try:
        burger.update_rating(5.1)
        assert False, "Should reject rating > 5.0"
    except ValueError:
        print(f"  [OK] Correctly rejected invalid rating (5.1)")

    # Test invalid quantity
    try:
        tx2 = Transaction(alice)
        tx2.add_item(burger, quantity=0)
        assert False, "Should reject quantity < 1"
    except ValueError:
        print(f"  [OK] Correctly rejected invalid quantity (0)")

    # Test item removal from menu
    initial_count = len(menu)
    menu.remove_item(fries)
    assert len(menu) == initial_count - 1
    print(f"  [OK] Successfully removed item from menu")

    # Test removing non-existent item
    try:
        menu.remove_item(fries)  # Already removed
        assert False, "Should raise error when removing non-existent item"
    except ValueError:
        print(f"  [OK] Correctly rejected removal of non-existent item")

    # Test transaction status tracking
    tx.mark_completed()
    assert tx.status == TransactionStatus.COMPLETED
    print(f"  [OK] Transaction status tracking works (COMPLETED)")

    # Test unavailable items are filtered out
    burger.is_available = False
    burgers = menu.filter_by_category(Category.BURGERS)
    assert len(burgers) == 0, "Should exclude unavailable items from filtering"
    print(f"  [OK] Unavailable items correctly excluded from filtering")
    burger.is_available = True

    # Test verification with invalid email
    bob = Customer("Bob", "invalid.email")
    result = bob.verify_user()
    assert result is False, "Should reject invalid email"
    assert bob.is_verified is False
    print(f"  [OK] Correctly rejected invalid email (no @ symbol)")

    # Test another invalid email format
    charlie = Customer("Charlie", "charlie@nodomain")
    result = charlie.verify_user()
    assert result is False, "Should reject email without domain extension"
    assert charlie.is_verified is False
    print(f"  [OK] Correctly rejected invalid email (no domain extension)")

    print("\n" + "=" * 70)
    print("ALL VERIFICATION TESTS PASSED [OK]")
    print("=" * 70)
    print(f"\nFinal state:")
    print(f"  • Menu has {len(menu)} items")
    print(f"  • Customer {alice.name} (ID: {alice.customer_id}) is verified")
    print(f"  • {alice.name} has {len(alice.get_purchase_history())} transaction(s)")
    print(f"  • Transaction {tx.transaction_id}: ${tx.compute_total():.2f} ({tx.status.value})")

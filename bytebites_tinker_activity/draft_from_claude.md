# ByteBites Class Design — UML Diagram & Critical Analysis

## Context

The spec describes a food-ordering backend with four OOP classes. No code exists yet.
This plan captures the intended UML design, flags every gap against the feature request,
and produces a complete, production-quality implementation plan.

---

## UML Class Diagram (Text-Based)

```
                          ┌──────────────────────────────┐
                          │           <<enum>>           │
                          │           Category           │
                          ├──────────────────────────────┤
                          │  BURGERS                     │
                          │  DRINKS                      │
                          │  DESSERTS                    │
                          │  SIDES                       │
                          └──────────────────────────────┘
                                        ▲
                                        │ uses
          ┌─────────────────────────────┼──────────────────────┐
          │                             │                      │
          ▼                             │                      ▼
┌─────────────────────┐                 │       ┌─────────────────────────┐
│      Customer       │                 │       │          Menu           │
├─────────────────────┤                 │       ├─────────────────────────┤
│ - customer_id: int  │                 │       │ - items: list[Item]     │
│ - name: str         │                 │       ├─────────────────────────┤
│ - email: str  [!]   │                 │       │ + add_item(item)        │
│ - is_verified: bool │                 │       │ + remove_item(item)     │
│ - purchase_history: │                 │       │ + filter_by_category()  │
│     list[Transaction│]                │       │ + get_all_items()       │
├─────────────────────┤                 │       └──────────┬──────────────┘
│ + verify_user():bool│                 │                  │ contains 0..*
│ + get_history()     │                 │                  │ (aggregation)
│ + add_transaction() │                 │                  ▼
└────────┬────────────┘                 │       ┌─────────────────────────┐
         │ has 0..* (aggregation)       │       │          Item           │
         ▼                             └───────▶├─────────────────────────┤
┌─────────────────────┐                         │ - item_id: int          │
│     Transaction     │                         │ - name: str             │
├─────────────────────┤                         │ - price: float          │
│ - transaction_id: int│                        │ - category: Category    │
│ - customer: Customer │◀── associated with ─── │ - popularity_rating:    │
│ - items: list[Item] │                         │     float  (0.0–5.0)    │
│ - timestamp: datetime│◀── [!] MISSING in spec │ - is_available: bool[!] │
│ - status: str   [!] │                         ├─────────────────────────┤
├─────────────────────┤                         │ + get_details(): str    │
│ + add_item(item)    │  contains 1..* ─────────│ + update_rating()       │
│ + remove_item(item) │─────────────────────────▶                         │
│ + compute_total()   │                         └─────────────────────────┘
└─────────────────────┘

[!] = attribute absent from spec but required for a correct implementation
```

---

## Relationship Map

| Relationship              | Type        | Multiplicity | Note                                    |
|---------------------------|-------------|--------------|---------------------------------------- |
| Customer → Transaction    | Aggregation | 1 to 0..*    | purchase_history stores past orders     |
| Transaction → Customer    | Association | * to 1       | ⚠ Spec omits this back-reference        |
| Transaction → Item        | Aggregation | 1 to 1..*    | at least one item per transaction       |
| Menu → Item               | Aggregation | 1 to 0..*    | menu is a catalog, not owner of items   |

---

## Gap Analysis — What the Spec Misses

### 1. No Unique Identifiers (Critical Bug Risk)
- **Problem:** Without `customer_id`, `item_id`, `transaction_id` you cannot distinguish
  two customers named "John" or two "Spicy Burger" items. Every lookup is O(n) string scan.
- **Fix:** Add `int` id fields, auto-incremented via a class-level counter or UUID.

### 2. Transaction Has No Reference Back to Customer (Logic Error)
- **Problem:** The spec says Customer stores purchase history, but Transaction doesn't
  know *who* placed it. You cannot reconstruct "all orders by customer X" from the
  Transaction side — that is a broken bidirectional relationship.
- **Fix:** `Transaction` must hold `self.customer: Customer`.

### 3. No Item Quantity in Transaction (Silent Data Loss)
- **Problem:** `items: list[Item]` cannot represent "2 Spicy Burgers". If a user orders
  3 of the same item you either duplicate objects (wasteful) or silently lose count.
- **Fix:** Use `items: dict[Item, int]` or a `LineItem` helper with `(item, quantity)`.
  `compute_total()` must multiply price × quantity.

### 4. "Verify Real Users" Is Undefined (Spec Ambiguity)
- **Problem:** The spec says the system should "verify they are real users" but no
  mechanism is described. This is the most ambiguous requirement.
- **Fix (minimal):** Add `is_verified: bool` flag and a `verify_user()` method.
  A production system would also need `email: str` at minimum.

### 5. Category Is a Loose String (Type Safety Risk)
- **Problem:** `category: str` allows `"drinks"`, `"DRINKS"`, `"Drinkss"` — all
  different values. Filtering by category becomes fragile.
- **Fix:** Use an `Enum` (`class Category(Enum)`). The spec even names examples:
  "Drinks", "Desserts" — these are natural enum members.

### 6. `popularity_rating` Has No Defined Scale or Update Mechanism
- **Problem:** Is it 0–5? 0–100? Who updates it? A static field set at construction
  makes no sense for a "popularity" metric that should reflect purchase frequency.
- **Fix:** Define scale (float 0.0–5.0). Add `update_rating(new_rating: float)` with
  bounds validation. Ideally derive it from transaction history.

### 7. Menu Has No Mutation Methods (Incomplete API)
- **Problem:** The spec only mentions "filter by category" but a real menu needs
  `add_item()` and `remove_item()` to be useful. Without these the Menu is immutable
  after construction, which cannot model a real restaurant.
- **Fix:** Add `add_item(item: Item)` and `remove_item(item: Item)`.

### 8. Transaction Has No Timestamp or Status (Missing Business Logic)
- **Problem:** Without a timestamp you cannot sort purchase history or audit orders.
  Without a status (pending/completed/cancelled) you can't distinguish an open cart
  from a completed order.
- **Fix:** Add `timestamp: datetime` (auto-set on construction) and `status: str`
  or a `TransactionStatus` enum.

---

## Metacognitive Consistency Check

| Question                                              | Answer                                          |
|-------------------------------------------------------|--------------------------------------------------|
| Can I explain Customer in one sentence?               | ✅ A verified user with a history of orders.     |
| Can I explain Item in one sentence?                   | ✅ A food/drink product with price and category. |
| Can I explain Menu in one sentence?                   | ✅ A searchable catalog of all available items.  |
| Can I explain Transaction in one sentence?            | ✅ A grouped order linking a customer to items + total. |
| Does Customer need Transaction before Transaction exists? | ⚠ Circular dependency — must use forward reference or decouple via IDs. |
| Can compute_total() work without quantity?            | ❌ No — a critical data model bug.              |
| Is "verify real user" implementable from the spec?   | ❌ Spec is ambiguous — need minimal `is_verified` flag. |

---

## Recommended Final Class Signatures (Python)

```python
from enum import Enum
from datetime import datetime
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

class Category(Enum):
    BURGERS  = "Burgers"
    DRINKS   = "Drinks"
    DESSERTS = "Desserts"
    SIDES    = "Sides"

class TransactionStatus(Enum):
    PENDING   = "Pending"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"

@dataclass
class Item:
    item_id: int
    name: str
    price: float                     # e.g. 9.99
    category: Category               # enum — not a raw string
    popularity_rating: float = 0.0  # 0.0–5.0 scale
    is_available: bool = True

    def update_rating(self, new_rating: float) -> None:
        if not 0.0 <= new_rating <= 5.0:
            raise ValueError("Rating must be between 0.0 and 5.0")
        self.popularity_rating = new_rating

    def get_details(self) -> str:
        return (f"[{self.item_id}] {self.name} | "
                f"${self.price:.2f} | {self.category.value} | "
                f"★ {self.popularity_rating:.1f}")


class Menu:
    def __init__(self) -> None:
        self._items: list[Item] = []

    def add_item(self, item: Item) -> None:
        self._items.append(item)

    def remove_item(self, item: Item) -> None:
        self._items.remove(item)

    def filter_by_category(self, category: Category) -> list[Item]:
        return [i for i in self._items if i.category == category and i.is_available]

    def get_all_items(self) -> list[Item]:
        return list(self._items)


class Transaction:
    _id_counter: int = 0

    def __init__(self, customer: "Customer") -> None:
        Transaction._id_counter += 1
        self.transaction_id: int = Transaction._id_counter
        self.customer: "Customer" = customer       # back-reference spec forgot
        self._items: dict[Item, int] = {}          # item → quantity
        self.timestamp: datetime = datetime.now()
        self.status: TransactionStatus = TransactionStatus.PENDING

    def add_item(self, item: Item, quantity: int = 1) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1")
        self._items[item] = self._items.get(item, 0) + quantity

    def remove_item(self, item: Item) -> None:
        self._items.pop(item, None)

    def compute_total(self) -> float:
        return sum(item.price * qty for item, qty in self._items.items())

    def get_items(self) -> dict[Item, int]:
        return dict(self._items)


class Customer:
    _id_counter: int = 0

    def __init__(self, name: str, email: str) -> None:
        Customer._id_counter += 1
        self.customer_id: int = Customer._id_counter
        self.name: str = name
        self.email: str = email
        self.is_verified: bool = False
        self._purchase_history: list[Transaction] = []

    def verify_user(self) -> bool:
        """Minimal verification: mark as verified if email looks valid."""
        self.is_verified = "@" in self.email and "." in self.email.split("@")[-1]
        return self.is_verified

    def add_transaction(self, transaction: Transaction) -> None:
        self._purchase_history.append(transaction)

    def get_purchase_history(self) -> list[Transaction]:
        return list(self._purchase_history)
```

---

## Files to Create

| File                                       | Purpose                         |
|--------------------------------------------|---------------------------------|
| `bytebites_tinker_activity/bytebites.py`   | All four classes + Category enum |
| `bytebites_tinker_activity/test_bytebites.py` | End-to-end smoke tests        |

---

## Verification Plan

Run the following scenario end-to-end to confirm correctness:

```python
# 1. Build catalog
burger = Item(1, "Spicy Burger", 12.99, Category.BURGERS, popularity_rating=4.5)
soda   = Item(2, "Large Soda",    3.49, Category.DRINKS,  popularity_rating=3.8)
cake   = Item(3, "Lava Cake",     6.99, Category.DESSERTS, popularity_rating=4.9)

# 2. Populate menu and filter
menu = Menu()
for item in [burger, soda, cake]:
    menu.add_item(item)
assert len(menu.filter_by_category(Category.DRINKS)) == 1

# 3. Create verified customer
alice = Customer("Alice", "alice@example.com")
assert alice.verify_user() is True

# 4. Build transaction with quantities
tx = Transaction(alice)
tx.add_item(burger, quantity=2)
tx.add_item(soda,   quantity=1)
expected_total = 2 * 12.99 + 1 * 3.49   # 29.47
assert abs(tx.compute_total() - expected_total) < 0.001
assert tx.customer is alice

# 5. Record in history
alice.add_transaction(tx)
assert len(alice.get_purchase_history()) == 1

print("All assertions passed ✓")
```

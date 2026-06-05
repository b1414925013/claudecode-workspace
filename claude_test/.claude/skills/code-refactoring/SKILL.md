---
name: code-refactoring
description: Code refactoring best practices and patterns for AI agents. Use when simplifying and restructuring code while preserving behavior, improving clarity, reducing complexity, and applying design patterns.
---

# Code Refactoring

Systematic approach to refactoring code with proven design patterns, focusing on behavioral preservation and incremental improvement.

## Process

### Step 1: Extract Method

Break long functions into smaller, named functions with clear intent:

```python
# Before
def process_order(order):
    # validate
    if not order.id or not order.items:
        raise ValueError("Invalid order")
    # calculate
    total = sum(item.price * item.quantity for item in order.items)
    tax = total * 0.08
    grand_total = total + tax
    # apply discount
    if order.coupon:
        grand_total *= 0.9
    # save
    db.save(order.id, grand_total)
    return grand_total

# After
def validate_order(order):
    if not order.id or not order.items:
        raise ValueError("Invalid order")

def calculate_total(order):
    subtotal = sum(item.price * item.quantity for item in order.items)
    return apply_tax_and_discount(subtotal, order.coupon)

def apply_tax_and_discount(amount, coupon):
    with_tax = amount * 1.08
    return with_tax * 0.9 if coupon else with_tax

def process_order(order):
    validate_order(order)
    total = calculate_total(order)
    db.save(order.id, total)
    return total
```

### Step 2: Remove Duplication (DRY)

Extract common logic into shared functions or base classes:

```python
# Before
def format_user_name(user):
    return f"{user.last_name}, {user.first_name}"

def format_admin_name(admin):
    return f"{admin.last_name}, {admin.first_name}"

# After
def format_person_name(person):
    return f"{person.last_name}, {person.first_name}"
```

### Step 3: Replace Conditional with Polymorphism

Replace complex conditionals with polymorphic dispatch:

```python
# Before
def calculate_shipping(order):
    if order.type == "standard":
        return 5.99
    elif order.type == "express":
        return 14.99
    elif order.type == "overnight":
        return 29.99

# After
class StandardShipping:
    def cost(self): return 5.99

class ExpressShipping:
    def cost(self): return 14.99

class OvernightShipping:
    def cost(self): return 29.99
```

### Step 4: Introduce Parameter Object

Group related parameters into a cohesive object:

```python
# Before
def create_event(title, start_date, end_date, location, max_attendees):
    pass

# After
@dataclass
class EventConfig:
    title: str
    start_date: datetime
    end_date: datetime
    location: str
    max_attendees: int

def create_event(config: EventConfig):
    pass
```

### Step 5: Apply SOLID Principles

- **Single Responsibility**: Each class/function has exactly one reason to change
- **Open/Closed**: Open for extension, closed for modification
- **Liskov Substitution**: Derived classes must be substitutable for base classes
- **Interface Segregation**: Small, focused interfaces over large monolithic ones
- **Dependency Inversion**: Depend on abstractions, not concretions

## Refactoring Checklist

Before considering refactoring complete, verify:

- [ ] Each function has a single responsibility (SRP)
- [ ] No duplicated logic (DRY)
- [ ] Functions are under 20 lines where practical
- [ ] Functions accept 3 or fewer parameters (use objects for more)
- [ ] Descriptive naming — intent is clear without comments
- [ ] No magic numbers or string literals (use named constants)
- [ ] Conditionals are replaced with polymorphism where appropriate
- [ ] Tests pass before and after (no behavioral change)
- [ ] No dead code or commented-out code remains

## Constraints

- **Test first**: Write/verify tests before refactoring
- **Small steps**: One refactoring pattern at a time, commit after each
- **No functional changes**: Refactoring changes structure, not behavior
- **Measure**: Use complexity metrics (cyclomatic, cognitive) to validate improvement

## Multi-Agent Workflow

For complex refactoring, split responsibilities:

- **Primary Agent** (Claude): Perform the refactoring
- **Analysis Agent**: Scan codebase for duplication and code smells
- **Verification Agent**: Run tests and validate no behavioral changes

## Common Code Smells

| Smell | Refactoring |
|-------|-------------|
| Long Method | Extract Method |
| Large Class | Extract Class |
| Duplicate Code | Extract Method / Pull Up Field |
| Long Parameter List | Introduce Parameter Object |
| Switch Statements | Replace Conditional with Polymorphism |
| Primitive Obsession | Replace Primitive with Object |
| Feature Envy | Move Method |
| Shotgun Surgery | Move Method / Inline Class |

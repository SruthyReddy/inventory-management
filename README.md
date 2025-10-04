# Warehouse Inventory Management Tool

This Django-based tool manages warehouse locations and inventory with commands for:

- Registering/unregistering locations
- Incrementing/decrementing inventory
- Transferring inventory
- Observing inventory

## Design Decisions

- **Data Structures**: Django ORM models `LocationMaster`, `StockDetail` and `MoveInventory` to handle locations, inventory and inventory transfers.
- **Persistence**: Uses SQLite for storing locations and stock (no PostgreSQL setup required).
- **Inventory Transfer**: Atomic transaction to ensure source and destination updates are consistent.
- **Management Commands**: Commands simulate CLI input/output (LOCATION REGISTER, INVENTORY INCREMENT, etc.).
- **External Dependencies**: Django for ORM & management commands.

## Setup Instructions

1. **Extract zip and navigate to project**:
```bash
cd inventory_management
````

2. **Create virtual environment**:

```bash
python3 -m venv venv
source venv/bin/activate   # macOS/Linux
# OR
venv\Scripts\activate      # Windows
```

3. **Install dependencies**:

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Migrate database**:

```bash
python manage.py makemigrations
python manage.py migrate
```

5. **Run server**:

```bash
python manage.py runserver
```

---

## Usage Examples

**Register location**

```bash
python manage.py location_master REGISTER LA
```

**Increment stock**

```bash
python manage.py stock_detail INCREMENT LA IA 5
```

**Transfer stock**

```bash
python manage.py move_inventory TRANSFER LA LB IA 2
```

**Observe inventory**

```bash
python manage.py stock_detail OBSERVE LB
```

**Unregister location**

```bash
python manage.py location_master UNREGISTER LA
```

````

---

### 4️⃣ How to Make the Zip File

1. Make sure your folder structure matches above.  
2. On macOS/Linux:
```bash
cd ..
zip -r inventory_management.zip inventory_management/
````

3. On Windows:

* Right-click the `inventory_management` folder → Send to → Compressed (zipped) folder.

This zip will contain everything needed: source code, requirements, management commands, and README.

---

If you want, I can **also provide a ready-to-copy `location_master.py`, `stock_detail.py`, and `move_inventory.py` files** so the zip is fully runnable.

Do you want me to do that next?

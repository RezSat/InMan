### Project Structure

```
inventory_management_app/
│
├── main.py                        # Entry point for the application
│
├── config/
│   └── config.py                  # Configuration settings (database path, API endpoints, etc.)
│
├── controllers/
│   ├── item_controller.py         # Business logic for items (add, edit, delete, search, etc.)
│   ├── user_controller.py         # User authentication and management logic
│   └── sync_controller.py         # Synchronization logic (online/offline, syncing database)
│
├── models/
│   ├── item_model.py              # Item model, database interactions for items
│   ├── user_model.py              # User model, database interactions for user accounts
│   └── database.py                # Database connection and operations
│
├── views/
│   ├── main_view.py               # Main application window, layout setup
│   ├── item_view.py               # Item-related views (forms, listings)
│   ├── user_view.py               # User-related views (login, register, etc.)
│   └── sync_view.py               # Synchronization status, alerts, etc.
│
├── gui/
│   ├── components/
│   │   ├── item_card.py           # Custom item card widget (individual inventory items)
│   │   ├── navigation_bar.py      # Navigation bar component
│   │   └── user_avatar.py         # User profile/role icon or avatar
│   └── styles.py                  # Styles for customtkinter widgets (theme colors, fonts)
│
├── utils/
│   ├── validators.py              # Input validation functions (e.g., for forms)
│   ├── logger.py                  # Logging setup for debugging or error tracking
│   └── sync_utils.py              # Helper functions for synchronization
│
├── assets/
│   ├── icons/                     # Icons for UI elements
│   ├── images/                    # Any images used in the app
│   └── styles/                    # Style sheets if applicable
│
└── README.md                      # Documentation for setup, usage, etc.
```

alerts for network issues.


Database Schema

#### 1. **Employee Table**
   *Now includes division ID as a foreign key and keeps track of each employee's division and details.*

| Column          | Type    | Description                           |
|-----------------|---------|---------------------------------------|
| emp_id          | String  | Unique ID for each employee          |
| name            | String  | Employee name                        |
| division_id     | Integer | Foreign key to `Division`            |
| item_count      | Integer | Total number of assigned items       |
| date_joined     | Date    | Date employee joined the company     |

#### 2. **Division Table**
   *Includes a count of employees in each division.*

| Column           | Type    | Description                          |
|------------------|---------|--------------------------------------|
| division_id      | Integer | Unique ID for each division         |
| name             | String  | Name of the division                |
| employee_count   | Integer | Number of employees in this division|

#### 3. **Item Table**
   *Now includes additional details for item status and history tracking.*

| Column          | Type    | Description                           |
|-----------------|---------|---------------------------------------|
| item_id         | Integer | Unique ID for each item              |
| name            | String  | Item name                            |
| unique_key      | String  | Unique identifier (e.g., serial)     |
| is_common       | Boolean | Whether the item is common or unique |
| status          | String  | Current status (`active`, `retired`, `lost`, etc.)|
| last_assigned   | Date    | Date when the item was last assigned |

#### 4. **EmployeeItem Table** (Associative Table for Many-to-Many Relationship)
   *Tracks unique or shared items and keeps records of item ownership.*

| Column          | Type    | Description                           |
|-----------------|---------|---------------------------------------|
| id              | Integer | Primary key                          |
| emp_id          | String  | Foreign key to `Employee`            |
| item_id         | Integer | Foreign key to `Item`                |
| is_unique       | Boolean | Indicates if item is unique to this employee |
| date_assigned   | Date    | Date when item was assigned          |
| notes           | Text    | Additional notes (e.g., item conditions) |

#### 5. **User Table** (For System Manager)
   *Manager login table.*

| Column          | Type    | Description                           |
|-----------------|---------|---------------------------------------|
| user_id         | Integer | Unique ID for user                   |
| username        | String  | Login username                       |
| password        | String  | Hashed login password                |
| role            | String  | Role of the user (`manager`)         |

#### 6. **Log Table**
   *Enhanced to log all user actions, including system changes, searches, and item updates.*

| Column          | Type      | Description                           |
|-----------------|-----------|---------------------------------------|
| log_id          | Integer   | Unique ID for each log entry         |
| action_type     | String    | Type of action (`search`, `add_item`, etc.) |
| details         | Text      | Additional action details            |
| timestamp       | DateTime  | When the action occurred             |
| user_id         | Integer   | Foreign key to `User` performing the action (nullable for searches) |

#### 7. **ItemTransferHistory Table**
   *Tracks historical transfers of items between employees.*

| Column          | Type      | Description                           |
|-----------------|-----------|---------------------------------------|
| transfer_id     | Integer   | Unique ID for each transfer entry    |
| item_id         | Integer   | Foreign key to `Item`                |
| from_emp_id     | String    | Employee ID of the previous holder   |
| to_emp_id       | String    | Employee ID of the new holder        |
| transfer_date   | Date      | Date of transfer                     |
| notes           | Text      | Optional notes (e.g., reason for transfer)|

---

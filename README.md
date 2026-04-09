<img width="691" height="795" alt="openart-image_1775755360079_a1e0769a_1775755360132_79dff5bc" src="https://github.com/user-attachments/assets/28381b0c-aa4c-4328-a920-9a00d573f7ba" />


# Railroad Drawer

> Slide-out drawer panels with **governed server execution**.

**Part of the Railroad ecosystem** — Works standalone or with [Railroad Runtime](https://github.com/faroncoder/railroad-runtime).

**Zero dependencies. ~4KB minified.**

---

## Philosophy

**Client declares intent. Server owns execution.**

```javascript
// ❌ Client builds SQL
drawer.open({ sql: "SELECT * FROM users WHERE id = ?" });  // Dangerous

// ✅ Client sends intent
RailroadDrawer.open('user-summary', { user_id: 42 });  // Server owns SQL
```

The drawer is a **viewport into governed server functions**, not a query runner.

---

## Features

✅ **Left/right slide-out panels**  
✅ **Governed server execution** (no SQL exposure)  
✅ **Declarative triggers** (`data-drawer-view`)  
✅ **Programmatic API** (`RailroadDrawer.open()`)  
✅ **Backdrop with click-to-close**  
✅ **Keyboard support** (ESC to close)  
✅ **Size variants** (narrow, medium, wide, full)  
✅ **Railroad Runtime integration** (auto-rebind)  
✅ **Loader integration** (auto-show/hide)  
✅ **Toast integration** (error notifications)  

---

## Installation

**CDN (fastest):**
```html
<script src="https://unpkg.com/railroad-drawer@1.0.0/dist/drawer.min.js"></script>
```

**npm:**
```bash
npm install railroad-drawer
```

---

## Quick Start

### Client-Side (Declarative)

```html
<!-- Drawer trigger -->
<button 
  data-drawer-view="user-summary"
  data-drawer-args='{"user_id": 42}'
  data-drawer-position="right"
  data-drawer-size="medium">
  Open User Summary
</button>
```

### Client-Side (Programmatic)

```javascript
// Open drawer with governed server execution
RailroadDrawer.open('user-summary', { user_id: 42 });

// Close drawer
RailroadDrawer.close();
```

### Server-Side (Governed Registry)

**Python/Flask Example:**

```python
from railroad_drawer import drawer_view

@drawer_view('user-summary', allowed_params=['user_id'])
def user_summary(args, user):
    # Permission check
    if not can_view_user(user, args['user_id']):
        raise PermissionError("Not authorized")
    
    # Server owns SQL - client never sees it
    user_data = db.query("SELECT * FROM users WHERE id = ?", args['user_id'])
    
    # Return HTML fragment
    return render_template('user_summary.html', user=user_data)
```

**Django Example:**

```python
from railroad_drawer import drawer_view

@drawer_view('user-summary', allowed_params=['user_id'])
def user_summary(args, user):
    user_obj = User.objects.get(id=args['user_id'])
    return render(request, 'user_summary.html', {'user': user_obj})
```

---

## The Security Model

### ✅ What the Client Sends

```json
{
  "view": "user-summary",
  "args": {"user_id": 42}
}
```

**Client knows:**
- View name (intent)
- Allowed parameters
- Target drawer position/size

### ❌ What the Client Never Sees

- SQL queries
- Table/column names
- Join logic
- Permission rules
- Database schema
- Function implementation

### ✅ What the Server Owns

- View registry (approved functions)
- SQL execution
- Permission checks
- Parameter validation
- Response rendering

---

## API Reference

### `RailroadDrawer.open(view, args, options)`

Open a drawer with governed server execution.

```javascript
RailroadDrawer.open('user-summary', 
  { user_id: 42 },
  { 
    position: 'right',  // 'left' or 'right'
    size: 'medium'      // 'narrow', 'medium', 'wide', 'full'
  }
);
```

**Parameters:**
- `view` (string) - Registered view name on server
- `args` (object) - Allowed parameters for that view
- `options` (object) - Drawer display options

### `RailroadDrawer.close()`

Close the current drawer.

```javascript
RailroadDrawer.close();
```

### `RailroadDrawer.init(config)`

Configure drawer system (optional).

```javascript
RailroadDrawer.init({
  endpoint: '/api/drawer/',  // Server endpoint
  position: 'right',          // Default position
  size: 'medium',             // Default size
  backdrop: true,             // Show backdrop
  keyboard: true              // ESC closes drawer
});
```

---

## Declarative Attributes

### `data-drawer-view` (required)

Specifies which server-registered view to load.

```html
<button data-drawer-view="user-summary">Open</button>
```

### `data-drawer-args` (optional)

JSON object of parameters to send to server.

```html
<button 
  data-drawer-view="recent-orders"
  data-drawer-args='{"customer_id": 123, "limit": 10}'>
  Recent Orders
</button>
```

### `data-drawer-position` (optional)

Where drawer slides from: `left` or `right` (default: `right`).

```html
<button 
  data-drawer-view="filters"
  data-drawer-position="left">
  Filters
</button>
```

### `data-drawer-size` (optional)

Drawer width: `narrow` (300px), `medium` (400px), `wide` (600px), `full` (800px max).

```html
<button 
  data-drawer-view="project-details"
  data-drawer-size="wide">
  Project Details
</button>
```

### `data-drawer-close`

Closes the drawer when clicked (use inside drawer content).

```html
<button data-drawer-close>Cancel</button>
```

---

## Server-Side Registry Pattern

### Decorator Registration

```python
DRAWER_VIEWS = {}

def drawer_view(name, allowed_params=None):
    def decorator(func):
        def wrapper(args, user):
            # Validate params
            if allowed_params:
                for key in args.keys():
                    if key not in allowed_params:
                        raise ValueError(f"Param '{key}' not allowed")
            
            # Execute governed function
            return func(args, user)
        
        DRAWER_VIEWS[name] = wrapper
        return wrapper
    return decorator
```

### Endpoint Handler

```python
@app.route('/drawer/', methods=['POST'])
def drawer_endpoint():
    data = request.get_json()
    view_name = data.get('view')
    args = data.get('args', {})
    user = get_current_user(request)
    
    # Lookup in registry
    if view_name not in DRAWER_VIEWS:
        return {'error': 'Unknown view'}, 404
    
    # Execute governed function
    view_func = DRAWER_VIEWS[view_name]
    html = view_func(args, user)
    
    return html, 200, {'Content-Type': 'text/html'}
```

---

## Integration with Railroad Ecosystem

### With Railroad Runtime

Drawers automatically rebind after content loads:

```javascript
RailroadDrawer.open('user-summary', { user_id: 42 });
// After server response → RAILROAD.rebind() called automatically
```

### With Railroad Loader

Loading states handled automatically:

```javascript
RailroadDrawer.open('heavy-report', { report_id: 5 });
// Loader shows → server executes → loader hides
```

### With Railroad Toasts

Errors shown automatically:

```javascript
RailroadDrawer.open('invalid-view', {});
// Toast appears: "Failed to load invalid-view"
```

---

## Use Cases

- **Navigation menus** (slide from left)
- **User profiles** (quick summary)
- **Filter panels** (e-commerce)
- **Shopping carts** (slide from right)
- **Notification sidebars**
- **Settings panels**
- **Quick-view drawers**
- **Detail views** (click row → drawer opens)

---

## Examples

See `/examples/server.py` for complete Flask implementation with:
- User summary drawer
- Recent orders drawer
- Project audit drawer (owner-only)
- Permission checks
- Parameter validation

Run the demo:

```bash
cd examples
python server.py
# Open http://localhost:5000
```

---

## Security Best Practices

### ✅ Do This

```python
@drawer_view('user-summary', allowed_params=['user_id'])
def user_summary(args, user):
    # Permission check
    if not can_view_user(user, args['user_id']):
        raise PermissionError()
    
    # Controlled SQL
    return db.query("SELECT name, email FROM users WHERE id = ?", args['user_id'])
```

### ❌ Don't Do This

```python
@drawer_view('bad-example')
def bad_example(args, user):
    # Never do this - SQL from client
    sql = args.get('sql')  # ❌ DANGEROUS
    return db.execute(sql)
```

---

## Dark Theme Support

Automatically supports `prefers-color-scheme: dark`:

```css
@media (prefers-color-scheme: dark) {
  .railroad-drawer {
    background: #1f2937;
    color: #f9fafb;
  }
}
```

---

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS 14+, Android 5+)

---

## License

MIT © Faron Wheeler

---

## Links

- **Railroad Runtime:** https://github.com/faroncoder/railroad-runtime
- **Railroad Toasts:** https://github.com/faroncoder/railroad-toasts
- **Railroad Loader:** https://github.com/faroncoder/railroad-loader
- **Full Demo:** https://github.com/faroncoder/railroad-demo-full

---

## Core Principle

> **The drawer is a viewport into governed server execution.**
>
> Not a query runner. Not a data browser.  
> A controlled surface for approved, server-owned functions.

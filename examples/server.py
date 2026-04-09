"""
Railroad Drawer - Server-Side Pattern
Governed Registry for Drawer Views

Philosophy:
- Client sends intent (view name) + allowed params
- Server owns execution and SQL
- Drawer views are registered, validated functions
- No SQL or schema exposed to client
"""

from flask import Flask, request, jsonify, render_template_string
from functools import wraps
import json

app = Flask(__name__)

# ============================================================================
# GOVERNED REGISTRY - All allowed drawer views
# ============================================================================

DRAWER_VIEWS = {}

def drawer_view(name, allowed_params=None):
    """
    Decorator to register a governed drawer view
    """
    def decorator(func):
        @wraps(func)
        def wrapper(args, user):
            # Validate params
            if allowed_params:
                for key in args.keys():
                    if key not in allowed_params:
                        raise ValueError(f"Parameter '{key}' not allowed for view '{name}'")
            
            # Execute governed function
            return func(args, user)
        
        DRAWER_VIEWS[name] = wrapper
        return wrapper
    return decorator


# ============================================================================
# DRAWER VIEWS - Each owns its SQL and validation
# ============================================================================

@drawer_view('user-summary', allowed_params=['user_id'])
def user_summary(args, user):
    """
    User summary drawer
    Server owns SQL - client only sends intent
    """
    user_id = args.get('user_id')
    
    # Permission check
    if not can_view_user(user, user_id):
        raise PermissionError("Not authorized to view this user")
    
    # Controlled SQL (or ORM)
    # This is just example data - replace with real DB query
    user_data = {
        'id': user_id,
        'name': 'John Doe',
        'email': 'john@example.com',
        'role': 'Developer',
        'projects': 12,
        'last_active': '2026-04-09'
    }
    
    # Return HTML fragment
    return render_template_string('''
        <div class="drawer-panel">
            <h2>{{ user.name }}</h2>
            <div class="user-meta">
                <p><strong>Email:</strong> {{ user.email }}</p>
                <p><strong>Role:</strong> {{ user.role }}</p>
                <p><strong>Projects:</strong> {{ user.projects }}</p>
                <p><strong>Last Active:</strong> {{ user.last_active }}</p>
            </div>
            <div class="drawer-actions">
                <button onclick="RailroadDrawer.open('user-activity', {user_id: {{ user.id }} })">
                    View Activity
                </button>
                <button data-drawer-close>Close</button>
            </div>
        </div>
        <style>
            .drawer-panel h2 { margin-top: 0; }
            .user-meta { margin: 20px 0; }
            .user-meta p { margin: 10px 0; color: #6b7280; }
            .drawer-actions { margin-top: 30px; display: flex; gap: 10px; }
            .drawer-actions button {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
            }
            .drawer-actions button:first-child {
                background: #3b82f6;
                color: white;
            }
        </style>
    ''', user=user_data)


@drawer_view('recent-orders', allowed_params=['customer_id', 'limit'])
def recent_orders(args, user):
    """
    Recent orders drawer
    """
    customer_id = args.get('customer_id')
    limit = min(int(args.get('limit', 10)), 50)  # Cap at 50
    
    # Permission check
    if not can_view_customer(user, customer_id):
        raise PermissionError("Not authorized")
    
    # Controlled SQL
    orders = [
        {'id': 1001, 'date': '2026-04-08', 'total': '$156.00', 'status': 'Shipped'},
        {'id': 1002, 'date': '2026-04-05', 'total': '$89.50', 'status': 'Delivered'},
        {'id': 1003, 'date': '2026-04-01', 'total': '$245.00', 'status': 'Processing'},
    ][:limit]
    
    return render_template_string('''
        <div class="drawer-panel">
            <h2>Recent Orders</h2>
            <div class="orders-list">
                {% for order in orders %}
                <div class="order-item">
                    <div><strong>#{{ order.id }}</strong></div>
                    <div>{{ order.date }}</div>
                    <div>{{ order.total }}</div>
                    <div class="status">{{ order.status }}</div>
                </div>
                {% endfor %}
            </div>
        </div>
        <style>
            .orders-list { margin-top: 20px; }
            .order-item {
                display: grid;
                grid-template-columns: 80px 100px 80px 1fr;
                gap: 15px;
                padding: 12px;
                border-bottom: 1px solid #e5e7eb;
            }
            .order-item:hover { background: #f9fafb; }
            .status { text-align: right; font-weight: 500; }
        </style>
    ''', orders=orders)


@drawer_view('project-audit', allowed_params=['project_id'])
def project_audit(args, user):
    """
    Project audit drawer - owner only
    """
    # Permission check
    if not user.get('is_owner'):
        raise PermissionError("Owner only")
    
    project_id = args.get('project_id')
    
    # Controlled SQL - complex join, but client doesn't know
    audit_data = {
        'project_id': project_id,
        'total_commits': 1247,
        'total_hours': 342,
        'team_size': 5,
        'risk_score': 'Low'
    }
    
    return render_template_string('''
        <div class="drawer-panel">
            <h2>Project Audit</h2>
            <div class="audit-grid">
                <div class="metric">
                    <div class="metric-value">{{ audit.total_commits }}</div>
                    <div class="metric-label">Total Commits</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ audit.total_hours }}</div>
                    <div class="metric-label">Total Hours</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ audit.team_size }}</div>
                    <div class="metric-label">Team Size</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{{ audit.risk_score }}</div>
                    <div class="metric-label">Risk Score</div>
                </div>
            </div>
        </div>
        <style>
            .audit-grid {
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
                margin-top: 30px;
            }
            .metric {
                padding: 20px;
                background: #f9fafb;
                border-radius: 8px;
                text-align: center;
            }
            .metric-value {
                font-size: 2rem;
                font-weight: bold;
                color: #3b82f6;
            }
            .metric-label {
                margin-top: 8px;
                font-size: 0.9rem;
                color: #6b7280;
            }
        </style>
    ''', audit=audit_data)


# ============================================================================
# DRAWER ENDPOINT - Governed execution boundary
# ============================================================================

@app.route('/drawer/', methods=['POST'])
def drawer_endpoint():
    """
    Single governed endpoint for all drawer views
    
    Request:
        {
            "view": "user-summary",
            "args": {"user_id": 42}
        }
    
    Response:
        HTML fragment (no JSON, no SQL, no schema)
    """
    try:
        data = request.get_json()
        view_name = data.get('view')
        args = data.get('args', {})
        
        # Get current user (from session/auth)
        user = get_current_user(request)
        
        # Lookup view in registry
        if view_name not in DRAWER_VIEWS:
            return jsonify({'error': 'Unknown view'}), 404
        
        # Execute governed function
        view_func = DRAWER_VIEWS[view_name]
        html = view_func(args, user)
        
        return html, 200, {'Content-Type': 'text/html'}
        
    except PermissionError as e:
        return jsonify({'error': str(e)}), 403
    except ValueError as e:
        return jsonify({'error': str(e)}), 400
    except Exception as e:
        app.logger.error(f"Drawer error: {e}")
        return jsonify({'error': 'Internal error'}), 500


# ============================================================================
# PERMISSION HELPERS
# ============================================================================

def can_view_user(user, user_id):
    """Permission check - server owns this logic"""
    # In real app: check user.role, user.permissions, etc.
    return True

def can_view_customer(user, customer_id):
    """Permission check"""
    return True

def get_current_user(request):
    """Get current user from session/JWT/etc."""
    # In real app: check session, JWT, etc.
    return {
        'id': 1,
        'name': 'Admin User',
        'role': 'admin',
        'is_owner': True
    }


# ============================================================================
# EXAMPLE PAGE
# ============================================================================

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Railroad Drawer - Server Pattern Demo</title>
    <script src="https://unpkg.com/railroad-runtime@1.0.0/dist/railroad-runtime.min.js"></script>
    <script src="https://unpkg.com/railroad-toasts@1.0.1/dist/toasts.min.js"></script>
    <script src="https://unpkg.com/railroad-loader@1.0.1/dist/loader.min.js"></script>
    <script src="/static/drawer.js"></script>
</head>
<body style="font-family: sans-serif; padding: 40px; background: #0d1117; color: #e6edf3;">
    <h1>🚂 Drawer Server Pattern Demo</h1>
    <p>Client declares intent. Server owns execution.</p>
    
    <div style="margin-top: 40px;">
        <h2>Declarative Triggers:</h2>
        <button 
            data-drawer-view="user-summary"
            data-drawer-args='{"user_id": 42}'
            style="padding: 12px 24px; margin: 10px; background: #238636; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Open User Summary
        </button>
        
        <button 
            data-drawer-view="recent-orders"
            data-drawer-args='{"customer_id": 123, "limit": 5}'
            data-drawer-position="left"
            style="padding: 12px 24px; margin: 10px; background: #1f6feb; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Recent Orders (Left)
        </button>
        
        <button 
            data-drawer-view="project-audit"
            data-drawer-args='{"project_id": 789}'
            data-drawer-size="wide"
            style="padding: 12px 24px; margin: 10px; background: #8957e5; color: white; border: none; border-radius: 6px; cursor: pointer;">
            Project Audit (Wide)
        </button>
    </div>
    
    <div style="margin-top: 40px;">
        <h2>Programmatic API:</h2>
        <button onclick="RailroadDrawer.open('user-summary', {user_id: 99})"
            style="padding: 12px 24px; background: #da3633; color: white; border: none; border-radius: 6px; cursor: pointer;">
            RailroadDrawer.open()
        </button>
    </div>
    
    <div style="margin-top: 60px; padding: 20px; background: #161b22; border-radius: 8px;">
        <h3>Key Points:</h3>
        <ul style="line-height: 2;">
            <li>✅ Client sends <strong>view name</strong> + <strong>allowed params</strong></li>
            <li>✅ Server has <strong>registry</strong> of approved views</li>
            <li>✅ Each view <strong>owns its SQL</strong></li>
            <li>✅ No SQL, schema, or table names exposed</li>
            <li>✅ Permission checks in server</li>
            <li>✅ Returns <strong>HTML fragment</strong></li>
        </ul>
    </div>
</body>
</html>
    ''')


if __name__ == '__main__':
    app.run(debug=True, port=5000)

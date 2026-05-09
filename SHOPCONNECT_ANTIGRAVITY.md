# SHOPCONNECT — Context File for Antigravity

## What I'm building
A multi-vendor e-commerce platform for Burundi. Customers can buy from multiple shops in one order. The platform handles commission splitting between sellers and has a built-in logistics system called DukaConnect Shipping.

---

## Tech Stack
- **Backend:** Django 5.x + Django REST Framework + JWT auth
- **Database:** PostgreSQL 15+
- **Frontend:** React 18 + Vite + TailwindCSS

---

## Dependencies

### Python (venv)
```
Django==5.0.1
djangorestframework==3.14.0
djangorestframework-simplejwt==5.3.0
django-cors-headers==4.3.1
psycopg2-binary==2.9.9
python-decouple==3.8
gunicorn==21.2.0
django-filter==23.5
Pillow==10.2.0
```

### React (npm)
```
axios
react-router-dom
@tanstack/react-query
react-hook-form
zod
@hookform/resolvers
```

---

## Database
Full schema (34 tables) is here: E:\project\shopconnect\shopconnect_schema.sql

Rules to always follow when touching the DB:
- All PKs are UUID
- Soft delete via `deleted_at` — never hard delete users, shops, or products
- `email` is nullable — `phone` is the primary identifier (Burundi context)
- `unit_price` in `OrderItem` is a snapshot — never read from `Product.price` for past orders
- `OrderItem` = financial record / `OrderProduct` = logistics record — always linked via `order_item_id` FK
- Currency default is `BIF`
- All querysets must filter `deleted_at__isnull=True` by default

---

## Project Structure

### Django
```
backend/
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
└── apps/
    ├── users/            ← User, Seller, Shop + auth
    ├── catalog/          ← Category, Product, ProductImage, ProductVariant
    ├── orders/           ← Cart, Order, OrderItem, OrderProduct
    ├── payments/         ← Payment, Transaction, SellerPayout
    └── logistics/        ← Region, DeliveryMethod, Shipment, Tracking
```

### React
```
frontend/src/
├── pages/
│   ├── HomePage.jsx
│   ├── ProductDetailPage.jsx
│   ├── CartPage.jsx
│   ├── CheckoutPage.jsx
│   ├── OrderHistoryPage.jsx
│   ├── OrderDetailPage.jsx
│   ├── LoginPage.jsx
│   ├── RegisterPage.jsx
│   ├── ProfilePage.jsx
│   └── seller/
│       ├── DashboardPage.jsx
│       ├── ProductsPage.jsx
│       ├── OrdersPage.jsx
│       ├── ShopSettingsPage.jsx
│       └── AnalyticsPage.jsx
├── components/
│   ├── Navbar.jsx
│   ├── ProductCard.jsx
│   ├── ProductGrid.jsx
│   ├── CategoryMenu.jsx
│   ├── CartIcon.jsx
│   ├── SearchBar.jsx
│   ├── PriceFilter.jsx
│   ├── Pagination.jsx
│   ├── LoadingSpinner.jsx
│   ├── ToastNotification.jsx
│   └── ProtectedRoute.jsx
├── context/
│   ├── AuthContext.jsx      ← user state + token management
│   ├── CartContext.jsx      ← cart state synced with backend
│   └── ShopContext.jsx
└── services/
    ├── api.js               ← axios instance + interceptors
    ├── authService.js
    ├── productService.js
    ├── cartService.js
    ├── orderService.js
    ├── paymentService.js
    └── sellerService.js
```

---

## API Endpoints

### Auth
```
POST   /api/auth/register/
POST   /api/auth/login/
POST   /api/auth/logout/
GET    /api/auth/me/
POST   /api/auth/token/refresh/
```

### Catalog (public)
```
GET    /api/products/         ← ?category=&shop=&search=&min_price=&max_price=
GET    /api/products/{id}/
GET    /api/categories/
```

### Cart (authenticated)
```
GET    /api/cart/
POST   /api/cart/add/
PUT    /api/cart/update/{id}/
DELETE /api/cart/remove/{id}/
```

### Orders (authenticated)
```
POST   /api/orders/create/    ← converts cart → order
GET    /api/orders/
GET    /api/orders/{id}/
```

### Payments (authenticated)
```
POST   /api/payments/initiate/
POST   /api/payments/callback/    ← mobile money webhook (no auth, verified by signature)
GET    /api/payments/status/{order_id}/
```

### Seller (role: seller)
```
GET    /api/seller/shop/
PUT    /api/seller/shop/
GET    /api/seller/products/
POST   /api/seller/products/
PUT    /api/seller/products/{id}/
DELETE /api/seller/products/{id}/
GET    /api/seller/orders/
PUT    /api/seller/orders/{id}/status/
```

### Admin (role: admin)
```
GET    /api/admin/users/
PUT    /api/admin/users/{id}/status/
GET    /api/admin/shops/
PUT    /api/admin/shops/{id}/verify/
```

---

## Frontend Routes

```
/                          → HomePage
/products/:id              → ProductDetailPage
/cart                      → CartPage
/checkout                  → CheckoutPage
/orders                    → OrderHistoryPage
/orders/:id                → OrderDetailPage
/login                     → LoginPage
/register                  → RegisterPage
/profile                   → ProfilePage (protected)

/seller                    → seller/DashboardPage (protected, role=seller)
/seller/products           → seller/ProductsPage
/seller/products/new       → seller/ProductsPage (create mode)
/seller/products/:id/edit  → seller/ProductsPage (edit mode)
/seller/orders             → seller/OrdersPage
/seller/settings           → seller/ShopSettingsPage
/seller/analytics          → seller/AnalyticsPage
```

---

## Business Rules

### Order creation — one atomic block
When `POST /api/orders/create/` is called, do ALL of this inside `@transaction.atomic`:
1. Read cart items for the user
2. For each product: check `stock_quantity > 0`, lock row with `select_for_update()`
3. Create one `Order` record
4. Create one `OrderItem` per cart item (snapshot `unit_price` from product at this moment)
5. Create one `OrderProduct` per `OrderItem` (logistics link)
6. Decrement `product.stock_quantity` by quantity ordered
7. Delete all cart items for this user
8. Return the created order

If any step fails → rollback everything.

### Commission calculation
- Platform takes **5% of `total_price`** per `OrderItem`
- Formula: `commission = total_price * 0.05`
- `net_amount = total_price - commission`
- Create one `Transaction` record per `OrderItem` when payment status becomes `paid`
- Commission rate is stored on the `Transaction` record (`commission_rate = 0.05`) so future rate changes don't affect historical records

### Seller isolation
A seller can only read/write their own data:
```python
shop__seller__user = request.user
```
Apply this filter on every seller-scoped queryset. Never trust a shop_id from the request body — always derive it from the authenticated user.

### Soft delete
```python
# In every Manager or ViewSet queryset:
queryset = Model.objects.filter(deleted_at__isnull=True)

# To soft delete:
instance.deleted_at = timezone.now()
instance.save()
```

---

## CartContext Sync Pattern

CartContext holds state locally and syncs with the backend. Here's the exact pattern to follow:

```
On app load / login     → GET /api/cart/  and populate local state
On add item             → optimistic update local state → POST /api/cart/add/ → confirm or rollback
On update quantity      → optimistic update → PUT /api/cart/update/{id}/
On remove item          → optimistic update → DELETE /api/cart/remove/{id}/
On logout               → clear local cart state (backend cart persists for next login)
On checkout success     → clear local cart state (backend already cleared by order creation)
```

CartContext exposes: `{ items, itemCount, total, addItem, updateItem, removeItem, clearCart, loading }`

---

## Error Response Format

All API errors must return this exact structure:

```json
{
  "success": false,
  "error": {
    "code": "OUT_OF_STOCK",
    "message": "Ce produit n'est plus disponible.",
    "field": "product_id"
  }
}
```

- `code` → machine-readable, uppercase snake case, used by frontend to handle specific errors
- `message` → human-readable, in French (primary language for Burundi)
- `field` → optional, only for validation errors (maps to form field)

Success responses:
```json
{
  "success": true,
  "data": { ... }
}
```

Common error codes to use consistently:
```
OUT_OF_STOCK
PRODUCT_NOT_FOUND
SHOP_SUSPENDED
UNAUTHORIZED
FORBIDDEN
INVALID_CREDENTIALS
TOKEN_EXPIRED
PAYMENT_FAILED
ORDER_NOT_FOUND
CART_EMPTY
```

---

## Custom Permission Classes

```python
# users/permissions.py

class IsSeller(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'seller'

class IsShopOwner(BasePermission):
    # Used on product/order views — checks object-level ownership
    def has_object_permission(self, request, view, obj):
        return obj.shop.seller.user == request.user

class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'
```

---

## Axios Setup (api.js)

```javascript
// src/services/api.js
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  headers: { 'Content-Type': 'application/json' },
})

// Attach access token to every request
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

// Auto-refresh token on 401
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const original = error.config
    if (error.response?.status === 401 && !original._retry) {
      original._retry = true
      const refresh = localStorage.getItem('refresh_token')
      if (refresh) {
        const { data } = await axios.post(`${import.meta.env.VITE_API_URL}/auth/token/refresh/`, { refresh })
        localStorage.setItem('access_token', data.access)
        original.headers.Authorization = `Bearer ${data.access}`
        return api(original)
      }
    }
    return Promise.reject(error)
  }
)

export default api
```

---

## Environment Variables

```bash
# backend/.env
SECRET_KEY=
DEBUG=False
DATABASE_URL=postgresql://user:password@localhost:5432/shopconnect
ALLOWED_HOSTS=localhost,api.shopconnect.com
CORS_ALLOWED_ORIGINS=http://localhost:5173,https://shopconnect.com
JWT_SECRET_KEY=
MOBILE_MONEY_API_URL=https://api.lumicash.bi/v1
MOBILE_MONEY_API_KEY=
MOBILE_MONEY_CALLBACK_SECRET=   ← used to verify webhook signature

# frontend/.env
VITE_API_URL=http://localhost:8000/api
```

---

## Code Rules (apply to every file)

- `select_related` / `prefetch_related` on all list views — no N+1 queries
- `@transaction.atomic` on order creation and payment confirmation
- Form validation with `react-hook-form` + `zod` on the frontend
- Loading and error state required on every async operation in React
- No hardcoded status strings — Django Choices on backend, constants file on frontend

---

## How to respond to my requests

For every feature:
1. Exact code — Django model (if new), serializer, view, URL registration + React service function + component
2. File path for every file
3. Comments on non-obvious logic
4. What to test after implementing

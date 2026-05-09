-- ============================================================
-- SHOPCONNECT — RECOMMENDED DATABASE SCHEMA (v2)
-- 34 tables | PostgreSQL
-- Changes vs original: marked with -- NEW or -- CHANGED
-- ============================================================

-- ─── EXTENSIONS ───────────────────────────────────────────
CREATE EXTENSION IF NOT EXISTS "pgcrypto";   -- gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS "pg_trgm";    -- trigram search on products

-- ════════════════════════════════════════════════════════════
-- DOMAIN 1: USERS & IDENTITY
-- ════════════════════════════════════════════════════════════

CREATE TABLE regions (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(100) NOT NULL,
    type        VARCHAR(20) NOT NULL CHECK (type IN ('province','city','zone')),
    parent_id   UUID REFERENCES regions(id),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE users (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    email       VARCHAR(255) NOT NULL UNIQUE,
    phone       VARCHAR(30) UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role        VARCHAR(20) NOT NULL CHECK (role IN ('customer','seller','admin','driver')),
    region_id   UUID REFERENCES regions(id),
    address     TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'active' CHECK (status IN ('active','suspended','banned')),
    deleted_at  TIMESTAMP,                           -- NEW: soft delete
    updated_by  UUID REFERENCES users(id),          -- NEW: audit trail
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE sellers (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id),
    business_name       VARCHAR(200) NOT NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (verification_status IN ('pending','verified','rejected')),
    rating_average      DECIMAL(3,2) DEFAULT 0,
    total_reviews       INT NOT NULL DEFAULT 0,
    bank_account_ref    VARCHAR(255),               -- NEW: encrypted payout reference
    created_at          TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE shops (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id   UUID NOT NULL REFERENCES sellers(id),
    name        VARCHAR(200) NOT NULL,
    slug        VARCHAR(200) NOT NULL UNIQUE,       -- NEW: URL slug
    description TEXT,
    region_id   UUID REFERENCES regions(id),
    address     TEXT,
    status      VARCHAR(20) NOT NULL DEFAULT 'pending'
                CHECK (status IN ('pending','active','suspended','banned')),
    deleted_at  TIMESTAMP,                          -- NEW: soft delete
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ════════════════════════════════════════════════════════════
-- DOMAIN 2: CATALOG
-- ════════════════════════════════════════════════════════════

CREATE TABLE categories (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(150) NOT NULL,
    slug        VARCHAR(150) NOT NULL UNIQUE,       -- NEW
    parent_id   UUID REFERENCES categories(id),
    photo_url   VARCHAR(500),
    sort_order  INT NOT NULL DEFAULT 0,             -- NEW: UI ordering
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE products (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shop_id         UUID NOT NULL REFERENCES shops(id),
    category_id     UUID REFERENCES categories(id),
    name            VARCHAR(300) NOT NULL,
    slug            VARCHAR(300) NOT NULL,          -- NEW: unique per shop (use unique(shop_id,slug))
    description     TEXT,
    price           DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'BIF', -- NEW: ISO 4217
    discount_price  DECIMAL(15,2),
    stock_quantity  INT NOT NULL DEFAULT 0,
    condition       VARCHAR(20) DEFAULT 'new'
                    CHECK (condition IN ('new','used','refurbished')), -- NEW
    status          VARCHAR(20) NOT NULL DEFAULT 'draft'
                    CHECK (status IN ('draft','active','paused','archived')),
    deleted_at      TIMESTAMP,                      -- NEW: soft delete
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (shop_id, slug)
);
CREATE INDEX idx_products_shop ON products(shop_id, status);
CREATE INDEX idx_products_category ON products(category_id);
CREATE INDEX idx_products_name_trgm ON products USING gin(name gin_trgm_ops); -- NEW: full-text

CREATE TABLE product_images (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id  UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    image_url   VARCHAR(500) NOT NULL,
    is_main     BOOLEAN NOT NULL DEFAULT FALSE,
    sort_order  INT NOT NULL DEFAULT 0,             -- NEW
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE product_variants (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id       UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    name             VARCHAR(100) NOT NULL,
    value            VARCHAR(100) NOT NULL,
    additional_price DECIMAL(15,2) NOT NULL DEFAULT 0,
    stock_quantity   INT NOT NULL DEFAULT 0,
    sku              VARCHAR(100) UNIQUE,            -- NEW: unique variant code
    deleted_at       TIMESTAMP                       -- NEW: soft delete
);

CREATE TABLE product_tags (                          -- NEW TABLE
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    product_id  UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
    tag         VARCHAR(100) NOT NULL,
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (product_id, tag)
);
CREATE INDEX idx_product_tags_tag ON product_tags(tag);

CREATE TABLE discounts (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    type        VARCHAR(20) NOT NULL CHECK (type IN ('percentage','fixed')),
    value       DECIMAL(10,2) NOT NULL,
    product_id  UUID REFERENCES products(id),
    shop_id     UUID REFERENCES shops(id),           -- NEW: shop-level discounts
    start_date  DATE NOT NULL,
    end_date    DATE NOT NULL,
    is_active   BOOLEAN NOT NULL DEFAULT TRUE        -- NEW
);

CREATE TABLE coupons (                               -- NEW TABLE
    id                UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code              VARCHAR(50) NOT NULL UNIQUE,
    type              VARCHAR(20) NOT NULL CHECK (type IN ('percentage','fixed','free_shipping')),
    value             DECIMAL(10,2) NOT NULL,
    min_order_amount  DECIMAL(15,2) DEFAULT 0,
    usage_limit       INT,                           -- NULL = unlimited
    used_count        INT NOT NULL DEFAULT 0,
    user_id           UUID REFERENCES users(id),     -- NULL = public code
    shop_id           UUID REFERENCES shops(id),     -- NULL = platform-wide
    start_date        DATE NOT NULL,
    end_date          DATE NOT NULL,
    is_active         BOOLEAN NOT NULL DEFAULT TRUE,
    created_at        TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_coupons_code ON coupons(code);

CREATE TABLE wishlist (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    product_id  UUID NOT NULL REFERENCES products(id),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    UNIQUE (user_id, product_id)
);

-- ════════════════════════════════════════════════════════════
-- DOMAIN 3: ORDERS
-- ════════════════════════════════════════════════════════════

CREATE TABLE delivery_methods (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code        VARCHAR(50) NOT NULL UNIQUE,
    name        VARCHAR(150) NOT NULL,
    description TEXT,                               -- NEW
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE shipping_addresses (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    region_id   UUID REFERENCES regions(id),
    label       VARCHAR(50),                        -- NEW: e.g. Home, Work
    address     TEXT NOT NULL,
    phone       VARCHAR(30),
    is_default  BOOLEAN NOT NULL DEFAULT FALSE,     -- NEW
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE cart (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    product_id  UUID NOT NULL REFERENCES products(id),
    variant_id  UUID REFERENCES product_variants(id),
    quantity    INT NOT NULL DEFAULT 1,
    coupon_code VARCHAR(50),                        -- NEW: applied promo code
    created_at  TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMP NOT NULL DEFAULT NOW(),   -- NEW
    UNIQUE (user_id, product_id, variant_id)
);

CREATE TABLE orders (
    id                      UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                 UUID NOT NULL REFERENCES users(id),
    shipping_address_id     UUID REFERENCES shipping_addresses(id), -- NEW: FK
    coupon_id               UUID REFERENCES coupons(id),            -- NEW
    subtotal                DECIMAL(15,2) NOT NULL,                 -- NEW: before discounts
    discount_amount         DECIMAL(15,2) NOT NULL DEFAULT 0,       -- NEW
    total_amount            DECIMAL(15,2) NOT NULL,
    currency                CHAR(3) NOT NULL DEFAULT 'BIF',         -- NEW
    final_delivery_method_id UUID REFERENCES delivery_methods(id),
    status                  VARCHAR(20) NOT NULL DEFAULT 'pending'
                            CHECK (status IN ('pending','confirmed','cancelled','completed')),
    created_at              TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at              TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_orders_user ON orders(user_id, created_at DESC);

CREATE TABLE order_items (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL REFERENCES orders(id),
    product_id      UUID NOT NULL REFERENCES products(id),
    variant_id      UUID REFERENCES product_variants(id),
    shop_id         UUID NOT NULL REFERENCES shops(id),  -- NEW: denormalized
    quantity        INT NOT NULL,
    unit_price      DECIMAL(15,2) NOT NULL,              -- CHANGED: was just "price"
    discount_amount DECIMAL(15,2) NOT NULL DEFAULT 0,    -- NEW
    total_price     DECIMAL(15,2) NOT NULL
);
CREATE INDEX idx_order_items_order ON order_items(order_id);
CREATE INDEX idx_order_items_shop ON order_items(shop_id);

CREATE TABLE order_products (
    id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id         UUID NOT NULL REFERENCES orders(id),
    order_item_id    UUID NOT NULL REFERENCES order_items(id), -- NEW: critical FK fix
    product_id       UUID NOT NULL REFERENCES products(id),
    shop_id          UUID NOT NULL REFERENCES shops(id),
    shipment_id      UUID,                                     -- FK added below (circular)
    status           VARCHAR(20) NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','packed','in_transit','delivered','returned'))
);

CREATE TABLE returns (                                          -- NEW TABLE
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL REFERENCES orders(id),
    order_item_id   UUID NOT NULL REFERENCES order_items(id),
    user_id         UUID NOT NULL REFERENCES users(id),
    reason          VARCHAR(50) NOT NULL
                    CHECK (reason IN ('damaged','wrong_item','not_as_described','other')),
    reason_detail   TEXT,
    status          VARCHAR(20) NOT NULL DEFAULT 'requested'
                    CHECK (status IN ('requested','approved','rejected','refunded')),
    refund_amount   DECIMAL(15,2),
    refund_method   VARCHAR(20) CHECK (refund_method IN ('original','wallet','credit')),
    resolved_at     TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE disputes (                                         -- NEW TABLE
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    order_id        UUID NOT NULL REFERENCES orders(id),
    raised_by       UUID NOT NULL REFERENCES users(id),
    against_user_id UUID NOT NULL REFERENCES users(id),
    type            VARCHAR(30) NOT NULL
                    CHECK (type IN ('non_delivery','fraud','quality','other')),
    description     TEXT NOT NULL,
    status          VARCHAR(20) NOT NULL DEFAULT 'open'
                    CHECK (status IN ('open','escalated','resolved','closed')),
    resolved_by     UUID REFERENCES users(id),
    resolution_note TEXT,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ════════════════════════════════════════════════════════════
-- DOMAIN 4: PAYMENTS & FINANCE
-- ════════════════════════════════════════════════════════════

CREATE TABLE payments (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL REFERENCES users(id),
    order_id            UUID NOT NULL UNIQUE REFERENCES orders(id),
    amount              DECIMAL(15,2) NOT NULL,
    currency            CHAR(3) NOT NULL DEFAULT 'BIF',         -- NEW
    method              VARCHAR(30) NOT NULL
                        CHECK (method IN ('mobile_money','card','cash','wallet')),
    provider            VARCHAR(100),                           -- NEW: e.g. Lumicash
    status              VARCHAR(20) NOT NULL DEFAULT 'pending'
                        CHECK (status IN ('pending','paid','failed','refunded')),
    external_reference  VARCHAR(255),
    paid_at             TIMESTAMP,                              -- NEW
    created_at          TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE transactions (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id      UUID NOT NULL REFERENCES payments(id),
    order_item_id   UUID NOT NULL REFERENCES order_items(id),  -- NEW: precise split
    shop_id         UUID NOT NULL REFERENCES shops(id),
    gross_amount    DECIMAL(15,2) NOT NULL,                    -- NEW
    commission_rate DECIMAL(5,4) NOT NULL,                     -- NEW: rate at sale time
    commission      DECIMAL(15,2) NOT NULL,
    net_amount      DECIMAL(15,2) NOT NULL,                    -- NEW: gross - commission
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','available','paid_out')),
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE seller_payouts (                                   -- NEW TABLE
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    seller_id       UUID NOT NULL REFERENCES sellers(id),
    batch_reference VARCHAR(100) NOT NULL UNIQUE,
    amount          DECIMAL(15,2) NOT NULL,
    currency        CHAR(3) NOT NULL DEFAULT 'BIF',
    method          VARCHAR(30) NOT NULL
                    CHECK (method IN ('bank_transfer','mobile_money')),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','processing','paid','failed')),
    period_from     DATE NOT NULL,
    period_to       DATE NOT NULL,
    paid_at         TIMESTAMP,
    created_at      TIMESTAMP NOT NULL DEFAULT NOW()
);

-- ════════════════════════════════════════════════════════════
-- DOMAIN 5: LOGISTICS
-- ════════════════════════════════════════════════════════════

CREATE TABLE shipping_rules (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    from_region_id      UUID NOT NULL REFERENCES regions(id),
    to_region_id        UUID NOT NULL REFERENCES regions(id),
    delivery_method_id  UUID NOT NULL REFERENCES delivery_methods(id),
    price               DECIMAL(15,2) NOT NULL,
    estimated_days      INT,                                    -- NEW
    currency            CHAR(3) NOT NULL DEFAULT 'BIF',        -- NEW
    is_active           BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (from_region_id, to_region_id, delivery_method_id)
);

CREATE TABLE hub_locations (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    region_id   UUID NOT NULL REFERENCES regions(id),
    address     TEXT,
    phone       VARCHAR(30),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE,                  -- NEW
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);

CREATE TABLE pickup_points (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        VARCHAR(200) NOT NULL,
    region_id   UUID NOT NULL REFERENCES regions(id),
    address     TEXT,
    phone       VARCHAR(30),
    type        VARCHAR(20) CHECK (type IN ('shop','partner','locker')),
    is_active   BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE delivery_agents (                                  -- CHANGED: merged with driver role
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id             UUID NOT NULL UNIQUE REFERENCES users(id),  -- role must = 'driver'
    vehicle_type        VARCHAR(20) CHECK (vehicle_type IN ('motorcycle','bicycle','car','van')),
    license_plate       VARCHAR(30),                            -- NEW
    hub_id              UUID REFERENCES hub_locations(id),     -- NEW: home base hub
    status              VARCHAR(20) NOT NULL DEFAULT 'offline'
                        CHECK (status IN ('available','on_delivery','offline')),
    current_latitude    DECIMAL(10,7),
    current_longitude   DECIMAL(10,7),
    location_updated_at TIMESTAMP                              -- NEW
);

CREATE TABLE dukaconnect_shipments (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    hub_from_id     UUID NOT NULL REFERENCES hub_locations(id),
    hub_to_id       UUID NOT NULL REFERENCES hub_locations(id),
    driver_id       UUID NOT NULL REFERENCES delivery_agents(id),
    status          VARCHAR(20) NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','in_transit','delivered','failed')),
    departure_time  TIMESTAMP,
    arrival_time    TIMESTAMP,
    notes           TEXT                                       -- NEW
);

-- Now add the FK from order_products → dukaconnect_shipments (forward ref resolved)
ALTER TABLE order_products
    ADD CONSTRAINT fk_order_products_shipment
    FOREIGN KEY (shipment_id) REFERENCES dukaconnect_shipments(id);

CREATE TABLE shipment_items (
    id                  UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id         UUID NOT NULL REFERENCES dukaconnect_shipments(id),
    order_product_id    UUID NOT NULL REFERENCES order_products(id),
    status              VARCHAR(20) NOT NULL DEFAULT 'packed'
                        CHECK (status IN ('packed','in_transit','delivered','lost')),
    UNIQUE (shipment_id, order_product_id)
);

CREATE TABLE shipment_tracking (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    shipment_id     UUID NOT NULL REFERENCES dukaconnect_shipments(id),
    status          VARCHAR(100) NOT NULL,
    latitude        DECIMAL(10,7),
    longitude       DECIMAL(10,7),
    recorded_by     UUID REFERENCES users(id),                -- NEW: driver or system
    timestamp       TIMESTAMP NOT NULL DEFAULT NOW()
    -- NOTE: append-only. Never UPDATE or DELETE rows here.
);
CREATE INDEX idx_tracking_shipment ON shipment_tracking(shipment_id, timestamp DESC);

-- ════════════════════════════════════════════════════════════
-- DOMAIN 6: SOCIAL & COMMUNICATION
-- ════════════════════════════════════════════════════════════

CREATE TABLE reviews (
    id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id              UUID NOT NULL REFERENCES users(id),
    review_type          VARCHAR(10) NOT NULL CHECK (review_type IN ('product','shop')), -- NEW
    target_id            UUID NOT NULL,           -- NEW: product_id or shop_id
    order_id             UUID REFERENCES orders(id), -- NEW: verify purchase
    rating               SMALLINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment              TEXT,
    is_verified_purchase BOOLEAN NOT NULL DEFAULT FALSE, -- NEW: auto-set from order_id
    created_at           TIMESTAMP NOT NULL DEFAULT NOW()
    -- OLD: product_id + shop_id dual nullable columns removed
);
CREATE INDEX idx_reviews_target ON reviews(review_type, target_id);

CREATE TABLE messages (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id   UUID NOT NULL,                    -- NEW: groups a conversation
    sender_id   UUID NOT NULL REFERENCES users(id),
    receiver_id UUID NOT NULL REFERENCES users(id),
    message     TEXT NOT NULL,
    status      VARCHAR(20) NOT NULL DEFAULT 'sent'
                CHECK (status IN ('sent','delivered','read')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_messages_thread ON messages(thread_id, created_at);

CREATE TABLE notifications (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id     UUID NOT NULL REFERENCES users(id),
    type        VARCHAR(60) NOT NULL,
    title       VARCHAR(200),                     -- NEW
    message     TEXT NOT NULL,
    entity_type VARCHAR(50),                      -- NEW: order | shipment | etc.
    entity_id   UUID,                             -- NEW: deep-link target
    status      VARCHAR(20) NOT NULL DEFAULT 'unread'
                CHECK (status IN ('unread','read','dismissed')),
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
);
CREATE INDEX idx_notifications_user ON notifications(user_id, status);

-- ════════════════════════════════════════════════════════════
-- DOMAIN 7: PLATFORM & ADMIN
-- ════════════════════════════════════════════════════════════

CREATE TABLE admin_logs (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    admin_id    UUID NOT NULL REFERENCES users(id),
    action      VARCHAR(100) NOT NULL,
    table_name  VARCHAR(100) NOT NULL,
    record_id   UUID NOT NULL,
    before_data JSONB,                            -- NEW: snapshot before change
    after_data  JSONB,                            -- NEW: snapshot after change
    ip_address  INET,                             -- NEW
    created_at  TIMESTAMP NOT NULL DEFAULT NOW()
    -- NOTE: never UPDATE or DELETE rows in this table
);

CREATE TABLE analytics_events (                   -- CHANGED: replaces flat metric table
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    event_type  VARCHAR(50) NOT NULL,             -- view | add_to_cart | purchase | search
    entity_type VARCHAR(50),                      -- product | shop | category
    entity_id   UUID,
    user_id     UUID REFERENCES users(id),        -- nullable (anonymous sessions)
    region_id   UUID REFERENCES regions(id),
    session_id  VARCHAR(100),                     -- NEW
    metadata    JSONB,                            -- NEW: flexible extra dimensions
    occurred_at TIMESTAMP NOT NULL DEFAULT NOW()  -- partition key
) PARTITION BY RANGE (occurred_at);

-- Monthly partitions (create as needed):
-- CREATE TABLE analytics_events_2025_01 PARTITION OF analytics_events
--     FOR VALUES FROM ('2025-01-01') TO ('2025-02-01');

CREATE INDEX idx_analytics_type ON analytics_events(event_type, occurred_at DESC);
CREATE INDEX idx_analytics_entity ON analytics_events(entity_type, entity_id, occurred_at DESC);

-- ════════════════════════════════════════════════════════════
-- SUMMARY OF CHANGES
-- ════════════════════════════════════════════════════════════
/*
ADDED TABLES (6):
  coupons           — user-redeemable promo codes
  product_tags      — faceted search / discovery
  returns           — return request & refund lifecycle
  disputes          — escalated buyer-seller conflicts
  seller_payouts    — disbursement records to sellers
  analytics_events  — replaces flat (metric, value, date) table

KEY STRUCTURAL FIXES:
  order_products.order_item_id FK — closes the logical gap between
    financial records and logistics records (critical integrity fix)
  reviews — review_type + target_id replaces dual nullable product_id/shop_id
  delivery_agents — role=driver on users IS the driver; delivery_agents
    is the profile extension (same pattern as sellers)
  transactions — added order_item_id FK for precise per-item commission splits

FIELDS ADDED ACROSS TABLES:
  currency (char 3)     — on products, orders, payments, shipping_rules, seller_payouts
  deleted_at            — on users, shops, products, product_variants (soft delete)
  updated_by            — on users (audit trail)
  slug                  — on shops, categories, products (URL-friendly)
  condition             — on products (new/used/refurbished)
  is_active             — on discounts, hub_locations
  before_data/after_data — on admin_logs (full change snapshot)
  thread_id             — on messages (conversation grouping)
  entity_type/entity_id — on notifications (deep-link support)
  provider              — on payments (Lumicash, Ecocash, etc.)
  estimated_days        — on shipping_rules
  license_plate, hub_id — on delivery_agents
  location_updated_at   — on delivery_agents

PERFORMANCE INDEXES ADDED:
  products(shop_id, status), products name trigram (pg_trgm)
  order_items(order_id), order_items(shop_id)
  orders(user_id, created_at)
  shipment_tracking(shipment_id, timestamp)
  reviews(review_type, target_id)
  messages(thread_id, created_at)
  notifications(user_id, status)
  coupons(code)
  product_tags(tag)
  analytics_events — partitioned by month
*/

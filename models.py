from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Index, CheckConstraint, text, UniqueConstraint
from sqlalchemy.dialects.postgresql import TSVECTOR
from flask_dance.consumer.storage.sqla import OAuthConsumerMixin
from flask_login import UserMixin

db = SQLAlchemy()

# Multi-user system with Replit Auth integration
class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.String, primary_key=True)
    email = db.Column(db.String, unique=True, nullable=True)
    first_name = db.Column(db.String, nullable=True)
    last_name = db.Column(db.String, nullable=True)
    profile_image_url = db.Column(db.String, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime,
                           default=datetime.now,
                           onupdate=datetime.now)
    
    # Relationship to content
    content_items = db.relationship('Content', backref='user', lazy=True)

# OAuth table for Replit Auth
class OAuth(OAuthConsumerMixin, db.Model):
    user_id = db.Column(db.String, db.ForeignKey(User.id))
    browser_session_key = db.Column(db.String, nullable=False)
    user = db.relationship(User)

    __table_args__ = (UniqueConstraint(
        'user_id',
        'browser_session_key',
        'provider',
        name='uq_user_browser_session_key_provider',
    ),)

class Content(db.Model):
    """Content model for storing dynamic content with images"""
    __tablename__ = 'content'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(100), nullable=False, index=True)
    status = db.Column(db.String(50), nullable=False, index=True)
    author = db.Column(db.String(100), nullable=False, index=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False, index=True)

    tags = db.Column(db.Text)  # Store tags as comma-separated string
    image = db.Column(db.String(255))  # Store image filename
    user_type = db.Column(db.String(20), default='mixed', index=True)  # tech, business, mixed
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    search_vector = db.Column(TSVECTOR)  # Full-text search vector
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("LENGTH(title) >= 1", name='content_title_length_check'),
        CheckConstraint("LENGTH(content) >= 1", name='content_body_length_check'),
        CheckConstraint("status IN ('Draft', 'Published', 'Archived')", name='content_status_check'),
        CheckConstraint("user_type IN ('tech', 'business', 'mixed')", name='content_user_type_check'),
        Index('idx_content_search', 'search_vector', postgresql_using='gin'),
        Index('idx_content_created_status', 'created_at', 'status'),
        Index('idx_content_category_status', 'category', 'status'),
        Index('idx_content_user_type', 'user_type'),
    )
    
    def __init__(self, title, content, category, status, author, user_id, image=None):
        self.title = title
        self.content = content
        self.category = category
        self.status = status
        self.author = author
        self.user_id = user_id
        self.image = image
    
    def __repr__(self):
        return f'<Content {self.title}>'
    
    def get_tags_list(self):
        """Return tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',') if tag.strip()]
        return []
    
    def set_tags_list(self, tags_list):
        """Set tags from a list"""
        if tags_list:
            self.tags = ', '.join(tags_list)
        else:
            self.tags = ''
    
    def to_dict(self):
        """Convert content to dictionary for compatibility with existing templates"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'status': self.status,
            'author': self.author,
            'tags': self.get_tags_list(),
            'image': self.image,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }


class UserInteraction(db.Model):
    """Track user interactions for collaborative filtering"""
    __tablename__ = 'user_interactions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), nullable=False, index=True)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=False, index=True)
    interaction_type = db.Column(db.String(50), nullable=False, index=True)
    interaction_score = db.Column(db.Float, default=1.0)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    
    # Relationship
    content = db.relationship('Content', backref=db.backref('interactions', lazy=True, cascade='all, delete-orphan'))
    
    # Database constraints and indexes
    __table_args__ = (
        CheckConstraint("interaction_score >= 0", name='interaction_score_positive_check'),
        CheckConstraint("interaction_type IN ('view', 'edit', 'like', 'share', 'delete')", name='interaction_type_check'),
        Index('idx_user_content', 'user_id', 'content_id'),
        Index('idx_user_timestamp', 'user_id', 'timestamp'),
        Index('idx_content_type_timestamp', 'content_id', 'interaction_type', 'timestamp'),
    )
    
    def __init__(self, user_id, content_id, interaction_type, interaction_score=1.0):
        self.user_id = user_id
        self.content_id = content_id
        self.interaction_type = interaction_type
        self.interaction_score = interaction_score
    
    def __repr__(self):
        return f'<UserInteraction {self.user_id} -> {self.content_id} ({self.interaction_type})>'

class File(db.Model):
    """File attachment model for storing uploaded files"""
    __tablename__ = 'files'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, document, video, audio, archive, other
    file_extension = db.Column(db.String(10), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # in bytes
    content_id = db.Column(db.Integer, db.ForeignKey('content.id', ondelete='CASCADE'), nullable=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    content = db.relationship('Content', backref=db.backref('files', lazy=True, cascade='all, delete-orphan'))
    user = db.relationship('User', backref=db.backref('files', lazy=True))
    
    # Database constraints and indexes
    __table_args__ = (
        CheckConstraint("file_size > 0", name='file_size_positive_check'),
        CheckConstraint("file_type IN ('image', 'document', 'video', 'audio', 'archive', 'other')", name='file_type_check'),
        Index('idx_file_type', 'file_type'),
        Index('idx_file_user', 'user_id'),
        Index('idx_file_content', 'content_id'),
    )
    
    def __init__(self, filename, original_filename, file_type, file_extension, file_size, user_id, content_id=None):
        self.filename = filename
        self.original_filename = original_filename
        self.file_type = file_type
        self.file_extension = file_extension
        self.file_size = file_size
        self.user_id = user_id
        self.content_id = content_id
    
    def __repr__(self):
        return f'<File {self.original_filename}>'
    
    def get_file_size_formatted(self):
        """Return human-readable file size"""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        elif self.file_size < 1024 * 1024 * 1024:
            return f"{self.file_size / (1024 * 1024):.1f} MB"
        else:
            return f"{self.file_size / (1024 * 1024 * 1024):.1f} GB"
    
    def get_file_icon(self):
        """Return appropriate FontAwesome icon based on file type"""
        icon_map = {
            'image': 'fas fa-camera-retro text-info',
            'document': 'fas fa-file-text text-primary',
            'video': 'fas fa-play-circle text-danger',
            'audio': 'fas fa-headphones text-success',
            'archive': 'fas fa-archive text-warning',
            'other': 'fas fa-file text-muted'
        }
        return icon_map.get(self.file_type, 'fas fa-file text-muted')
    
    def to_dict(self):
        """Convert file to dictionary for template use"""
        return {
            'id': self.id,
            'filename': self.filename,
            'original_filename': self.original_filename,
            'file_type': self.file_type,
            'file_extension': self.file_extension,
            'file_size': self.file_size,
            'file_size_formatted': self.get_file_size_formatted(),
            'file_icon': self.get_file_icon(),
            'content_id': self.content_id,
            'user_id': self.user_id,
            'created_at': self.created_at
        }

# Story Model for Limited-Time Dynamic Content (removed duplicate definition)

# Ecommerce Models

class Product(db.Model):
    """Product model for ecommerce functionality"""
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stripe_price_id = db.Column(db.String(100), nullable=True)  # Stripe Price ID
    image_url = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(100), nullable=False, index=True)
    stock_quantity = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_digital = db.Column(db.Boolean, nullable=False, default=False)
    is_new_arrival = db.Column(db.Boolean, nullable=False, default=True)
    featured_until = db.Column(db.DateTime, nullable=True)  # For time-limited new arrival status
    
    # Seasonal product fields
    is_seasonal = db.Column(db.Boolean, nullable=False, default=False)
    season_type = db.Column(db.String(50), nullable=True)  # spring, summer, fall, winter, holiday, valentine, etc.
    seasonal_start = db.Column(db.DateTime, nullable=True)  # When seasonal availability starts
    seasonal_end = db.Column(db.DateTime, nullable=True)  # When seasonal availability ends
    seasonal_year = db.Column(db.Integer, nullable=True)  # For year-specific seasonal items
    
    # Seller information
    seller_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    seller = db.relationship('User', backref=db.backref('products', lazy=True))
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("price > 0", name='price_positive_check'),
        CheckConstraint("stock_quantity >= 0", name='stock_positive_check'),
        Index('idx_product_category', 'category'),
        Index('idx_product_seller', 'seller_id'),
        Index('idx_product_active', 'is_active'),
    )
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    @property
    def is_still_new(self):
        """Check if product is still considered a new arrival"""
        if not self.is_new_arrival:
            return False
        if self.featured_until and datetime.utcnow() > self.featured_until:
            return False
        # Default: products are new for 30 days
        if not self.featured_until:
            return (datetime.utcnow() - self.created_at).days <= 30
        return True
    
    @property
    def days_since_created(self):
        """Get number of days since product was created"""
        return (datetime.utcnow() - self.created_at).days
    
    @property
    def is_currently_seasonal(self):
        """Check if seasonal product is currently available"""
        if not self.is_seasonal:
            return True  # Non-seasonal products are always available
        
        now = datetime.utcnow()
        
        # Check if within seasonal date range
        if self.seasonal_start and self.seasonal_end:
            # For same-year ranges
            if self.seasonal_start.year == self.seasonal_end.year:
                return self.seasonal_start <= now <= self.seasonal_end
            # For cross-year ranges (e.g., winter from Dec to Feb)
            else:
                return now >= self.seasonal_start or now <= self.seasonal_end
        
        # If no specific dates, check by season type and current month
        if self.season_type:
            current_month = now.month
            seasonal_months = self._get_season_months(self.season_type)
            return current_month in seasonal_months
        
        return True  # Default to available if no restrictions
    
    def _get_season_months(self, season_type):
        """Get months for different season types"""
        season_map = {
            'spring': [3, 4, 5],      # March, April, May
            'summer': [6, 7, 8],      # June, July, August
            'fall': [9, 10, 11],      # September, October, November
            'autumn': [9, 10, 11],    # Same as fall
            'winter': [12, 1, 2],     # December, January, February
            'holiday': [11, 12, 1],   # November, December, January
            'christmas': [11, 12],    # November, December
            'valentine': [1, 2],      # January, February
            'easter': [3, 4],         # March, April
            'halloween': [10],        # October
            'thanksgiving': [11],     # November
            'back_to_school': [7, 8, 9], # July, August, September
            'new_year': [12, 1],      # December, January
        }
        return season_map.get(season_type.lower(), [1,2,3,4,5,6,7,8,9,10,11,12])
    
    @property
    def seasonal_status(self):
        """Get seasonal status for display"""
        if not self.is_seasonal:
            return None
        
        if self.is_currently_seasonal:
            return 'available'
        else:
            return 'out_of_season'
    
    @property
    def days_until_seasonal(self):
        """Get days until seasonal availability starts"""
        if not self.is_seasonal or self.is_currently_seasonal:
            return None
        
        now = datetime.utcnow()
        if self.seasonal_start and self.seasonal_start > now:
            return (self.seasonal_start - now).days
        
        return None
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'price': float(self.price),
            'image_url': self.image_url,
            'category': self.category,
            'stock_quantity': self.stock_quantity,
            'is_active': self.is_active,
            'is_digital': self.is_digital,
            'is_new_arrival': self.is_new_arrival,
            'is_still_new': self.is_still_new,
            'days_since_created': self.days_since_created,
            'seller_id': self.seller_id,
            'created_at': self.created_at,
            'is_seasonal': self.is_seasonal,
            'season_type': self.season_type,
            'seasonal_start': self.seasonal_start,
            'seasonal_end': self.seasonal_end,
            'seasonal_year': self.seasonal_year,
            'is_currently_seasonal': self.is_currently_seasonal,
            'seasonal_status': self.seasonal_status,
            'days_until_seasonal': self.days_until_seasonal
        }

# User Views System for Analytics and Recommendations

class ProductView(db.Model):
    """Track product views for analytics and recommendations"""
    __tablename__ = 'product_views'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # View details
    session_id = db.Column(db.String(100), nullable=True)  # Browser session tracking
    ip_address = db.Column(db.String(45), nullable=True)   # IPv4/IPv6 support
    user_agent = db.Column(db.String(500), nullable=True)  # Browser/device info
    referrer = db.Column(db.String(500), nullable=True)    # Where they came from
    
    # Engagement metrics
    view_duration = db.Column(db.Integer, default=0)       # Seconds spent viewing
    scroll_depth = db.Column(db.Float, default=0.0)       # Percentage scrolled
    clicked_images = db.Column(db.Boolean, default=False)  # Engaged with product images
    viewed_reviews = db.Column(db.Boolean, default=False)  # Scrolled to reviews section
    
    # Timestamps
    viewed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='product_views')
    product = db.relationship('Product', backref='views')
    
    def __repr__(self):
        return f'<ProductView {self.user_id} -> {self.product_id} at {self.viewed_at}>'

class ContentView(db.Model):
    """Track content views for analytics"""
    __tablename__ = 'content_views'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=False)
    
    # View details
    session_id = db.Column(db.String(100), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    referrer = db.Column(db.String(500), nullable=True)
    
    # Engagement metrics
    view_duration = db.Column(db.Integer, default=0)
    scroll_depth = db.Column(db.Float, default=0.0)
    read_percentage = db.Column(db.Float, default=0.0)  # Estimated reading progress
    
    # Timestamps
    viewed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='content_views')
    content = db.relationship('Content', backref='views')

class UserSession(db.Model):
    """Track user session data for analytics"""
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False, unique=True)
    
    # Session details
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    device_type = db.Column(db.String(50), nullable=True)  # desktop, mobile, tablet
    browser = db.Column(db.String(100), nullable=True)
    os = db.Column(db.String(100), nullable=True)
    
    # Session metrics
    page_views = db.Column(db.Integer, default=0)
    total_duration = db.Column(db.Integer, default=0)  # Total session time in seconds
    products_viewed = db.Column(db.Integer, default=0)
    cart_additions = db.Column(db.Integer, default=0)
    purchases_made = db.Column(db.Integer, default=0)
    
    # Timestamps
    started_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    last_activity = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    ended_at = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    user = db.relationship('User', backref='sessions')
    
    @property
    def is_active(self):
        """Check if session is still active (last activity within 30 minutes)"""
        if self.ended_at:
            return False
        return (datetime.utcnow() - self.last_activity).seconds < 1800  # 30 minutes
    
    @property
    def duration_minutes(self):
        """Get session duration in minutes"""
        end_time = self.ended_at or datetime.utcnow()
        return (end_time - self.started_at).seconds // 60

class ViewAnalytics(db.Model):
    """Daily aggregated view analytics"""
    __tablename__ = 'view_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    
    # Product analytics
    total_product_views = db.Column(db.Integer, default=0)
    unique_product_viewers = db.Column(db.Integer, default=0)
    avg_view_duration = db.Column(db.Float, default=0.0)
    top_viewed_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True)
    
    # Content analytics
    total_content_views = db.Column(db.Integer, default=0)
    unique_content_viewers = db.Column(db.Integer, default=0)
    avg_read_percentage = db.Column(db.Float, default=0.0)
    top_viewed_content_id = db.Column(db.Integer, db.ForeignKey('content.id'), nullable=True)
    
    # User analytics
    total_users = db.Column(db.Integer, default=0)
    new_users = db.Column(db.Integer, default=0)
    returning_users = db.Column(db.Integer, default=0)
    avg_session_duration = db.Column(db.Float, default=0.0)
    
    # Device analytics
    desktop_views = db.Column(db.Integer, default=0)
    mobile_views = db.Column(db.Integer, default=0)
    tablet_views = db.Column(db.Integer, default=0)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    top_product = db.relationship('Product', foreign_keys=[top_viewed_product_id])
    top_content = db.relationship('Content', foreign_keys=[top_viewed_content_id])

class CartItem(db.Model):
    """Shopping cart items"""
    __tablename__ = 'cart_items'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id', ondelete='CASCADE'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    added_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    product = db.relationship('Product', backref=db.backref('cart_items', lazy=True))
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name='cart_quantity_positive_check'),
        UniqueConstraint('user_id', 'product_id', name='unique_user_product_cart'),
        Index('idx_cart_user', 'user_id'),
    )
    
    def __repr__(self):
        return f'<CartItem {self.product.name} x {self.quantity}>'
    
    def get_total_price(self):
        return float(self.product.price * self.quantity)

class Order(db.Model):
    """Customer orders"""
    __tablename__ = 'orders'
    
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(20), unique=True, nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    
    # Order details
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')  # pending, paid, shipped, delivered, cancelled
    
    # Payment information
    stripe_session_id = db.Column(db.String(200), nullable=True)
    stripe_payment_intent_id = db.Column(db.String(200), nullable=True)
    payment_status = db.Column(db.String(50), nullable=False, default='pending')
    
    # Shipping information
    shipping_name = db.Column(db.String(100), nullable=True)
    shipping_address = db.Column(db.Text, nullable=True)
    shipping_city = db.Column(db.String(100), nullable=True)
    shipping_state = db.Column(db.String(100), nullable=True)
    shipping_zip = db.Column(db.String(20), nullable=True)
    shipping_country = db.Column(db.String(100), nullable=True)
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('orders', lazy=True))
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("total_amount > 0", name='order_total_positive_check'),
        CheckConstraint("status IN ('pending', 'paid', 'shipped', 'delivered', 'cancelled')", name='order_status_check'),
        CheckConstraint("payment_status IN ('pending', 'paid', 'failed', 'refunded')", name='payment_status_check'),
        Index('idx_order_user', 'user_id'),
        Index('idx_order_status', 'status'),
        Index('idx_order_payment_status', 'payment_status'),
    )
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
    
    def generate_order_number(self):
        """Generate unique order number"""
        import random
        import string
        while True:
            order_number = 'ORD-' + ''.join(random.choices(string.digits, k=8))
            if not Order.query.filter_by(order_number=order_number).first():
                return order_number

class OrderItem(db.Model):
    """Items within an order"""
    __tablename__ = 'order_items'
    
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id', ondelete='CASCADE'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    
    # Store product details at time of purchase
    product_name = db.Column(db.String(200), nullable=False)
    product_price = db.Column(db.Numeric(10, 2), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    
    # Relationships
    order = db.relationship('Order', backref=db.backref('items', lazy=True, cascade='all, delete-orphan'))
    product = db.relationship('Product', backref=db.backref('order_items', lazy=True))
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("quantity > 0", name='order_item_quantity_positive_check'),
        CheckConstraint("product_price > 0", name='order_item_price_positive_check'),
        Index('idx_order_item_order', 'order_id'),
        Index('idx_order_item_product', 'product_id'),
    )
    
    def __repr__(self):
        return f'<OrderItem {self.product_name} x {self.quantity}>'
    
    def get_total_price(self):
        return float(self.product_price * self.quantity)


class Wishlist(db.Model):
    __tablename__ = 'wishlist'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    user = db.relationship('User', backref='wishlist_items')
    product = db.relationship('Product', backref='wishlist_items')
    
    __table_args__ = (db.UniqueConstraint('user_id', 'product_id', name='unique_user_product_wishlist'),)


class ProductReview(db.Model):
    __tablename__ = 'product_reviews'
    id = db.Column(db.Integer, primary_key=True)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    title = db.Column(db.String(200))
    review_text = db.Column(db.Text)
    verified_purchase = db.Column(db.Boolean, default=False)
    helpful_votes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    product = db.relationship('Product', backref='reviews')
    user = db.relationship('User', backref='reviews')
    
    __table_args__ = (db.UniqueConstraint('product_id', 'user_id', name='unique_product_user_review'),)


class Coupon(db.Model):
    __tablename__ = 'coupons'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    discount_type = db.Column(db.String(20), nullable=False)  # 'percentage' or 'fixed'
    discount_value = db.Column(db.Float, nullable=False)
    minimum_amount = db.Column(db.Float, default=0)
    maximum_discount = db.Column(db.Float)  # For percentage discounts
    usage_limit = db.Column(db.Integer)  # Total usage limit
    usage_count = db.Column(db.Integer, default=0)
    per_user_limit = db.Column(db.Integer, default=1)  # Usage limit per user
    starts_at = db.Column(db.DateTime, default=datetime.now)
    expires_at = db.Column(db.DateTime)
    is_active = db.Column(db.Boolean, default=True)
    created_by_id = db.Column(db.String, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    created_by = db.relationship('User', backref='created_coupons')
    
    @property
    def is_valid(self):
        """Check if coupon is currently valid"""
        now = datetime.now()
        if not self.is_active:
            return False
        if self.starts_at and now < self.starts_at:
            return False
        if self.expires_at and now > self.expires_at:
            return False
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return False
        return True
    
    def calculate_discount(self, amount):
        """Calculate discount amount for given order amount"""
        if not self.is_valid or amount < self.minimum_amount:
            return 0
        
        if self.discount_type == 'percentage':
            discount = amount * (self.discount_value / 100)
            if self.maximum_discount:
                discount = min(discount, self.maximum_discount)
            return discount
        elif self.discount_type == 'fixed':
            return min(self.discount_value, amount)
        
        return 0


class CouponUsage(db.Model):
    __tablename__ = 'coupon_usage'
    id = db.Column(db.Integer, primary_key=True)
    coupon_id = db.Column(db.Integer, db.ForeignKey('coupons.id'), nullable=False)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    discount_amount = db.Column(db.Float, nullable=False)
    used_at = db.Column(db.DateTime, default=datetime.now)
    
    coupon = db.relationship('Coupon', backref='usage_history')
    user = db.relationship('User', backref='coupon_usage')
    order = db.relationship('Order', backref='coupon_usage')

class UserPreference(db.Model):
    """User preferences for various features like recommendation wizard"""
    __tablename__ = 'user_preference'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    preference_type = db.Column(db.String(50), nullable=False)  # 'wizard', 'recommendations', etc.
    preferences = db.Column(db.JSON, nullable=False)  # Store JSON data
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    # Relationships
    user = db.relationship('User', backref='preferences')
    
    # Unique constraint for user and preference type
    __table_args__ = (db.UniqueConstraint('user_id', 'preference_type', name='uq_user_preference_type'),)

# Newsletter Subscription Model
class NewsletterSubscription(db.Model):
    """Newsletter subscription management for fashion inspiration"""
    __tablename__ = 'newsletter_subscriptions'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), nullable=False, unique=True, index=True)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=True, index=True)
    first_name = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    
    # Fashion preferences for personalization
    preferred_categories = db.Column(db.JSON)  # list of fashion categories
    style_preferences = db.Column(db.JSON)  # casual, formal, trendy, vintage, etc.
    size_range = db.Column(db.String(50), nullable=True)  # XS, S, M, L, XL, etc.
    budget_range = db.Column(db.String(50), nullable=True)  # budget, mid-range, luxury
    color_preferences = db.Column(db.JSON)  # preferred color palette
    
    # Newsletter settings
    frequency = db.Column(db.String(20), default='weekly')  # weekly, monthly
    last_sent = db.Column(db.DateTime, nullable=True)
    total_emails_sent = db.Column(db.Integer, default=0)
    
    # Engagement tracking
    open_count = db.Column(db.Integer, default=0)
    click_count = db.Column(db.Integer, default=0)
    last_opened = db.Column(db.DateTime, nullable=True)
    last_clicked = db.Column(db.DateTime, nullable=True)
    
    # Subscription management
    subscription_token = db.Column(db.String(255), unique=True, nullable=False, index=True)
    subscribed_at = db.Column(db.DateTime, default=datetime.now)
    unsubscribed_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)
    
    # Relationship to user
    user = db.relationship('User', backref='newsletter_subscription')

# Fashion Newsletter Content Model
class FashionNewsletter(db.Model):
    """Fashion newsletter content and campaigns"""
    __tablename__ = 'fashion_newsletters'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    subject_line = db.Column(db.String(255), nullable=False)
    content_html = db.Column(db.Text, nullable=False)
    content_text = db.Column(db.Text, nullable=True)
    
    # Newsletter metadata
    newsletter_type = db.Column(db.String(50), default='weekly_inspiration')  # weekly_inspiration, seasonal, special
    season = db.Column(db.String(20), nullable=True)  # spring, summer, fall, winter
    featured_categories = db.Column(db.JSON)  # featured fashion categories
    featured_products = db.Column(db.JSON)  # list of product IDs
    
    # Campaign tracking
    status = db.Column(db.String(20), default='draft')  # draft, scheduled, sent
    scheduled_at = db.Column(db.DateTime, nullable=True)
    sent_at = db.Column(db.DateTime, nullable=True)
    total_sent = db.Column(db.Integer, default=0)
    total_opened = db.Column(db.Integer, default=0)
    total_clicked = db.Column(db.Integer, default=0)
    
    created_at = db.Column(db.DateTime, default=datetime.now)
    created_by = db.Column(db.String, db.ForeignKey('users.id'), nullable=True)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

# Newsletter Analytics Model
class NewsletterAnalytics(db.Model):
    """Detailed analytics for newsletter campaigns"""
    __tablename__ = 'newsletter_analytics'
    
    id = db.Column(db.Integer, primary_key=True)
    newsletter_id = db.Column(db.Integer, db.ForeignKey('fashion_newsletters.id'), nullable=False, index=True)
    subscription_id = db.Column(db.Integer, db.ForeignKey('newsletter_subscriptions.id'), nullable=False, index=True)
    
    # Tracking events
    event_type = db.Column(db.String(20), nullable=False, index=True)  # sent, opened, clicked, unsubscribed
    event_data = db.Column(db.JSON)  # additional event data (clicked link, etc.)
    user_agent = db.Column(db.String(500), nullable=True)
    ip_address = db.Column(db.String(45), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.now, index=True)
    
    # Relationships
    newsletter = db.relationship('FashionNewsletter', backref='analytics')
    subscription = db.relationship('NewsletterSubscription', backref='analytics')

# Limited-Time Stories Model
class Story(db.Model):
    """Limited-time stories for dynamic content and announcements"""
    __tablename__ = 'stories'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    story_type = db.Column(db.String(50), nullable=False, index=True)  # general, product, event, news, promotion
    
    # Visual content
    image_url = db.Column(db.String(500), nullable=True)
    background_color = db.Column(db.String(7), default='#007bff')  # Hex color code
    text_color = db.Column(db.String(7), default='#ffffff')  # Hex color code
    
    # Time management
    expires_at = db.Column(db.DateTime, nullable=False, index=True)
    priority = db.Column(db.Integer, default=1, nullable=False, index=True)  # Higher priority shows first
    
    # Status and visibility
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
    is_featured = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # Product linkage (optional)
    linked_product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=True, index=True)
    
    # Author and ownership
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False, index=True)
    author_name = db.Column(db.String(100), nullable=False)
    
    # Engagement tracking
    view_count = db.Column(db.Integer, default=0, nullable=False)
    click_count = db.Column(db.Integer, default=0, nullable=False)
    like_count = db.Column(db.Integer, default=0, nullable=False)
    
    # Multilingual support
    title_ko = db.Column(db.String(200), nullable=True)  # Korean title
    content_ko = db.Column(db.Text, nullable=True)  # Korean content
    
    # Timestamps
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='stories')
    linked_product = db.relationship('Product', backref='linked_stories')
    
    # Database constraints
    __table_args__ = (
        CheckConstraint("story_type IN ('general', 'product', 'event', 'news', 'promotion')", name='story_type_check'),
        CheckConstraint("priority >= 1", name='story_priority_check'),
        CheckConstraint("expires_at > created_at", name='story_expiry_check'),
        Index('idx_story_active_expires', 'is_active', 'expires_at'),
        Index('idx_story_featured_priority', 'is_featured', 'priority'),
        Index('idx_story_type_active', 'story_type', 'is_active'),
    )
    
    def __repr__(self):
        return f'<Story {self.title}>'
    
    def is_expired(self):
        """Check if story has expired"""
        return datetime.utcnow() > self.expires_at
    
    def time_remaining(self):
        """Get time remaining until expiry"""
        if self.is_expired():
            return None
        return self.expires_at - datetime.utcnow()
    
    def time_remaining_hours(self):
        """Get time remaining in hours"""
        remaining = self.time_remaining()
        if remaining:
            return int(remaining.total_seconds() / 3600)
        return 0
    
    def get_localized_title(self, language='en'):
        """Get title in specified language"""
        if language == 'ko' and self.title_ko:
            return self.title_ko
        return self.title
    
    def get_localized_content(self, language='en'):
        """Get content in specified language"""
        if language == 'ko' and self.content_ko:
            return self.content_ko
        return self.content
    
    def increment_views(self):
        """Increment view count"""
        self.view_count += 1
        db.session.commit()
    
    def increment_clicks(self):
        """Increment click count"""
        self.click_count += 1
        db.session.commit()
    
    def increment_likes(self):
        """Increment like count"""
        self.like_count += 1
        db.session.commit()
    
    def to_dict(self):
        """Convert story to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'story_type': self.story_type,
            'image_url': self.image_url,
            'background_color': self.background_color,
            'text_color': self.text_color,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'priority': self.priority,
            'is_active': self.is_active,
            'is_featured': self.is_featured,
            'linked_product_id': self.linked_product_id,
            'author_name': self.author_name,
            'view_count': self.view_count,
            'click_count': self.click_count,
            'like_count': self.like_count,
            'time_remaining_hours': self.time_remaining_hours(),
            'is_expired': self.is_expired(),
            'created_at': self.created_at.isoformat(),
        }
    
    @classmethod
    def get_active_stories(cls, limit=10):
        """Get active, non-expired stories ordered by priority and creation time"""
        return cls.query.filter(
            cls.is_active == True,
            cls.expires_at > datetime.utcnow()
        ).order_by(
            cls.priority.desc(),
            cls.created_at.desc()
        ).limit(limit).all()
    
    def time_remaining_korean(self):
        """Get time remaining in Korean format"""
        remaining = self.time_remaining()
        if not remaining:
            return "만료됨"
        
        total_hours = int(remaining.total_seconds() / 3600)
        if total_hours >= 24:
            days = total_hours // 24
            return f"{days}일 남음"
        elif total_hours >= 1:
            return f"{total_hours}시간 남음"
        else:
            minutes = int(remaining.total_seconds() / 60)
            if minutes > 0:
                return f"{minutes}분 남음"
            else:
                return "곧 만료"

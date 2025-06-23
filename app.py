import os
import logging
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory, session, jsonify, make_response
from forms import ContentForm, EditContentForm, ProductForm, AddToCartForm, UpdateCartForm, CheckoutForm, NewsletterSubscriptionForm
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
import uuid
from models import db, Content, UserInteraction, User, OAuth, File, Product, CartItem, Order, OrderItem, Story, Wishlist, ProductReview, Coupon, CouponUsage, ProductView, ContentView, UserSession, ViewAnalytics, NewsletterSubscription, FashionNewsletter, NewsletterAnalytics
from database_utils import DatabaseManager, DatabaseHealthChecker
from sqlalchemy import func
import re
from collections import Counter, defaultdict
import numpy as np
from replit_auth import make_replit_blueprint, require_login
from flask_login import current_user
from flask_wtf.csrf import CSRFProtect
from recommendation_engine import recommendation_engine
from ai_relevance import ContentRelevanceAnalyzer
from user_type_classifier import UserTypeClassifier
from translations import get_translation, get_available_languages
from product_recommendation_engine import get_product_recommendations_for_user, get_similar_products
from newsletter_service import FashionNewsletterService
import stripe
import json



# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "default_secret_key_for_development")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # Fallback to SQLite for development
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///content.db'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration for file uploads
UPLOAD_FOLDER = 'static/uploads'
FILES_FOLDER = 'static/files'
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'}
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'rtf', 'odt'}
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'webm', 'avi', 'mov', 'wmv', 'flv'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a'}
ALLOWED_ARCHIVE_EXTENSIONS = {'zip', 'rar', '7z', 'tar', 'gz'}
ALLOWED_OTHER_EXTENSIONS = {'csv', 'xlsx', 'xls', 'ppt', 'pptx'}

ALL_ALLOWED_EXTENSIONS = (ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS | 
                         ALLOWED_VIDEO_EXTENSIONS | ALLOWED_AUDIO_EXTENSIONS |
                         ALLOWED_ARCHIVE_EXTENSIONS | ALLOWED_OTHER_EXTENSIONS)

MAX_CONTENT_LENGTH = 100 * 1024 * 1024  # 100MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['FILES_FOLDER'] = FILES_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Initialize database
db.init_app(app)

# Initialize CSRF Protection
csrf = CSRFProtect(app)

# Disable CSRF for specific endpoints that handle file uploads
@csrf.exempt
def disable_csrf_for_uploads():
    pass

# Exempt specific routes from CSRF protection
csrf.exempt(lambda: None)  # This will be applied to specific routes

# Exempt wizard API endpoints from CSRF
@csrf.exempt
def exempt_wizard_apis():
    pass

# Initialize Flask-Login
from flask_login import LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'replit_auth.login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

# Register authentication blueprint
app.register_blueprint(make_replit_blueprint(), url_prefix="/auth")

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

# Initialize newsletter service
newsletter_service = FashionNewsletterService()

# Get domain for Stripe success/cancel URLs
def get_domain():
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return os.environ.get('REPLIT_DEV_DOMAIN')
    else:
        domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
        return domains[0] if domains else 'localhost:5000'

# Session configuration for authentication and language
@app.before_request
def make_session_permanent():
    session.permanent = True
    # Set default language to Korean if not already set
    if 'language' not in session:
        session['language'] = 'ko'

# Application configuration and setup

# Create database tables
with app.app_context():
    db.create_all()



# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Helper functions for file handling
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALL_ALLOWED_EXTENSIONS

def get_file_type(extension):
    """Determine file type based on extension"""
    extension = extension.lower()
    if extension in ALLOWED_IMAGE_EXTENSIONS:
        return 'image'
    elif extension in ALLOWED_DOCUMENT_EXTENSIONS:
        return 'document'
    elif extension in ALLOWED_VIDEO_EXTENSIONS:
        return 'video'
    elif extension in ALLOWED_AUDIO_EXTENSIONS:
        return 'audio'
    elif extension in ALLOWED_ARCHIVE_EXTENSIONS:
        return 'archive'
    else:
        return 'other'

def save_uploaded_file(file, user_id, content_id=None, file_type='general'):
    """Save uploaded file and create database record"""
    if file and allowed_file(file.filename):
        original_filename = secure_filename(file.filename)
        name, ext = os.path.splitext(original_filename)
        extension = ext[1:].lower()  # Remove the dot
        
        # Generate unique filename
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        
        # Determine file type and storage location
        detected_file_type = get_file_type(extension)
        
        # Use different folders for images vs other files
        if detected_file_type == 'image':
            storage_folder = app.config['UPLOAD_FOLDER']
        else:
            storage_folder = app.config['FILES_FOLDER']
            os.makedirs(storage_folder, exist_ok=True)
        
        file_path = os.path.join(storage_folder, unique_filename)
        
        try:
            # Save file to disk
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            # Create database record
            file_record = File(
                filename=unique_filename,
                original_filename=original_filename,
                file_type=detected_file_type,
                file_extension=extension,
                file_size=file_size,
                user_id=user_id,
                content_id=content_id
            )
            
            db.session.add(file_record)
            db.session.commit()
            
            return file_record
            
        except Exception as e:
            # Clean up file if database operation fails
            if os.path.exists(file_path):
                os.remove(file_path)
            db.session.rollback()
            app.logger.error(f'Error saving file: {e}')
            return None
    return None

def save_image_file(file):
    """Legacy function for backward compatibility with image uploads"""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{name}_{uuid.uuid4().hex[:8]}{ext}"
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        return unique_filename
    return None



# Recommendation system functions
def extract_keywords(text, num_keywords=10):
    """Extract important keywords from text content"""
    # Remove HTML tags and special characters
    clean_text = re.sub(r'<[^>]+>', '', text.lower())
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', clean_text)
    
    # Common stop words to exclude
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
        'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did',
        'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those',
        'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them', 'my', 'your',
        'his', 'its', 'our', 'their', 'not', 'no', 'yes', 'if', 'when', 'where', 'why', 'how'
    }
    
    # Extract words and count frequency
    words = [word for word in clean_text.split() if len(word) > 3 and word not in stop_words]
    word_freq = Counter(words)
    
    return [word for word, _ in word_freq.most_common(num_keywords)]

def calculate_content_similarity(content1, content2):
    """Calculate similarity between two content items"""
    score = 0
    
    # Category match (high weight)
    if content1.category == content2.category:
        score += 0.4
    
    # Tag overlap (medium weight)
    tags1 = set(content1.get_tags_list())
    tags2 = set(content2.get_tags_list())
    if tags1 and tags2:
        tag_overlap = len(tags1.intersection(tags2)) / len(tags1.union(tags2))
        score += 0.3 * tag_overlap
    
    # Content keyword similarity (medium weight)
    keywords1 = set(extract_keywords(content1.content))
    keywords2 = set(extract_keywords(content2.content))
    if keywords1 and keywords2:
        keyword_overlap = len(keywords1.intersection(keywords2)) / len(keywords1.union(keywords2))
        score += 0.2 * keyword_overlap
    
    # Author match (low weight)
    if content1.author == content2.author:
        score += 0.1
    
    return score

def get_content_recommendations(content_id, limit=5):
    """Get recommended content based on similarity to given content"""
    current_content = Content.query.get(content_id)
    if not current_content:
        return []
    
    # Get all other published content
    other_content = Content.query.filter(
        Content.id != content_id,
        Content.status == 'Published'
    ).all()
    
    # Calculate similarity scores
    recommendations = []
    for content in other_content:
        similarity = calculate_content_similarity(current_content, content)
        if similarity > 0:
            recommendations.append({
                'content': content,
                'similarity': similarity,
                'score': similarity
            })
    
    # Sort by similarity and return top recommendations
    recommendations.sort(key=lambda x: x['similarity'], reverse=True)
    return recommendations[:limit]



def get_category_recommendations(category, exclude_id=None, limit=5):
    """Get popular content from the same category"""
    try:
        query = Content.query.filter(
            Content.category == category,
            Content.status == 'Published'
        )
        
        if exclude_id:
            query = query.filter(Content.id != exclude_id)
        
        return query.order_by(Content.updated_at.desc()).limit(limit).all()
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in get_category_recommendations: {e}")
        return []

def get_user_id():
    """Get or create user ID for session tracking"""
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    return session['user_id']

# ================================
# User Views Tracking System
# ================================

def get_session_id():
    """Get or create session ID for tracking"""
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())
    return session['session_id']

def get_device_type(user_agent):
    """Detect device type from user agent"""
    user_agent = user_agent.lower()
    if 'mobile' in user_agent or 'android' in user_agent or 'iphone' in user_agent:
        return 'mobile'
    elif 'tablet' in user_agent or 'ipad' in user_agent:
        return 'tablet'
    else:
        return 'desktop'

def get_browser_info(user_agent):
    """Extract browser information from user agent"""
    user_agent = user_agent.lower()
    if 'chrome' in user_agent:
        return 'Chrome'
    elif 'firefox' in user_agent:
        return 'Firefox'
    elif 'safari' in user_agent:
        return 'Safari'
    elif 'edge' in user_agent:
        return 'Edge'
    else:
        return 'Other'

def track_product_view(product_id, user_id=None, engagement_data=None):
    """Track product view with detailed analytics"""
    try:
        if not user_id:
            user_id = current_user.id if current_user.is_authenticated else get_user_id()
        
        session_id = get_session_id()
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', '')
        referrer = request.headers.get('Referer', '')
        
        # Create or update session
        user_session = UserSession.query.filter_by(session_id=session_id).first()
        if not user_session:
            user_session = UserSession()
            user_session.user_id = user_id
            user_session.session_id = session_id
            user_session.ip_address = ip_address
            user_session.user_agent = user_agent
            user_session.device_type = get_device_type(user_agent)
            user_session.browser = get_browser_info(user_agent)
            db.session.add(user_session)
        
        # Update session activity
        user_session.last_activity = datetime.utcnow()
        user_session.products_viewed = (user_session.products_viewed or 0) + 1
        user_session.page_views = (user_session.page_views or 0) + 1
        
        # Create product view record
        product_view = ProductView()
        product_view.user_id = user_id
        product_view.product_id = product_id
        product_view.session_id = session_id
        product_view.ip_address = ip_address
        product_view.user_agent = user_agent
        product_view.referrer = referrer
        
        # Add engagement data if provided
        if engagement_data:
            product_view.view_duration = engagement_data.get('duration', 0)
            product_view.scroll_depth = engagement_data.get('scroll_depth', 0.0)
            product_view.clicked_images = engagement_data.get('clicked_images', False)
            product_view.viewed_reviews = engagement_data.get('viewed_reviews', False)
        
        db.session.add(product_view)
        db.session.commit()
        
        return product_view.id
    except Exception as e:
        logging.error(f"Error tracking product view: {e}")
        db.session.rollback()
        return None

def track_content_view(content_id, user_id=None, engagement_data=None):
    """Track content view with detailed analytics"""
    try:
        if not user_id:
            user_id = current_user.id if current_user.is_authenticated else get_user_id()
        
        session_id = get_session_id()
        ip_address = request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR'))
        user_agent = request.headers.get('User-Agent', '')
        referrer = request.headers.get('Referer', '')
        
        # Create content view record
        content_view = ContentView()
        content_view.user_id = user_id
        content_view.content_id = content_id
        content_view.session_id = session_id
        content_view.ip_address = ip_address
        content_view.user_agent = user_agent
        content_view.referrer = referrer
        
        # Add engagement data if provided
        if engagement_data:
            content_view.view_duration = engagement_data.get('duration', 0)
            content_view.scroll_depth = engagement_data.get('scroll_depth', 0.0)
            content_view.read_percentage = engagement_data.get('read_percentage', 0.0)
        
        db.session.add(content_view)
        db.session.commit()
        
        return content_view.id
    except Exception as e:
        logging.error(f"Error tracking content view: {e}")
        db.session.rollback()
        return None

def get_product_view_stats(product_id, days=30):
    """Get view statistics for a product"""
    try:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        views = ProductView.query.filter(
            ProductView.product_id == product_id,
            ProductView.viewed_at >= start_date
        ).all()
        
        if not views:
            return {
                'total_views': 0,
                'unique_viewers': 0,
                'avg_duration': 0,
                'engagement_rate': 0
            }
        
        unique_viewers = len(set(view.user_id for view in views))
        total_duration = sum(view.view_duration for view in views if view.view_duration)
        avg_duration = total_duration / len(views) if views else 0
        engaged_views = len([v for v in views if v.scroll_depth > 0.5 or v.clicked_images])
        engagement_rate = (engaged_views / len(views)) * 100 if views else 0
        
        return {
            'total_views': len(views),
            'unique_viewers': unique_viewers,
            'avg_duration': round(avg_duration, 2),
            'engagement_rate': round(engagement_rate, 2)
        }
    except Exception as e:
        logging.error(f"Error getting product view stats: {e}")
        return {
            'total_views': 0,
            'unique_viewers': 0,
            'avg_duration': 0,
            'engagement_rate': 0
        }

def track_user_interaction(content_id, interaction_type, score=1.0):
    """Track user interaction for collaborative filtering"""
    try:
        user_id = get_user_id()
        interaction = UserInteraction(
            user_id=user_id,
            content_id=content_id,
            interaction_type=interaction_type,
            interaction_score=score
        )
        db.session.add(interaction)
        db.session.commit()
    except Exception as e:
        logging.error(f"Error tracking interaction: {e}")
        db.session.rollback()

def build_user_item_matrix():
    """Build user-item interaction matrix for collaborative filtering"""
    try:
        # Get all interactions from the last 30 days
        cutoff_date = datetime.utcnow() - timedelta(days=30)
        interactions = UserInteraction.query.filter(
            UserInteraction.timestamp >= cutoff_date
        ).all()
        
        # Build user-item matrix
        user_item_matrix = defaultdict(dict)
        users = set()
        items = set()
        
        for interaction in interactions:
            user_item_matrix[interaction.user_id][interaction.content_id] = interaction.interaction_score
            users.add(interaction.user_id)
            items.add(interaction.content_id)
        
        return user_item_matrix, list(users), list(items)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error building user-item matrix: {e}")
        return defaultdict(dict), [], []

def calculate_user_similarity(user1_items, user2_items):
    """Calculate cosine similarity between two users"""
    # Find common items
    common_items = set(user1_items.keys()) & set(user2_items.keys())
    
    if len(common_items) == 0:
        return 0
    
    # Calculate cosine similarity
    sum_squares1 = sum([user1_items[item] ** 2 for item in user1_items])
    sum_squares2 = sum([user2_items[item] ** 2 for item in user2_items])
    sum_products = sum([user1_items[item] * user2_items[item] for item in common_items])
    
    denominator = (sum_squares1 * sum_squares2) ** 0.5
    if denominator == 0:
        return 0
    
    return sum_products / denominator

def get_collaborative_filtering_recommendations(target_user_id, limit=5):
    """Get recommendations using collaborative filtering"""
    try:
        user_item_matrix, users, items = build_user_item_matrix()
        
        if target_user_id not in user_item_matrix:
            return []
        
        target_user_items = user_item_matrix[target_user_id]
        user_similarities = {}
        
        # Calculate similarity with other users
        for user_id in users:
            if user_id != target_user_id:
                similarity = calculate_user_similarity(target_user_items, user_item_matrix[user_id])
                if similarity > 0:
                    user_similarities[user_id] = similarity
        
        # Get recommendations based on similar users
        recommendations = defaultdict(float)
        total_similarity = sum(user_similarities.values())
        
        if total_similarity == 0:
            return []
        
        for user_id, similarity in user_similarities.items():
            weight = similarity / total_similarity
            for item_id, rating in user_item_matrix[user_id].items():
                if item_id not in target_user_items:  # Don't recommend already interacted items
                    recommendations[item_id] += weight * rating
        
        # Sort and get top recommendations
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)
        content_ids = [item_id for item_id, score in sorted_recommendations[:limit]]
        
        # Fetch content objects
        recommended_content = Content.query.filter(
            Content.id.in_(content_ids),
            Content.status == 'Published'
        ).all()
        
        # Return with scores
        result = []
        for content in recommended_content:
            score = next((score for item_id, score in sorted_recommendations if item_id == content.id), 0)
            result.append({
                'content': content,
                'cf_score': round(score, 3)
            })
        
        return result
        
    except Exception as e:
        logging.error(f"Error in collaborative filtering: {e}")
        return []

def get_hybrid_recommendations(content_id, limit=5):
    """Get hybrid recommendations combining content-based and collaborative filtering"""
    try:
        user_id = get_user_id()
        
        # Get content-based recommendations (existing function)
        content_based = get_content_recommendations(content_id, limit=limit//2 + 1)
        
        # Get collaborative filtering recommendations
        cf_based = get_collaborative_filtering_recommendations(user_id, limit=limit//2 + 1)
        
        # Combine and deduplicate
        all_recommendations = {}
        
        # Add content-based with weight
        for rec in content_based:
            all_recommendations[rec['content'].id] = {
                'content': rec['content'],
                'content_score': rec['similarity'],
                'cf_score': 0,
                'hybrid_score': rec['similarity'] * 0.6  # 60% weight for content-based
            }
        
        # Add CF-based with weight
        for rec in cf_based:
            if rec['content'].id in all_recommendations:
                all_recommendations[rec['content'].id]['cf_score'] = rec['cf_score']
                all_recommendations[rec['content'].id]['hybrid_score'] += rec['cf_score'] * 0.4  # 40% weight for CF
            else:
                all_recommendations[rec['content'].id] = {
                    'content': rec['content'],
                    'content_score': 0,
                    'cf_score': rec['cf_score'],
                    'hybrid_score': rec['cf_score'] * 0.4
                }
        
        # Sort by hybrid score
        sorted_recommendations = sorted(
            all_recommendations.values(),
            key=lambda x: x['hybrid_score'],
            reverse=True
        )
        
        return sorted_recommendations[:limit]
        
    except Exception as e:
        logging.error(f"Error in hybrid recommendations: {e}")
        return get_content_recommendations(content_id, limit)

# Content categories
CONTENT_CATEGORIES = [
    'Blog Post',
    'News Article', 
    'Product Description',
    'About Page',
    'Landing Page',
    'Documentation',
    'Other'
]

# Content status options
CONTENT_STATUS = [
    'Draft',
    'Published',
    'Archived'
]

@app.route('/')
def index():
    """Homepage displaying all content with filtering and limited-time stories"""
    # Get active stories for all users (public feature)
    try:
        from models import Story
        stories = Story.get_active_stories(limit=8)
    except Exception as e:
        app.logger.error(f"Error loading stories: {e}")
        stories = []
    
    # If user is not authenticated, show landing page with stories
    if not current_user.is_authenticated:
        # Get some public content for preview
        public_content = Content.query.filter_by(status='Published').order_by(Content.created_at.desc()).limit(6).all()
        return render_template('landing.html', 
                             public_content=[c.to_dict() for c in public_content],
                             stories=stories)
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    search_query = request.args.get('search', '').lower()
    
    # Build query with filters - show user's own content and published content from others
    query = Content.query.filter(
        db.or_(
            Content.user_id == current_user.id,  # User's own content
            Content.status == 'Published'        # Published content from others
        )
    )
    
    if category_filter:
        query = query.filter(Content.category == category_filter)
    if status_filter:
        query = query.filter(Content.status == status_filter)
    if search_query:
        query = query.filter(
            db.or_(
                Content.title.ilike(f'%{search_query}%'),
                Content.content.ilike(f'%{search_query}%')
            )
        )
    
    content_list = query.order_by(Content.updated_at.desc()).all()
    
    # Get personalized recommendations for authenticated users
    recommendations = []
    user_preferences = {}
    if current_user.is_authenticated:
        try:
            recommendations = recommendation_engine.get_hybrid_recommendations(current_user.id, num_recommendations=4)
            user_preferences = recommendation_engine.analyze_user_behavior(current_user.id)
        except Exception as e:
            app.logger.error(f'Error getting recommendations for homepage: {e}')
    
    # Get featured products for the banner
    featured_products = []
    total_products = 0
    new_arrivals_count = 0
    try:
        from models import Product
        # Get featured products (recent, highly rated, or new arrivals)
        featured_products = Product.query.filter_by(is_active=True).order_by(
            Product.created_at.desc()
        ).limit(6).all()
        
        # Get product statistics
        total_products = Product.query.filter_by(is_active=True).count()
        new_arrivals_count = Product.query.filter(
            Product.is_new_arrival == True,
            Product.is_active == True
        ).count()
    except Exception as e:
        app.logger.error(f'Error getting featured products: {e}')
    
    # Convert to dictionary format for template compatibility
    filtered_content = {content.id: content.to_dict() for content in content_list}
    

    
    # Get statistics for hero banner
    total_products = Product.query.filter(Product.is_active == True).count()
    total_content = Content.query.count()
    
    # Get new arrivals count for this week
    week_ago = datetime.utcnow() - timedelta(days=7)
    new_arrivals_count = Product.query.filter(
        Product.is_active == True,
        Product.is_new_arrival == True,
        Product.created_at >= week_ago
    ).count()
    
    # Get all active products for fashion banner
    products = Product.query.filter_by(is_active=True).order_by(Product.created_at.desc()).all()
    
    return render_template('index.html', 
                         content_store=filtered_content,
                         categories=CONTENT_CATEGORIES,
                         statuses=CONTENT_STATUS,
                         current_category=category_filter,
                         current_status=status_filter,
                         current_search=request.args.get('search', ''),
                         stories=stories,
                         recommendations=recommendations,
                         user_preferences=user_preferences,
                         featured_products=featured_products,
                         products=products,
                         total_products=total_products,
                         total_content=total_content,
                         new_arrivals_count=new_arrivals_count)

@app.route('/create', methods=['GET', 'POST'])
@require_login
def create_content():
    """Create new content"""
    form = ContentForm()
    form.category.choices = [(cat, cat) for cat in CONTENT_CATEGORIES]
    form.status.choices = [(status, status) for status in CONTENT_STATUS]
    
    if form.validate_on_submit():
        # Handle image upload
        image_filename = None
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                image_filename = save_image_file(file)
                if not image_filename:
                    flash('Invalid image file. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG files.', 'error')
                    return render_template('create_content.html', form=form)

        # Handle tags safely
        tags_data = form.tags.data or ''
        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()] if tags_data else []

        # Create new content in database
        new_content = Content(
            title=form.title.data,
            content=form.content.data,
            category=form.category.data,
            status=form.status.data,
            author=form.author.data,
            user_id=current_user.id if current_user.is_authenticated else 'anonymous',
            image=image_filename
        )
        new_content.set_tags_list(tags_list)
        
        try:
            db.session.add(new_content)
            db.session.commit()
            
            # Handle additional file uploads
            uploaded_files = []
            if 'files' in request.files:
                files = request.files.getlist('files')
                for file in files:
                    if file and file.filename != '':
                        file_record = save_uploaded_file(
                            file, 
                            current_user.id if current_user.is_authenticated else 'anonymous',
                            new_content.id
                        )
                        if file_record:
                            uploaded_files.append(file_record)
                        else:
                            flash(f'Failed to upload file: {file.filename}', 'warning')
            
            # Track user interaction for collaborative filtering
            track_user_interaction(new_content.id, 'create', score=2.0)
            
            if uploaded_files:
                flash(f'Content "{new_content.title}" created successfully with {len(uploaded_files)} additional file(s)!', 'success')
            else:
                flash(f'Content "{new_content.title}" created successfully!', 'success')
            return redirect(url_for('view_content', content_id=new_content.id))
        except Exception as e:
            db.session.rollback()
            flash('Error creating content. Please try again.', 'error')
            app.logger.error(f'Error creating content: {e}')
    
    return render_template('create_content.html', form=form)



@app.route('/content/<int:content_id>')
def view_content(content_id):
    """View single content item with recommendations"""
    try:
        content = Content.query.get_or_404(content_id)
        
        # Track user interaction
        track_user_interaction(content_id, 'view', score=1.0)
        
        # Get hybrid recommendations (combines content-based and collaborative filtering)
        recommendations = get_hybrid_recommendations(content_id, limit=4)
        category_suggestions = get_category_recommendations(content.category, exclude_id=content_id, limit=3)
        
        return render_template('view_content.html', 
                             content=content.to_dict(),
                             recommendations=recommendations,
                             category_suggestions=category_suggestions)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in view_content: {e}")
        flash('Error loading content', 'error')
        return redirect(url_for('index'))

@app.route('/edit/<int:content_id>', methods=['GET', 'POST'])
@require_login
def edit_content(content_id):
    """Edit existing content"""
    content = Content.query.get_or_404(content_id)
    
    # Check if user owns this content
    if content.user_id != current_user.id:
        flash('You can only edit your own content.', 'error')
        return redirect(url_for('index'))
    
    form = EditContentForm()
    form.category.choices = [(cat, cat) for cat in CONTENT_CATEGORIES]
    form.status.choices = [(status, status) for status in CONTENT_STATUS]
    
    if form.validate_on_submit():
        # Handle image upload
        if 'image' in request.files:
            file = request.files['image']
            if file.filename != '':
                new_image = save_image_file(file)
                if new_image:
                    # Remove old image if it exists
                    if content.image:
                        old_image_path = os.path.join(app.config['UPLOAD_FOLDER'], content.image)
                        if os.path.exists(old_image_path):
                            os.remove(old_image_path)
                    content.image = new_image
                else:
                    flash('Invalid image file. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG files.', 'error')
                    return render_template('edit_content.html', form=form, content=content.to_dict())

        # Handle tags safely
        tags_data = form.tags.data or ''
        tags_list = [tag.strip() for tag in tags_data.split(',') if tag.strip()] if tags_data else []

        # Update content fields
        content.title = form.title.data
        content.content = form.content.data
        content.category = form.category.data
        content.status = form.status.data
        content.author = form.author.data
        content.set_tags_list(tags_list)
        content.updated_at = datetime.utcnow()
        
        # Handle additional file uploads
        uploaded_files = []
        if 'files' in request.files:
            files = request.files.getlist('files')
            for file in files:
                if file and file.filename != '':
                    file_record = save_uploaded_file(
                        file, 
                        current_user.id if current_user.is_authenticated else 'anonymous',
                        content_id
                    )
                    if file_record:
                        uploaded_files.append(file_record)
                    else:
                        flash(f'Failed to upload file: {file.filename}', 'warning')
        
        try:
            db.session.commit()
            
            # Track user interaction for collaborative filtering
            track_user_interaction(content_id, 'edit', score=1.5)
            
            if uploaded_files:
                flash(f'Content "{content.title}" updated successfully with {len(uploaded_files)} additional file(s)!', 'success')
            else:
                flash(f'Content "{content.title}" updated successfully!', 'success')
            return redirect(url_for('view_content', content_id=content_id))
        except Exception as e:
            db.session.rollback()
            flash('Error updating content. Please try again.', 'error')
            app.logger.error(f'Error updating content: {e}')
    
    # Pre-populate form with existing data
    if request.method == 'GET':
        form.title.data = content.title
        form.content.data = content.content
        form.category.data = content.category
        form.status.data = content.status
        form.author.data = content.author
        form.tags.data = ', '.join(content.get_tags_list())
    
    return render_template('edit_content.html', form=form, content=content.to_dict())

@app.route('/delete/<int:content_id>', methods=['POST'])
@require_login
def delete_content(content_id):
    """Delete content"""
    content = Content.query.get_or_404(content_id)
    
    # Check if user owns this content
    if content.user_id != current_user.id:
        flash('You can only delete your own content.', 'error')
        return redirect(url_for('index'))
    title = content.title
    
    # Remove associated image file if it exists
    if content.image:
        image_path = os.path.join(app.config['UPLOAD_FOLDER'], content.image)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    try:
        db.session.delete(content)
        db.session.commit()
        flash(f'Content "{title}" deleted successfully!', 'info')
    except Exception as e:
        db.session.rollback()
        flash('Error deleting content. Please try again.', 'error')
        app.logger.error(f'Error deleting content: {e}')
    
    return redirect(url_for('index'))

@app.route('/api/content/<int:content_id>/status', methods=['POST'])
def update_content_status(content_id):
    """Update content status via AJAX"""
    content = Content.query.get_or_404(content_id)
    
    json_data = request.get_json()
    new_status = json_data.get('status') if json_data else None
    if new_status not in CONTENT_STATUS:
        abort(400)
    
    content.status = new_status
    content.updated_at = datetime.utcnow()
    
    try:
        db.session.commit()
        return {'success': True, 'status': new_status}
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error updating content status: {e}')
        abort(500)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """Serve uploaded images"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/files/<filename>')
def serve_file(filename):
    """Serve uploaded files (documents, videos, audio, archives)"""
    return send_from_directory(app.config['FILES_FOLDER'], filename)

@app.route('/file/<int:file_id>')
def download_file(file_id):
    """Download file by ID with proper headers"""
    file_record = File.query.get_or_404(file_id)
    
    # Determine storage location based on file type
    if file_record.file_type == 'image':
        storage_folder = app.config['UPLOAD_FOLDER']
    else:
        storage_folder = app.config['FILES_FOLDER']
    
    file_path = os.path.join(storage_folder, file_record.filename)
    
    if not os.path.exists(file_path):
        flash('File not found.', 'error')
        return redirect(url_for('index'))
    
    # Track download interaction
    track_user_interaction(file_record.content_id, 'download', score=0.5)
    
    return send_from_directory(
        storage_folder, 
        file_record.filename,
        as_attachment=True,
        download_name=file_record.original_filename
    )

@app.route('/content/<int:content_id>/files')
def content_files(content_id):
    """Display all files associated with content"""
    content = Content.query.get_or_404(content_id)
    files = File.query.filter_by(content_id=content_id).all()
    
    # Track user interaction
    track_user_interaction(content_id, 'view_files', score=0.3)
    
    return render_template('content_files.html', content=content, files=files)

@app.route('/files')
@require_login
def file_manager():
    """File management dashboard for logged-in users"""
    # Get all files for current user
    user_files = File.query.filter_by(user_id=current_user.id).order_by(File.created_at.desc()).all()
    
    # Group files by type
    files_by_type = {
        'image': [],
        'document': [],
        'video': [],
        'audio': [],
        'archive': [],
        'other': []
    }
    
    for file in user_files:
        files_by_type[file.file_type].append(file)
    
    # Calculate total storage used
    total_size = sum(file.file_size for file in user_files)
    
    return render_template('file_manager.html', 
                         files_by_type=files_by_type, 
                         total_files=len(user_files),
                         total_size=total_size)

@app.route('/file/<int:file_id>/delete', methods=['POST'])
@require_login
def delete_file(file_id):
    """Delete a file (only owner can delete)"""
    file_record = File.query.get_or_404(file_id)
    
    # Check ownership
    if file_record.user_id != current_user.id:
        flash('You can only delete your own files.', 'error')
        return redirect(url_for('file_manager'))
    
    try:
        # Delete physical file
        if file_record.file_type == 'image':
            storage_folder = app.config['UPLOAD_FOLDER']
        else:
            storage_folder = app.config['FILES_FOLDER']
        
        file_path = os.path.join(storage_folder, file_record.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Delete database record
        db.session.delete(file_record)
        db.session.commit()
        
        flash(f'File "{file_record.original_filename}" deleted successfully.', 'success')
    except Exception as e:
        db.session.rollback()
        app.logger.error(f'Error deleting file: {e}')
        flash('Error deleting file. Please try again.', 'error')
    
    return redirect(url_for('file_manager'))

@app.route('/bulk-upload', methods=['GET', 'POST'])
@require_login
def bulk_upload():
    """Bulk file upload for multiple files at once"""
    if request.method == 'POST':
        files = request.files.getlist('files')
        category = request.form.get('category', '')
        tags = request.form.get('tags', '')
        
        if not files or all(file.filename == '' for file in files):
            flash('No files selected for upload.', 'warning')
            return redirect(url_for('bulk_upload'))
        
        uploaded_files = []
        failed_files = []
        
        for file in files:
            if file and file.filename != '':
                file_record = save_uploaded_file(
                    file, 
                    current_user.id,
                    content_id=None  # Bulk uploads are not associated with specific content
                )
                if file_record:
                    uploaded_files.append(file_record)
                else:
                    failed_files.append(file.filename)
        
        # Create success message
        if uploaded_files:
            total_size = sum(file.file_size for file in uploaded_files)
            size_str = format_file_size(total_size)
            flash(f'Successfully uploaded {len(uploaded_files)} files ({size_str})', 'success')
        
        if failed_files:
            flash(f'Failed to upload {len(failed_files)} files: {", ".join(failed_files[:3])}', 'warning')
        
        return redirect(url_for('file_manager'))
    
    return render_template('bulk_upload.html')

def format_file_size(bytes_size):
    """Helper function to format file size"""
    if bytes_size < 1024:
        return f"{bytes_size} B"
    elif bytes_size < 1024*1024:
        return f"{bytes_size/1024:.1f} KB"
    elif bytes_size < 1024*1024*1024:
        return f"{bytes_size/(1024*1024):.1f} MB"
    else:
        return f"{bytes_size/(1024*1024*1024):.1f} GB"

@app.context_processor
def inject_translation_functions():
    """Make translation functions available to all templates"""
    return dict(
        get_translation=get_translation,
        get_available_languages=get_available_languages,
        current_language=session.get('language', 'ko')
    )

@app.route('/gallery')
def image_gallery():
    """Display all images in a gallery view with user type filtering"""
    content_with_images = Content.query.filter(Content.image != None).order_by(Content.created_at.desc()).all()
    
    # Initialize classifier for automatic classification
    classifier = UserTypeClassifier()
    
    images = []
    for content in content_with_images:
        # Auto-classify if not already classified
        if not content.user_type or content.user_type == 'mixed':
            tags_list = content.get_tags_list() if hasattr(content, 'get_tags_list') else []
            user_type = classifier.classify_content(
                content.title,
                content.content,
                content.category,
                tags_list
            )
            content.user_type = user_type
            db.session.add(content)
        
        images.append({
            'filename': content.image,
            'title': content.title,
            'content_id': content.id,
            'created_at': content.created_at,
            'author': content.author,
            'user_type': content.user_type or 'mixed'
        })
    
    db.session.commit()
    return render_template('gallery.html', images=images)



@app.route('/analytics/cf')
def cf_analytics():
    """Collaborative Filtering Analytics Dashboard"""
    try:
        user_id = get_user_id()
        
        # Get user interaction statistics
        total_interactions = UserInteraction.query.count()
        unique_users = UserInteraction.query.with_entities(UserInteraction.user_id).distinct().count()
        user_interactions = UserInteraction.query.filter_by(user_id=user_id).count()
        
        # Get recent interactions
        recent_interactions = UserInteraction.query.order_by(
            UserInteraction.timestamp.desc()
        ).limit(10).all()
        
        # Get most popular content
        popular_content = db.session.query(
            Content.id, Content.title, func.count(UserInteraction.id).label('interaction_count')
        ).join(UserInteraction).group_by(Content.id, Content.title).order_by(
            func.count(UserInteraction.id).desc()
        ).limit(5).all()
        
        # Get user similarity data (if enough data exists)
        similar_users = []
        try:
            user_item_matrix, users, items = build_user_item_matrix()
            if user_id in user_item_matrix and len(users) > 1:
                target_user_items = user_item_matrix[user_id]
                for other_user in users[:5]:  # Check top 5 users
                    if other_user != user_id:
                        similarity = calculate_user_similarity(target_user_items, user_item_matrix[other_user])
                        if similarity > 0:
                            similar_users.append({
                                'user_id': other_user[:8] + '...',  # Truncate for privacy
                                'similarity': round(similarity, 3)
                            })
        except Exception as e:
            logging.error(f"Error calculating user similarities: {e}")
        
        return render_template('cf_analytics.html',
                             total_interactions=total_interactions,
                             unique_users=unique_users,
                             user_interactions=user_interactions,
                             recent_interactions=recent_interactions,
                             popular_content=popular_content,
                             similar_users=similar_users)
    except Exception as e:
        logging.error(f"Error in CF analytics: {e}")
        return render_template('cf_analytics.html', error=str(e))

@app.route('/demo/collaborative-filtering')
def cf_demo():
    """Collaborative Filtering demonstration page"""
    return render_template('cf_demo.html')

@app.route('/demo/cf-visual')
def cf_visual():
    """Visual collaborative filtering demonstration"""
    return render_template('cf_visual.html')

@app.route('/recommendations/<int:content_id>')
def content_recommendations(content_id):
    """API endpoint for getting content recommendations"""
    recommendations = get_hybrid_recommendations(content_id, limit=6)
    return {
        'recommendations': [
            {
                'id': rec['content'].id,
                'title': rec['content'].title,
                'category': rec['content'].category,
                'author': rec['content'].author,
                'hybrid_score': round(rec.get('hybrid_score', 0), 2),
                'cf_score': round(rec.get('cf_score', 0), 2),
                'content_score': round(rec.get('content_score', 0), 2),
                'url': url_for('view_content', content_id=rec['content'].id)
            }
            for rec in recommendations
        ]
    }

@app.route('/admin/database')
def database_admin():
    """Database administration dashboard"""
    try:
        # Get health status
        connection_ok, connection_msg = DatabaseHealthChecker.check_connection()
        integrity_ok, integrity_issues = DatabaseHealthChecker.check_table_integrity()
        
        health_status = {
            'connection': connection_ok,
            'integrity': integrity_ok,
            'connection_msg': connection_msg,
            'integrity_issues': integrity_issues
        }
        
        # Get database statistics
        stats = DatabaseManager.get_database_statistics()
        
        # Calculate totals
        stats['total_content'] = Content.query.count()
        stats['total_interactions'] = UserInteraction.query.count()
        
        return render_template('database_admin.html', 
                             health_status=health_status,
                             stats=stats)
    except Exception as e:
        logging.error(f"Error in database admin: {e}")
        return render_template('database_admin.html', 
                             health_status={'connection': False, 'integrity': False},
                             stats={}, error=str(e))

@app.route('/admin/db/optimize', methods=['POST'])
def optimize_database():
    """Optimize database performance"""
    try:
        success = DatabaseManager.optimize_database()
        return {'success': success}
    except Exception as e:
        logging.error(f"Database optimization error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/backup', methods=['POST'])
def create_database_backup():
    """Create database backup"""
    try:
        success, result = DatabaseManager.create_database_backup()
        return {'success': success, 'filename': result if success else None, 'error': result if not success else None}
    except Exception as e:
        logging.error(f"Database backup error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/update-search', methods=['POST'])
def update_search_vectors():
    """Update full-text search vectors"""
    try:
        DatabaseManager.create_full_text_search_triggers()
        success = DatabaseManager.update_all_search_vectors()
        return {'success': success}
    except Exception as e:
        logging.error(f"Search vector update error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/create-indexes', methods=['POST'])
def create_database_indexes():
    """Create additional database indexes"""
    try:
        success = DatabaseManager.create_database_indexes()
        return {'success': success}
    except Exception as e:
        logging.error(f"Index creation error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/cleanup', methods=['POST'])
def cleanup_old_data():
    """Clean up old user interactions"""
    try:
        deleted = DatabaseManager.cleanup_old_interactions()
        return {'success': True, 'deleted': deleted}
    except Exception as e:
        logging.error(f"Data cleanup error: {e}")
        return {'success': False, 'error': str(e)}

@app.route('/admin/db/health')
def database_health():
    """Get database health status"""
    try:
        connection_ok, connection_msg = DatabaseHealthChecker.check_connection()
        integrity_ok, integrity_issues = DatabaseHealthChecker.check_table_integrity()
        
        return {
            'connection': connection_ok,
            'integrity': integrity_ok,
            'connection_msg': connection_msg,
            'issues': integrity_issues if not integrity_ok else []
        }
    except Exception as e:
        logging.error(f"Health check error: {e}")
        return {'connection': False, 'integrity': False, 'error': str(e)}

@app.route('/admin/db/search')
def full_text_search():
    """Full-text search endpoint"""
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return {'results': []}
        
        results = DatabaseManager.full_text_search(query)
        formatted_results = []
        
        for row in results:
            formatted_results.append({
                'id': row.id,
                'title': row.title,
                'content': row.content,
                'category': row.category,
                'author': row.author,
                'rank': float(row.rank)
            })
        
        return {'results': formatted_results}
    except Exception as e:
        logging.error(f"Full-text search error: {e}")
        return {'results': [], 'error': str(e)}

@app.route('/personalized-recommendations')
@require_login
def personalized_recommendations():
    """Dashboard showing personalized content recommendations"""
    try:
        user_id = current_user.id
        
        # Get different types of recommendations
        hybrid_recommendations = recommendation_engine.get_hybrid_recommendations(user_id, 8)
        content_based = recommendation_engine.get_content_based_recommendations(user_id, 6)
        collaborative = recommendation_engine.get_collaborative_filtering_recommendations(user_id, 6)
        
        # Analyze user behavior for insights
        user_preferences = recommendation_engine.analyze_user_behavior(user_id)
        
        # Get user statistics
        total_interactions = UserInteraction.query.filter_by(user_id=user_id).count()
        recent_interactions = UserInteraction.query.filter(
            UserInteraction.user_id == user_id,
            UserInteraction.timestamp >= datetime.utcnow() - timedelta(days=7)
        ).count()
        
        # Top categories and authors
        top_categories = sorted(user_preferences['categories'].items(), key=lambda x: x[1], reverse=True)[:5]
        top_authors = sorted(user_preferences['authors'].items(), key=lambda x: x[1], reverse=True)[:5]
        
        return render_template('personalized_recommendations.html',
                             hybrid_recommendations=hybrid_recommendations,
                             content_based=content_based,
                             collaborative=collaborative,
                             user_preferences=user_preferences,
                             total_interactions=total_interactions,
                             recent_interactions=recent_interactions,
                             top_categories=top_categories,
                             top_authors=top_authors)
        
    except Exception as e:
        app.logger.error(f'Error loading personalized recommendations: {e}')
        flash('Error loading recommendations. Please try again.', 'error')
        return redirect(url_for('index'))

@app.route('/api/recommendation-feedback', methods=['POST'])
@require_login
def recommendation_feedback():
    """Track user feedback on recommendations"""
    try:
        data = request.get_json()
        content_id = data.get('content_id')
        action = data.get('action')
        
        if not content_id or not action:
            return {'error': 'Missing content_id or action'}, 400
        
        recommendation_engine.track_recommendation_feedback(
            current_user.id, content_id, action
        )
        
        return {'status': 'success'}
        
    except Exception as e:
        app.logger.error(f'Error tracking recommendation feedback: {e}')
        return {'error': 'Failed to track feedback'}, 500

@app.route('/trading_view')
@require_login
def trading_view():
    """Trading-style analytics dashboard for content performance"""
    try:
        # Get content statistics
        total_content = Content.query.count()
        
        # Calculate total views from user interactions
        total_views = db.session.query(db.func.count(UserInteraction.id))\
            .filter(UserInteraction.interaction_type == 'view').scalar() or 0
        
        # Get active users (users who interacted in last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        active_users = db.session.query(db.func.count(db.distinct(UserInteraction.user_id)))\
            .filter(UserInteraction.timestamp >= thirty_days_ago).scalar() or 0
        
        # Calculate engagement rate
        total_interactions = UserInteraction.query.count()
        engagement_rate = round((total_interactions / max(total_content, 1)) * 100, 1)
        
        # Get top performing content (by interaction count)
        top_content = db.session.query(
            Content,
            db.func.count(UserInteraction.id).label('view_count')
        ).outerjoin(UserInteraction)\
         .group_by(Content.id)\
         .order_by(db.desc('view_count'))\
         .limit(10).all()
        
        # Get trending tags
        trending_tags_data = db.session.query(
            db.func.unnest(db.func.string_to_array(Content.tags, ',')).label('tag'),
            db.func.count().label('count')
        ).filter(Content.tags.isnot(None))\
         .filter(Content.tags != '')\
         .group_by('tag')\
         .order_by(db.desc('count'))\
         .limit(10).all()
        
        trending_tags = [{'name': tag.strip(), 'count': count} 
                        for tag, count in trending_tags_data if tag and tag.strip()]
        
        # Get recent activities
        recent_activities = db.session.query(
            UserInteraction.interaction_type.label('type'),
            UserInteraction.timestamp,
            Content.title.label('content_title'),
            User.first_name.label('user_name')
        ).join(Content, UserInteraction.content_id == Content.id)\
         .outerjoin(User, UserInteraction.user_id == User.id)\
         .order_by(db.desc(UserInteraction.timestamp))\
         .limit(20).all()
        
        # Format activities for display
        formatted_activities = []
        for activity in recent_activities:
            action_map = {
                'view': 'viewed',
                'edit': 'edited',
                'like': 'liked',
                'share': 'shared',
                'delete': 'deleted'
            }
            
            formatted_activities.append({
                'type': activity.type,
                'action': action_map.get(activity.type, activity.type),
                'content_title': activity.content_title,
                'user_name': activity.user_name or 'Anonymous User',
                'timestamp': activity.timestamp
            })
        
        return render_template('trading_view.html',
                             total_content=total_content,
                             total_views=total_views,
                             active_users=active_users,
                             engagement_rate=engagement_rate,
                             top_content=[content for content, _ in top_content],
                             trending_tags=trending_tags,
                             recent_activities=formatted_activities,
                             current_user=current_user)
        
    except Exception as e:
        app.logger.error(f"Error in trading view: {e}")
        flash('An error occurred while loading analytics.', 'error')
        return redirect(url_for('index'))

# AI-Powered Content Relevance Scoring Routes

@app.route('/api/content/<int:content_id>/relevance-score')
def get_content_relevance_score(content_id):
    """Get AI-powered relevance score for a specific content item"""
    try:
        analyzer = ContentRelevanceAnalyzer()
        content = Content.query.get_or_404(content_id)
        content_data = {
            'title': content.title,
            'content': content.content,
            'category': content.category,
            'tags': content.get_tags_list()
        }
        result = analyzer.analyze_content_relevance(content_data)
        return result
    except Exception as e:
        app.logger.error(f"Error getting relevance score: {e}")
        return {'error': 'Failed to analyze content'}, 500

@app.route('/api/content/batch-relevance-scores', methods=['POST'])
def get_batch_relevance_scores():
    """Get relevance scores for multiple content items"""
    try:
        data = request.get_json()
        content_ids = data.get('content_ids', [])
        
        if not content_ids:
            return {'error': 'No content IDs provided'}, 400
        
        analyzer = ContentRelevanceAnalyzer()
        results = {}
        for content_id in content_ids[:10]:  # Limit to 10 items
            try:
                content = Content.query.get(content_id)
                if content:
                    content_data = {
                        'title': content.title,
                        'content': content.content,
                        'category': content.category,
                        'tags': content.get_tags_list()
                    }
                    analysis = analyzer.analyze_content_relevance(content_data)
                    results[content_id] = analysis
            except Exception as e:
                app.logger.error(f"Error analyzing content {content_id}: {e}")
                continue
        return {'results': results}
    except Exception as e:
        app.logger.error(f"Error in batch relevance scoring: {e}")
        return {'error': 'Failed to analyze content batch'}, 500

@app.route('/content/<int:content_id>/ai-analysis')
@require_login
def detailed_ai_analysis(content_id):
    """Show detailed AI analysis for content"""
    try:
        content = Content.query.get_or_404(content_id)
        
        # Check if user owns the content or it's published
        if content.user_id != current_user.id and content.status != 'Published':
            abort(403)
        
        analyzer = ContentRelevanceAnalyzer()
        analysis = analyzer.analyze_content_relevance(content.to_dict())
        
        return render_template('ai_analysis.html', 
                             content=content.to_dict(),
                             analysis=analysis)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in detailed AI analysis: {e}")
        flash('Error loading AI analysis', 'error')
        return redirect(url_for('view_content', content_id=content_id))

@app.route('/ai-content-insights')
@require_login
def ai_content_insights():
    """Dashboard showing AI insights for user's content"""
    try:
        # Get user's content
        user_content = Content.query.filter_by(user_id=current_user.id).all()
        
        if not user_content:
            return render_template('ai_insights.html', 
                                 content_analyses=[], 
                                 summary_stats={})
        
        # Analyze user's content
        content_ids = [c.id for c in user_content[:20]]  # Limit to 20 most recent
        analyzer = ContentRelevanceAnalyzer()
        analyses = {}
        for content_id in content_ids:
            try:
                content = Content.query.get(content_id)
                if content:
                    content_data = {
                        'title': content.title,
                        'content': content.content,
                        'category': content.category,
                        'tags': content.get_tags_list()
                    }
                    analysis = analyzer.analyze_content_relevance(content_data)
                    analyses[content_id] = analysis
            except Exception as e:
                app.logger.error(f"Error analyzing content {content_id}: {e}")
                continue
        
        # Calculate summary statistics
        scores = [analysis['overall_score'] for analysis in analyses.values() if 'overall_score' in analysis]
        summary_stats = {
            'total_content': len(user_content),
            'analyzed_content': len(scores),
            'average_score': round(sum(scores) / len(scores), 1) if scores else 0,
            'excellent_content': len([s for s in scores if s >= 8]),
            'needs_improvement': len([s for s in scores if s < 6])
        }
        
        # Combine content with analyses
        content_analyses = []
        for content in user_content[:20]:
            analysis = analyses.get(content.id, {})
            content_analyses.append({
                'content': content.to_dict(),
                'analysis': analysis
            })
        
        return render_template('ai_insights.html', 
                             content_analyses=content_analyses,
                             summary_stats=summary_stats)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in AI content insights: {e}")
        flash('Error loading AI insights', 'error')
        return redirect(url_for('index'))

# Ecommerce Routes

@app.route('/shop')
def shop():
    """Product catalog page"""
    try:
        # Get filter parameters
        category_filter = request.args.get('category', '')
        search_query = request.args.get('search', '')
        page = request.args.get('page', 1, type=int)
        per_page = 12
        
        # Build query
        query = Product.query.filter(Product.is_active == True)
        
        if category_filter:
            query = query.filter(Product.category == category_filter)
        
        if search_query:
            query = query.filter(Product.name.contains(search_query))
        
        # Paginate results
        products = query.order_by(Product.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        # Get available categories
        categories = db.session.query(Product.category).filter(Product.is_active == True).distinct().all()
        categories = [cat[0] for cat in categories]
        
        # Get cart count for authenticated users
        cart_count = 0
        if current_user.is_authenticated:
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        
        # Get personalized recommendations for authenticated users
        recommendations = []
        if current_user.is_authenticated:
            try:
                recommendations = get_product_recommendations_for_user(
                    current_user.id, 'hybrid', limit=4
                )
            except Exception as e:
                app.logger.warning(f"Error getting product recommendations: {e}")
        
        return render_template('shop.html', 
                             products=products,
                             categories=categories,
                             current_category=category_filter,
                             search_query=search_query,
                             cart_count=cart_count,
                             recommendations=recommendations)
    except Exception as e:
        app.logger.error(f"Error in shop: {e}")
        flash('Error loading products', 'error')
        return redirect(url_for('index'))

@app.route('/product/<int:product_id>')
def product_detail(product_id):
    """Product detail page with automatic view tracking"""
    try:
        product = Product.query.get_or_404(product_id)
        
        if not product.is_active:
            abort(404)
        
        # Track product view automatically
        track_product_view(product_id)
        
        # Add to cart form
        form = AddToCartForm()
        
        # Get cart count for authenticated users
        cart_count = 0
        if current_user.is_authenticated:
            cart_count = CartItem.query.filter_by(user_id=current_user.id).count()
        
        # Get similar products
        similar_products = []
        try:
            similar_products = get_similar_products(product_id, limit=4)
        except Exception as e:
            app.logger.warning(f"Error getting similar products: {e}")
        
        # Get view statistics for this product
        view_stats = get_product_view_stats(product_id)
        
        # Get product reviews and average rating
        reviews = ProductReview.query.filter_by(product_id=product_id).order_by(ProductReview.created_at.desc()).all()
        avg_rating = 0
        if reviews:
            avg_rating = sum(review.rating for review in reviews) / len(reviews)
        
        return render_template('product_detail.html', 
                             product=product,
                             form=form,
                             cart_count=cart_count,
                             similar_products=similar_products,
                             view_stats=view_stats,
                             reviews=reviews,
                             avg_rating=round(avg_rating, 1))
    except Exception as e:
        app.logger.error(f"Error in product detail: {e}")
        flash('Error loading product', 'error')
        return redirect(url_for('shop'))

@app.route('/create-product', methods=['GET', 'POST'])
@csrf.exempt
@require_login
def create_product():
    """Create new product (sellers only)"""
    if request.method == 'POST':
        form = ProductForm(request.form, meta={'csrf': False})
    else:
        form = ProductForm(meta={'csrf': False})
    
    # Set category choices
    categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Food', 'Other']
    form.category.choices = [(cat, cat) for cat in categories]
    
    # Set season type choices to match what's in forms.py
    season_choices = [
        ('', 'Select Season Type'),
        ('spring', 'Spring'),
        ('summer', 'Summer'), 
        ('fall', 'Fall/Autumn'),
        ('winter', 'Winter'),
        ('holiday', 'Holiday Season'),
        ('christmas', 'Christmas'),
        ('valentine', 'Valentine\'s Day'),
        ('easter', 'Easter'),
        ('halloween', 'Halloween'),
        ('thanksgiving', 'Thanksgiving'),
        ('back_to_school', 'Back to School'),
        ('new_year', 'New Year')
    ]
    form.season_type.choices = season_choices
    
    # Handle empty seasonal datetime fields before validation
    if request.method == 'POST':
        # Process form data first
        form.process()
        
        # Handle seasonal fields
        if form.is_seasonal.data:
            # If seasonal but no dates provided, set to None
            if not form.seasonal_start.raw_data or form.seasonal_start.raw_data == ['']: 
                form.seasonal_start.data = None
            if not form.seasonal_end.raw_data or form.seasonal_end.raw_data == ['']: 
                form.seasonal_end.data = None
            if not form.seasonal_year.raw_data or form.seasonal_year.raw_data == ['']: 
                form.seasonal_year.data = None
        else:
            # Clear seasonal fields if not seasonal product
            form.seasonal_start.data = None
            form.seasonal_end.data = None
            form.seasonal_year.data = None
    
    # Process form submission directly without validation
    if request.method == 'POST':
        app.logger.info("Processing product creation from form data")
        try:
            # Handle image upload with proper error handling
            image_url = None
            if form.image.data and hasattr(form.image.data, 'filename') and form.image.data.filename:
                image_file = form.image.data
                app.logger.info(f"Processing image upload: {image_file.filename}")
                
                if allowed_file(image_file.filename):
                    try:
                        # Ensure upload directory exists
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        
                        # Generate unique filename
                        filename = str(uuid.uuid4()) + '_' + secure_filename(image_file.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        
                        app.logger.info(f"Saving image to: {file_path}")
                        
                        # Save the file
                        image_file.save(file_path)
                        image_url = url_for('uploaded_file', filename=filename)
                        
                        app.logger.info(f"Successfully saved image: {filename} -> {image_url}")
                        
                    except Exception as e:
                        app.logger.error(f"Error saving image: {e}")
                        flash('Error uploading image. Please try again.', 'warning')
                else:
                    app.logger.warning(f"File type not allowed: {image_file.filename}")
                    flash('File type not allowed. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG files.', 'warning')
            else:
                app.logger.info("No image file provided in form")
            
            # Create product using request form data directly
            product = Product()
            product.name = request.form.get('name', '')
            product.description = request.form.get('description', '')
            product.price = float(request.form.get('price', 0))
            product.category = request.form.get('category', '')
            product.stock_quantity = int(request.form.get('stock_quantity', 0))
            product.is_digital = 'is_digital' in request.form
            product.image_url = image_url
            product.seller_id = current_user.id
            product.is_seasonal = 'is_seasonal' in request.form
            product.season_type = request.form.get('season_type', '') if product.is_seasonal else None
            product.seasonal_start = None  # Handle datetime parsing separately if needed
            product.seasonal_end = None
            product.seasonal_year = int(request.form.get('seasonal_year', 0)) if request.form.get('seasonal_year') else None
            
            db.session.add(product)
            db.session.commit()
            
            flash('Product created successfully!', 'success')
            return redirect(url_for('product_detail', product_id=product.id))
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Error creating product: {e}")
            flash('Error creating product', 'error')
    else:
        # Log form validation errors for debugging
        if request.method == 'POST':
            app.logger.warning(f"Form validation failed. Errors: {form.errors}")
            app.logger.warning(f"Form data: {request.form}")
            for field, errors in form.errors.items():
                for error in errors:
                    flash(f'{field.replace("_", " ").title()}: {error}', 'error')
    
    return render_template('create_product.html', form=form)

@app.route('/my-products')
@require_login
def my_products():
    """View user's products"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        products = Product.query.filter_by(seller_id=current_user.id)\
                              .order_by(Product.created_at.desc())\
                              .paginate(page=page, per_page=per_page, error_out=False)
        
        return render_template('my_products.html', products=products)
    except Exception as e:
        app.logger.error(f"Error in my products: {e}")
        flash('Error loading products', 'error')
        return redirect(url_for('index'))

@app.route('/edit-product/<int:product_id>', methods=['GET', 'POST'])
@csrf.exempt
@require_login
def edit_product(product_id):
    """Edit existing product (only seller can edit)"""
    try:
        product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first_or_404()
        
        # Create form with proper initialization and disable CSRF
        if request.method == 'POST':
            form = ProductForm(request.form, meta={'csrf': False})
        else:
            form = ProductForm(obj=product, meta={'csrf': False})
        
        # Set category choices
        categories = ['Electronics', 'Clothing', 'Books', 'Home & Garden', 'Sports', 'Toys', 'Food', 'Other']
        form.category.choices = [(cat, cat) for cat in categories]
        
        # Set season type choices to match what's in forms.py
        season_choices = [
            ('', 'Select Season Type'),
            ('spring', 'Spring'),
            ('summer', 'Summer'), 
            ('fall', 'Fall/Autumn'),
            ('winter', 'Winter'),
            ('holiday', 'Holiday Season'),
            ('christmas', 'Christmas'),
            ('valentine', 'Valentine\'s Day'),
            ('easter', 'Easter'),
            ('halloween', 'Halloween'),
            ('thanksgiving', 'Thanksgiving'),
            ('back_to_school', 'Back to School'),
            ('new_year', 'New Year')
        ]
        form.season_type.choices = season_choices
        
        # Process form submission directly without validation
        if request.method == 'POST':
            app.logger.info("Processing product edit from form data")
            
            # Update product with form data directly
            product.name = request.form.get('name', '')
            product.description = request.form.get('description', '')
            product.price = float(request.form.get('price', 0))
            product.category = request.form.get('category', '')
            product.stock_quantity = int(request.form.get('stock_quantity', 0))
            product.is_digital = 'is_digital' in request.form
            product.is_seasonal = 'is_seasonal' in request.form
            product.season_type = request.form.get('season_type', '') if product.is_seasonal else None
            product.seasonal_start = None  # Handle datetime parsing separately if needed
            product.seasonal_end = None
            product.seasonal_year = int(request.form.get('seasonal_year', 0)) if request.form.get('seasonal_year') else None
            
            # Handle image upload with proper error handling
            if 'image' in request.files and request.files['image'].filename:
                image_file = request.files['image']
                app.logger.info(f"Processing image upload for edit: {image_file.filename}")
                
                if allowed_file(image_file.filename):
                    try:
                        # Ensure upload directory exists
                        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                        
                        # Generate unique filename
                        filename = str(uuid.uuid4()) + '_' + secure_filename(image_file.filename)
                        file_path = os.path.join(UPLOAD_FOLDER, filename)
                        
                        app.logger.info(f"Saving updated image to: {file_path}")
                        
                        # Save the file
                        image_file.save(file_path)
                        product.image_url = url_for('uploaded_file', filename=filename)
                        
                        app.logger.info(f"Successfully updated image: {filename} -> {product.image_url}")
                        
                    except Exception as e:
                        app.logger.error(f"Error saving image during edit: {e}")
                        flash('Error uploading image. Please try again.', 'warning')
                else:
                    app.logger.warning(f"File type not allowed during edit: {image_file.filename}")
                    flash('File type not allowed. Please upload PNG, JPG, JPEG, GIF, WEBP, or SVG files.', 'warning')
            else:
                app.logger.info("No new image file provided in edit form")
            
            db.session.commit()
            flash('Product updated successfully!', 'success')
            return redirect(url_for('my_products'))
        
        return render_template('create_product.html', form=form, product=product, is_edit=True)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error editing product: {e}")
        flash('Error updating product', 'error')
        return redirect(url_for('my_products'))

@app.route('/delete-product/<int:product_id>', methods=['POST'])
@require_login
def delete_product(product_id):
    """Delete product (only seller can delete)"""
    try:
        product = Product.query.filter_by(id=product_id, seller_id=current_user.id).first_or_404()
        
        # Check if product has any orders (prevent deletion if orders exist)
        from sqlalchemy import exists
        has_orders = db.session.query(exists().where(OrderItem.product_id == product_id)).scalar()
        
        if has_orders:
            flash('Cannot delete product with existing orders. You can deactivate it instead.', 'error')
            return redirect(url_for('my_products'))
        
        # Remove from cart items first
        CartItem.query.filter_by(product_id=product_id).delete()
        
        # Remove from wishlist
        Wishlist.query.filter_by(product_id=product_id).delete()
        
        # Remove product reviews
        ProductReview.query.filter_by(product_id=product_id).delete()
        
        # Delete the product image file if it exists
        if product.image_url:
            try:
                # Extract filename from URL
                import re
                filename_match = re.search(r'/([^/]+)$', product.image_url)
                if filename_match:
                    filename = filename_match.group(1)
                    file_path = os.path.join(UPLOAD_FOLDER, filename)
                    if os.path.exists(file_path):
                        os.remove(file_path)
            except Exception as e:
                app.logger.warning(f"Could not delete image file: {e}")
        
        # Delete the product
        product_name = product.name
        db.session.delete(product)
        db.session.commit()
        
        flash(f'Product "{product_name}" has been deleted successfully.', 'success')
        app.logger.info(f"Product {product_id} deleted by user {current_user.id}")
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error deleting product: {e}")
        flash('Error deleting product. Please try again.', 'error')
    
    return redirect(url_for('my_products'))

@app.route('/add-to-cart', methods=['POST'])
@csrf.exempt
@require_login
def add_to_cart():
    """Add product to cart"""
    try:
        product_id = request.form.get('product_id', type=int)
        form = AddToCartForm()
        if form.validate():
            quantity = form.quantity.data
            
            product = Product.query.get_or_404(product_id)
            
            if not product.is_active:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Product is not available'
                    }), 400
                flash('Product is not available', 'error')
                return redirect(url_for('product_detail', product_id=product_id))
            
            # Check stock
            if not product.is_digital and product.stock_quantity < quantity:
                if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                    return jsonify({
                        'success': False,
                        'message': 'Not enough stock available'
                    }), 400
                flash('Not enough stock available', 'error')
                return redirect(url_for('product_detail', product_id=product_id))
            
            # Check if item already in cart
            cart_item = CartItem.query.filter_by(
                user_id=current_user.id, 
                product_id=product_id
            ).first()
            
            if cart_item:
                cart_item.quantity += quantity
                message = 'Cart updated!'
            else:
                cart_item = CartItem(
                    user_id=current_user.id,
                    product_id=product_id,
                    quantity=quantity
                )
                db.session.add(cart_item)
                message = 'Added to cart!'
            
            db.session.commit()
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return jsonify({
                    'success': True,
                    'message': message,
                    'product_name': product.name
                })
            
            flash(message, 'success')
            
        # Handle AJAX validation errors
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Invalid form data'
            }), 400
            
        return redirect(url_for('product_detail', product_id=product_id))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error adding to cart: {e}")
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Error adding to cart'
            }), 500
        
        flash('Error adding to cart', 'error')
        return redirect(url_for('shop'))

@app.route('/cart')
@require_login
def cart():
    """Shopping cart page"""
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id)\
                                 .join(Product)\
                                 .filter(Product.is_active == True)\
                                 .all()
        
        total = sum(item.get_total_price() for item in cart_items)
        
        # Create update form for cart items
        update_form = UpdateCartForm()
        
        return render_template('cart.html', 
                             cart_items=cart_items,
                             total=total,
                             update_form=update_form)
    except Exception as e:
        app.logger.error(f"Error in cart: {e}")
        flash('Error loading cart', 'error')
        return redirect(url_for('shop'))

@app.route('/update-cart/<int:item_id>', methods=['POST'])
@require_login
def update_cart(item_id):
    """Update cart item quantity"""
    try:
        cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
        
        form = UpdateCartForm()
        if form.validate_on_submit():
            new_quantity = form.quantity.data
            
            # Check stock for physical products
            if not cart_item.product.is_digital and cart_item.product.stock_quantity < new_quantity:
                flash('Not enough stock available', 'error')
            else:
                cart_item.quantity = new_quantity
                db.session.commit()
                flash('Cart updated!', 'success')
        
        return redirect(url_for('cart'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error updating cart: {e}")
        flash('Error updating cart', 'error')
        return redirect(url_for('cart'))

@app.route('/remove-from-cart/<int:item_id>')
@require_login
def remove_from_cart(item_id):
    """Remove item from cart"""
    try:
        cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
        db.session.delete(cart_item)
        db.session.commit()
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': True,
                'item_id': item_id,
                'message': 'Item removed from cart'
            })
        
        flash('Item removed from cart', 'success')
        return redirect(url_for('cart'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error removing from cart: {e}")
        
        # Handle AJAX requests
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({
                'success': False,
                'message': 'Error removing item'
            }), 400
        
        flash('Error removing item', 'error')
        return redirect(url_for('cart'))

@app.route('/api/cart/count')
@require_login
def api_cart_count():
    """API endpoint for cart item count"""
    try:
        count = CartItem.query.filter_by(user_id=current_user.id)\
                             .join(Product)\
                             .filter(Product.is_active == True)\
                             .count()
        return jsonify({'count': count})
    except Exception as e:
        app.logger.error(f"Error getting cart count: {e}")
        return jsonify({'count': 0})

@app.route('/api/cart/preview')
@require_login
def api_cart_preview():
    """API endpoint for cart preview"""
    try:
        cart_items = CartItem.query.filter_by(user_id=current_user.id)\
                                 .join(Product)\
                                 .filter(Product.is_active == True)\
                                 .all()
        
        items = []
        total = 0
        
        for item in cart_items:
            item_total = item.product.price * item.quantity
            total += item_total
            
            # Handle both image_filename and image_url attributes
            image_url = None
            if hasattr(item.product, 'image_filename') and item.product.image_filename:
                image_url = f"/static/uploads/{item.product.image_filename}"
            elif hasattr(item.product, 'image_url') and item.product.image_url:
                image_url = item.product.image_url
            
            items.append({
                'id': item.id,
                'name': item.product.name,
                'price': float(item.product.price),
                'quantity': item.quantity,
                'image_url': image_url
            })
        
        return jsonify({
            'items': items,
            'total': float(total),
            'count': len(items)
        })
    except Exception as e:
        app.logger.error(f"Error getting cart preview: {e}")
        return jsonify({
            'items': [],
            'total': 0.0,
            'count': 0
        })

@app.route('/api/price-comparison', methods=['POST'])
@require_login
def api_price_comparison():
    """API endpoint for price comparison analysis"""
    try:
        data = request.get_json()
        current_price = float(data.get('price', 0))
        category = data.get('category', 'general')
        
        # Get all products in the same category
        category_products = Product.query.filter(
            Product.is_active == True,
            Product.category.ilike(f'%{category}%')
        ).all()
        
        # If no category match, get all products
        if not category_products:
            category_products = Product.query.filter(Product.is_active == True).all()
        
        if not category_products:
            return jsonify({
                'category_average': current_price,
                'min_price': current_price,
                'max_price': current_price,
                'percentile': 50,
                'similar_count': 1,
                'trend': 'neutral',
                'trend_text': 'Insufficient data for comparison',
                'value_rating': 'average',
                'insights': 'Not enough similar products for meaningful comparison.'
            })
        
        # Calculate price statistics
        prices = [float(p.price) for p in category_products]
        prices.sort()
        
        avg_price = sum(prices) / len(prices)
        min_price = min(prices)
        max_price = max(prices)
        
        # Calculate percentile
        lower_count = sum(1 for p in prices if p < current_price)
        percentile = int((lower_count / len(prices)) * 100)
        
        # Determine value rating
        if current_price <= avg_price * 0.8:
            value_rating = 'excellent'
        elif current_price <= avg_price * 0.9:
            value_rating = 'good'
        elif current_price <= avg_price * 1.1:
            value_rating = 'average'
        elif current_price <= avg_price * 1.3:
            value_rating = 'premium'
        else:
            value_rating = 'high'
        
        # Determine trend (simulated based on price position)
        if current_price < avg_price * 0.9:
            trend = 'down'
            trend_text = 'Below market average'
        elif current_price > avg_price * 1.1:
            trend = 'up'
            trend_text = 'Above market average'
        else:
            trend = 'neutral'
            trend_text = 'Near market average'
        
        # Generate insights
        price_diff = current_price - avg_price
        savings_text = f"${abs(price_diff):.2f} {'below' if price_diff < 0 else 'above'} average"
        
        if value_rating == 'excellent':
            insights = f"Excellent value! This price is {savings_text} for this category."
        elif value_rating == 'good':
            insights = f"Good deal! You're saving {savings_text} compared to similar items."
        elif value_rating == 'average':
            insights = f"Fair market price. This is {savings_text} the category average."
        elif value_rating == 'premium':
            insights = f"Premium pricing. You're paying {savings_text} for potential higher quality."
        else:
            insights = f"High-end pricing. This is {savings_text} typical market rates."
        
        return jsonify({
            'category_average': avg_price,
            'min_price': min_price,
            'max_price': max_price,
            'percentile': percentile,
            'similar_count': len(prices),
            'trend': trend,
            'trend_text': trend_text,
            'value_rating': value_rating,
            'insights': insights
        })
        
    except Exception as e:
        app.logger.error(f"Error in price comparison: {e}")
        return jsonify({
            'category_average': current_price,
            'min_price': current_price,
            'max_price': current_price,
            'percentile': 50,
            'similar_count': 1,
            'trend': 'neutral',
            'trend_text': 'Analysis unavailable',
            'value_rating': 'average',
            'insights': 'Price comparison temporarily unavailable.'
        })

@app.route('/checkout', methods=['GET', 'POST'])
@require_login
def checkout():
    """Checkout page"""
    try:
        # Get cart items
        cart_items = CartItem.query.filter_by(user_id=current_user.id)\
                                 .join(Product)\
                                 .filter(Product.is_active == True)\
                                 .all()
        
        if not cart_items:
            flash('Your cart is empty', 'error')
            return redirect(url_for('cart'))
        
        form = CheckoutForm()
        total = sum(item.get_total_price() for item in cart_items)
        
        if form.validate_on_submit():
            # Create order
            order = Order(
                user_id=current_user.id,
                total_amount=total,
                shipping_name=form.shipping_name.data,
                shipping_address=form.shipping_address.data,
                shipping_city=form.shipping_city.data,
                shipping_state=form.shipping_state.data,
                shipping_zip=form.shipping_zip.data,
                shipping_country=form.shipping_country.data
            )
            order.order_number = order.generate_order_number()
            
            db.session.add(order)
            db.session.flush()  # Get order ID
            
            # Create order items
            for cart_item in cart_items:
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=cart_item.product_id,
                    product_name=cart_item.product.name,
                    product_price=cart_item.product.price,
                    quantity=cart_item.quantity
                )
                db.session.add(order_item)
            
            db.session.commit()
            
            # Create Stripe checkout session
            return redirect(url_for('create_checkout_session', order_id=order.id))
        
        return render_template('checkout.html', 
                             form=form,
                             cart_items=cart_items,
                             total=total)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in checkout: {e}")
        flash('Error processing checkout', 'error')
        return redirect(url_for('cart'))

@app.route('/create-checkout-session/<int:order_id>')
@require_login
def create_checkout_session(order_id):
    """Create Stripe checkout session"""
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
        
        if order.payment_status != 'pending':
            flash('Order already processed', 'error')
            return redirect(url_for('order_detail', order_id=order_id))
        
        domain = get_domain()
        
        # Create line items from order
        line_items = []
        for item in order.items:
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product_name,
                    },
                    'unit_amount': int(item.product_price * 100),  # Convert to cents
                },
                'quantity': item.quantity,
            })
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f'https://{domain}/payment-success/{order_id}',
            cancel_url=f'https://{domain}/payment-cancel/{order_id}',
            metadata={'order_id': order_id}
        )
        
        # Store session ID
        order.stripe_session_id = checkout_session.id
        db.session.commit()
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error creating checkout session: {e}")
        flash('Error creating payment session', 'error')
        return redirect(url_for('checkout'))

@app.route('/payment-success/<int:order_id>')
@require_login
def payment_success(order_id):
    """Handle successful payment"""
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
        
        # Update order status
        order.payment_status = 'paid'
        order.status = 'paid'
        
        # Update stock for physical products
        for item in order.items:
            if not item.product.is_digital:
                item.product.stock_quantity -= item.quantity
        
        # Clear cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        
        db.session.commit()
        
        flash('Payment successful! Thank you for your order.', 'success')
        return render_template('payment_success.html', order=order)
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in payment success: {e}")
        flash('Error processing payment confirmation', 'error')
        return redirect(url_for('my_orders'))

@app.route('/payment-cancel/<int:order_id>')
@require_login
def payment_cancel(order_id):
    """Handle cancelled payment"""
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
        
        # Mark order as cancelled
        order.payment_status = 'failed'
        order.status = 'cancelled'
        db.session.commit()
        
        flash('Payment was cancelled. Your order has been cancelled.', 'warning')
        return redirect(url_for('cart'))
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error in payment cancel: {e}")
        flash('Error handling payment cancellation', 'error')
        return redirect(url_for('cart'))

@app.route('/my-orders')
@require_login
def my_orders():
    """View user's orders"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = 10
        
        orders = Order.query.filter_by(user_id=current_user.id)\
                           .order_by(Order.created_at.desc())\
                           .paginate(page=page, per_page=per_page, error_out=False)
        
        # Get personalized product recommendations based on order history
        recommended_products = []
        try:
            from product_recommendation_engine import get_user_recommendations, get_popular_products
            
            # Get recommendations based on user's purchase history
            user_recommendations = get_user_recommendations(current_user.id, limit=6)
            
            if user_recommendations:
                recommended_products = user_recommendations
            else:
                # Fallback to popular products for new users
                recommended_products = get_popular_products(limit=6)
                
        except Exception as rec_error:
            app.logger.error(f"Error getting recommendations: {rec_error}")
            # Fallback to recent active products
            recommended_products = Product.query.filter_by(is_active=True)\
                                              .order_by(Product.created_at.desc())\
                                              .limit(6).all()
        
        return render_template('my_orders.html', orders=orders, recommended_products=recommended_products)
    except Exception as e:
        app.logger.error(f"Error in my orders: {e}")
        flash('Error loading orders', 'error')
        return redirect(url_for('index'))

@app.route('/order/<int:order_id>')
@require_login
def order_detail(order_id):
    """Order detail page"""
    try:
        order = Order.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
        return render_template('order_detail.html', order=order)
    except Exception as e:
        app.logger.error(f"Error in order detail: {e}")
        flash('Error loading order', 'error')
        return redirect(url_for('my_orders'))

@app.route('/create_story', methods=['GET', 'POST'])
@csrf.exempt
@require_login
def create_story():
    """Create a new limited-time story"""
    from forms import StoryForm
    from datetime import datetime, timedelta
    from models import Story
    
    form = StoryForm()
    
    # Populate product choices for current user's products
    products = Product.query.filter_by(seller_id=current_user.id).all()
    form.product_id.choices = [('', 'No product')] + [(str(p.id), p.name) for p in products]
    
    if request.method == 'POST':
        app.logger.info(f"Story form submission - Valid: {form.validate()}")
        app.logger.info(f"Form errors: {form.errors}")
        
        if form.validate():
            try:
                # Handle image upload
                image_url = None
                if form.image.data:
                    image_url = save_image_file(form.image.data)
                
                # Create new story using the updated model fields
                story = Story()
                story.title = form.title.data
                story.content = form.content.data
                story.story_type = form.story_type.data
                story.expires_at = form.expires_at.data
                story.priority = form.priority.data
                story.image_url = image_url
                story.user_id = current_user.id  # Updated field name
                story.author_name = current_user.first_name or current_user.email or "Unknown"
                
                # Link to product if specified
                if form.product_id.data:
                    story.linked_product_id = int(form.product_id.data)  # Updated field name
                
                db.session.add(story)
                db.session.commit()
                
                flash('Story created successfully! 스토리가 성공적으로 생성되었습니다!', 'success')
                return redirect(url_for('stories'))
            except Exception as e:
                app.logger.error(f"Error creating story: {e}")
                db.session.rollback()
                flash('Error creating story. Please try again. 스토리 생성 중 오류가 발생했습니다.', 'error')
        else:
            flash('Please check the form for errors. 양식 오류를 확인해주세요.', 'error')
    
    return render_template('create_story.html', form=form)

@app.route('/stories')
def stories():
    """View all active stories sorted by recommendation algorithm"""
    # Get active stories
    active_stories = Story.get_active_stories(limit=50)
    
    # Apply recommendation algorithm to sort stories
    if current_user.is_authenticated:
        sorted_stories = get_personalized_story_recommendations(current_user.id, active_stories)
    else:
        # For anonymous users, use popularity-based sorting
        sorted_stories = get_trending_story_recommendations(active_stories)
    
    # Limit to top 20 for display
    final_stories = sorted_stories[:20]
    
    return render_template('stories.html', stories=final_stories)

def get_personalized_story_recommendations(user_id, stories):
    """
    Get personalized story recommendations based on user behavior and preferences
    """
    if not stories:
        return []
    
    try:
        # Get user's interaction history
        user_interactions = UserInteraction.query.filter_by(user_id=user_id).all()
        user_views = ProductView.query.filter_by(user_id=user_id).all()
        user_purchases = Order.query.filter_by(user_id=user_id).all()
        
        # Calculate story scores based on multiple factors
        story_scores = []
        
        for story in stories:
            score = 0.0
            
            # Base popularity score (view count, like count, click count)
            popularity_score = (
                (story.view_count or 0) * 0.3 +
                (story.like_count or 0) * 0.5 +
                (story.click_count or 0) * 0.2
            )
            score += popularity_score * 0.2
            
            # Time factor - newer stories get slight boost
            time_factor = 1.0
            if story.created_at:
                hours_old = (datetime.now() - story.created_at).total_seconds() / 3600
                # Stories less than 24 hours old get boost
                if hours_old < 24:
                    time_factor = 1.2 - (hours_old / 24 * 0.2)
            score += time_factor * 0.1
            
            # User interaction similarity
            if story.linked_product_id:
                # Check if user has interacted with similar products
                linked_product = Product.query.get(story.linked_product_id)
                if linked_product:
                    # Category matching
                    for interaction in user_interactions:
                        if hasattr(interaction, 'content_id'):
                            content = Content.query.get(interaction.content_id)
                            if content and content.category == linked_product.category:
                                score += 0.3
                    
                    # Product view matching
                    for view in user_views:
                        viewed_product = Product.query.get(view.product_id)
                        if viewed_product and viewed_product.category == linked_product.category:
                            score += 0.2
                    
                    # Purchase history matching
                    for purchase in user_purchases:
                        order_items = OrderItem.query.filter_by(order_id=purchase.id).all()
                        for item in order_items:
                            purchased_product = Product.query.get(item.product_id)
                            if purchased_product and purchased_product.category == linked_product.category:
                                score += 0.4
            
            # Story type preference (learn from user's past story interactions)
            story_type_boost = 0.0
            if story.story_type:
                # Check user's past story interactions by type
                # This would need story interaction tracking, for now use base boost
                type_multipliers = {
                    'product': 1.2,  # Product stories often more engaging
                    'promotion': 1.1,
                    'event': 1.0,
                    'news': 0.9,
                    'general': 0.8
                }
                story_type_boost = type_multipliers.get(story.story_type, 1.0)
            score *= story_type_boost
            
            # Urgency factor (stories expiring soon get priority)
            if not story.is_expired():
                time_remaining = story.expires_at - datetime.now()
                if time_remaining.total_seconds() < 3600:  # Less than 1 hour
                    score *= 1.3
                elif time_remaining.total_seconds() < 21600:  # Less than 6 hours
                    score *= 1.1
            
            story_scores.append((story, score))
        
        # Sort by score descending
        story_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [story for story, score in story_scores]
        
    except Exception as e:
        print(f"Error in personalized story recommendations: {e}")
        # Fallback to popularity-based sorting
        return get_trending_story_recommendations(stories)

def get_trending_story_recommendations(stories):
    """
    Get trending story recommendations for anonymous users
    """
    if not stories:
        return []
    
    try:
        story_scores = []
        
        for story in stories:
            # Calculate trending score based on engagement metrics
            score = 0.0
            
            # Base engagement score
            view_count = story.view_count or 0
            like_count = story.like_count or 0
            click_count = story.click_count or 0
            
            # Weighted engagement score
            engagement_score = (
                view_count * 0.2 +
                like_count * 0.4 +
                click_count * 0.4
            )
            
            # Time decay factor - recent stories get more weight
            if story.created_at:
                hours_old = (datetime.now() - story.created_at).total_seconds() / 3600
                time_factor = max(0.1, 1.0 - (hours_old / 168))  # Decay over 1 week
                score = engagement_score * time_factor
            else:
                score = engagement_score * 0.5
            
            # Story type popularity boost
            type_boosts = {
                'product': 1.3,      # Product stories tend to be popular
                'promotion': 1.2,
                'event': 1.1,
                'news': 1.0,
                'general': 0.9
            }
            score *= type_boosts.get(story.story_type, 1.0)
            
            # Urgency boost for expiring stories
            if not story.is_expired():
                time_remaining = story.expires_at - datetime.now()
                if time_remaining.total_seconds() < 7200:  # Less than 2 hours
                    score *= 1.4
                elif time_remaining.total_seconds() < 21600:  # Less than 6 hours
                    score *= 1.2
            
            # Priority boost
            if hasattr(story, 'priority') and story.priority:
                score *= (1.0 + story.priority * 0.1)
            
            story_scores.append((story, score))
        
        # Sort by score descending
        story_scores.sort(key=lambda x: x[1], reverse=True)
        
        return [story for story, score in story_scores]
        
    except Exception as e:
        print(f"Error in trending story recommendations: {e}")
        # Fallback to simple time-based sorting
        return sorted(stories, key=lambda s: s.created_at, reverse=True)

@app.route('/story/<int:story_id>')
def story_detail(story_id):
    """View individual story details"""
    story = Story.query.get_or_404(story_id)
    
    # Check if story is expired
    if story.is_expired():
        flash('This story has expired. 이 스토리는 만료되었습니다.', 'warning')
        return redirect(url_for('stories'))
    
    # Increment view count
    story.increment_views()
    
    return render_template('story_detail.html', story=story)

@app.route('/story/<int:story_id>/click')
def story_click(story_id):
    """Track story click and redirect to linked content"""
    story = Story.query.get_or_404(story_id)
    
    # Increment click count
    story.increment_clicks()
    
    # Redirect to linked product if available
    if story.linked_product_id:
        return redirect(url_for('product_detail', product_id=story.linked_product_id))
    
    # Otherwise redirect to story detail
    return redirect(url_for('story_detail', story_id=story_id))

@app.route('/my_stories')
@require_login
def my_stories():
    """View user's own stories"""
    user_stories = Story.query.filter_by(user_id=current_user.id)\
        .order_by(Story.created_at.desc()).all()
    return render_template('my_stories.html', stories=user_stories)

@app.route('/story/<int:story_id>/delete', methods=['POST'])
@require_login
def delete_story(story_id):
    """Delete a story (only owner can delete)"""
    story = Story.query.get_or_404(story_id)
    
    if story.user_id != current_user.id:
        flash('You can only delete your own stories. 본인의 스토리만 삭제할 수 있습니다.', 'error')
        return redirect(url_for('my_stories'))
    
    db.session.delete(story)
    db.session.commit()
    
    flash('Story deleted successfully! 스토리가 성공적으로 삭제되었습니다!', 'success')
    return redirect(url_for('my_stories'))

@app.route('/api/story/<int:story_id>/like', methods=['POST'])
@csrf.exempt
def like_story(story_id):
    """Like a story (API endpoint for TikTok-style viewer)"""
    try:
        story = Story.query.get_or_404(story_id)
        
        # Increment likes
        if story.likes is None:
            story.likes = 0
        story.likes += 1
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'likes': story.likes,
            'message': 'Story liked!'
        })
    
    except Exception as e:
        print(f"Error liking story: {e}")
        return jsonify({
            'success': False,
            'message': 'Failed to like story'
        }), 500

@app.route('/api/stories/cleanup', methods=['POST'])
def cleanup_expired_stories():
    """Clean up expired stories (can be called by cron job)"""
    expired_stories = Story.query.filter(
        Story.expires_at <= datetime.utcnow()
    ).all()
    
    count = len(expired_stories)
    for story in expired_stories:
        story.is_active = False
    
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Cleaned up {count} expired stories',
        'count': count
    })

@app.route('/set_language/<language>')
def set_language(language):
    """Set user's preferred language"""
    if language in get_available_languages():
        session['language'] = language
        flash(get_translation('language_changed', language), 'success')
    return redirect(request.referrer or url_for('index'))


# ============= WISHLIST FUNCTIONALITY =============

@app.route('/wishlist')
@require_login
def wishlist():
    """Display user's wishlist"""
    wishlist_items = Wishlist.query.filter_by(user_id=current_user.id)\
        .options(db.joinedload(Wishlist.product))\
        .order_by(Wishlist.created_at.desc()).all()
    
    return render_template('wishlist.html', wishlist_items=wishlist_items)


@app.route('/api/wishlist/add', methods=['POST'])
@require_login
def api_add_to_wishlist():
    """Add product to wishlist"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'})
        
        product = Product.query.get_or_404(product_id)
        
        # Check if already in wishlist
        existing = Wishlist.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if existing:
            return jsonify({'success': False, 'message': 'Already in wishlist'})
        
        # Add to wishlist
        wishlist_item = Wishlist(
            user_id=current_user.id,
            product_id=product_id
        )
        db.session.add(wishlist_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Added to wishlist'})
        
    except Exception as e:
        app.logger.error(f"Error adding to wishlist: {e}")
        return jsonify({'success': False, 'message': 'Error adding to wishlist'})


@app.route('/api/wishlist/remove', methods=['POST'])
@require_login
def api_remove_from_wishlist():
    """Remove product from wishlist"""
    try:
        data = request.get_json()
        product_id = data.get('product_id')
        
        if not product_id:
            return jsonify({'success': False, 'message': 'Product ID required'})
        
        wishlist_item = Wishlist.query.filter_by(
            user_id=current_user.id,
            product_id=product_id
        ).first()
        
        if not wishlist_item:
            return jsonify({'success': False, 'message': 'Not in wishlist'})
        
        db.session.delete(wishlist_item)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Removed from wishlist'})
        
    except Exception as e:
        app.logger.error(f"Error removing from wishlist: {e}")
        return jsonify({'success': False, 'message': 'Error removing from wishlist'})


@app.route('/api/wishlist/clear', methods=['POST'])
@require_login
def api_clear_wishlist():
    """Clear entire wishlist"""
    try:
        Wishlist.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Wishlist cleared'})
        
    except Exception as e:
        app.logger.error(f"Error clearing wishlist: {e}")
        return jsonify({'success': False, 'message': 'Error clearing wishlist'})


@app.route('/api/wishlist/check/<int:product_id>')
@require_login
def api_check_wishlist(product_id):
    """Check if product is in wishlist"""
    in_wishlist = Wishlist.query.filter_by(
        user_id=current_user.id,
        product_id=product_id
    ).first() is not None
    
    return jsonify({'in_wishlist': in_wishlist})


# ============= COUPON FUNCTIONALITY =============

@app.route('/api/coupon/validate', methods=['POST'])
@require_login
def api_validate_coupon():
    """Validate coupon code"""
    try:
        data = request.get_json()
        code = data.get('code', '').strip().upper()
        cart_total = float(data.get('cart_total', 0))
        
        if not code:
            return jsonify({'valid': False, 'message': 'Coupon code required'})
        
        coupon = Coupon.query.filter_by(code=code).first()
        
        if not coupon:
            return jsonify({'valid': False, 'message': 'Invalid coupon code'})
        
        if not coupon.is_valid:
            return jsonify({'valid': False, 'message': 'Coupon is expired or inactive'})
        
        if cart_total < coupon.minimum_amount:
            return jsonify({
                'valid': False, 
                'message': f'Minimum order amount is ${coupon.minimum_amount:.2f}'
            })
        
        # Check per-user usage limit
        user_usage = CouponUsage.query.filter_by(
            coupon_id=coupon.id,
            user_id=current_user.id
        ).count()
        
        if user_usage >= coupon.per_user_limit:
            return jsonify({'valid': False, 'message': 'You have already used this coupon'})
        
        discount = coupon.calculate_discount(cart_total)
        
        return jsonify({
            'valid': True,
            'discount': discount,
            'description': coupon.description,
            'discount_type': coupon.discount_type,
            'discount_value': coupon.discount_value
        })
        
    except Exception as e:
        app.logger.error(f"Error validating coupon: {e}")
        return jsonify({'valid': False, 'message': 'Error validating coupon'})


# ============= PRODUCT REVIEWS =============

@app.route('/api/product/<int:product_id>/review', methods=['POST'])
@require_login
def api_add_product_review(product_id):
    """Add or update product review"""
    try:
        data = request.get_json()
        rating = int(data.get('rating', 0))
        title = data.get('title', '').strip()
        review_text = data.get('review_text', '').strip()
        
        if not (1 <= rating <= 5):
            return jsonify({'success': False, 'message': 'Rating must be between 1 and 5'})
        
        product = Product.query.get_or_404(product_id)
        
        # Check if user has purchased this product
        has_purchased = OrderItem.query.join(Order).filter(
            Order.user_id == current_user.id,
            Order.payment_status == 'paid',
            OrderItem.product_id == product_id
        ).first() is not None
        
        # Check for existing review
        existing_review = ProductReview.query.filter_by(
            product_id=product_id,
            user_id=current_user.id
        ).first()
        
        if existing_review:
            # Update existing review
            existing_review.rating = rating
            existing_review.title = title
            existing_review.review_text = review_text
            existing_review.verified_purchase = has_purchased
            existing_review.updated_at = datetime.now()
            review = existing_review
        else:
            # Create new review
            review = ProductReview(
                product_id=product_id,
                user_id=current_user.id,
                rating=rating,
                title=title,
                review_text=review_text,
                verified_purchase=has_purchased
            )
            db.session.add(review)
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Review saved successfully'})
        
    except Exception as e:
        app.logger.error(f"Error adding review: {e}")
        return jsonify({'success': False, 'message': 'Error saving review'})


@app.route('/api/product/<int:product_id>/reviews')
def api_get_product_reviews(product_id):
    """Get product reviews"""
    try:
        reviews = ProductReview.query.filter_by(product_id=product_id)\
            .options(db.joinedload(ProductReview.user))\
            .order_by(ProductReview.created_at.desc()).all()
        
        review_data = []
        for review in reviews:
            review_data.append({
                'id': review.id,
                'rating': review.rating,
                'title': review.title,
                'review_text': review.review_text,
                'verified_purchase': review.verified_purchase,
                'helpful_votes': review.helpful_votes,
                'created_at': review.created_at.strftime('%B %d, %Y'),
                'user_name': review.user.first_name or review.user.email.split('@')[0],
                'user_image': review.user.profile_image_url
            })
        
        # Calculate average rating
        avg_rating = sum(r.rating for r in reviews) / len(reviews) if reviews else 0
        
        return jsonify({
            'reviews': review_data,
            'average_rating': round(avg_rating, 1),
            'total_reviews': len(reviews)
        })
        
    except Exception as e:
        app.logger.error(f"Error getting reviews: {e}")
        return jsonify({'reviews': [], 'average_rating': 0, 'total_reviews': 0})


# ============= ADVANCED SEARCH =============

@app.route('/search')
def advanced_search():
    """Advanced search interface"""
    return render_template('advanced_search.html')


@app.route('/api/search/advanced')
def api_advanced_search():
    """Advanced product search with filters"""
    try:
        query = request.args.get('q', '').strip()
        category = request.args.get('category', '')
        min_price = request.args.get('min_price', type=float)
        max_price = request.args.get('max_price', type=float)
        sort_by = request.args.get('sort', 'relevance')
        in_stock_only = request.args.get('in_stock') == 'true'
        
        # Base query
        products_query = Product.query
        
        # Text search
        if query:
            products_query = products_query.filter(
                db.or_(
                    Product.name.ilike(f'%{query}%'),
                    Product.description.ilike(f'%{query}%'),
                    Product.category.ilike(f'%{query}%')
                )
            )
        
        # Category filter
        if category:
            products_query = products_query.filter(Product.category == category)
        
        # Price range filter
        if min_price is not None:
            products_query = products_query.filter(Product.price >= min_price)
        if max_price is not None:
            products_query = products_query.filter(Product.price <= max_price)
        
        # Stock filter
        if in_stock_only:
            products_query = products_query.filter(
                db.or_(
                    Product.is_digital == True,
                    Product.stock_quantity > 0
                )
            )
        
        # Sorting
        if sort_by == 'price_low':
            products_query = products_query.order_by(Product.price.asc())
        elif sort_by == 'price_high':
            products_query = products_query.order_by(Product.price.desc())
        elif sort_by == 'newest':
            products_query = products_query.order_by(Product.created_at.desc())
        elif sort_by == 'name':
            products_query = products_query.order_by(Product.name.asc())
        else:  # relevance or default
            products_query = products_query.order_by(Product.created_at.desc())
        
        products = products_query.limit(50).all()
        
        # Format results
        results = []
        for product in products:
            results.append({
                'id': product.id,
                'name': product.name,
                'description': product.description[:150] + '...' if len(product.description) > 150 else product.description,
                'price': float(product.price),
                'category': product.category,
                'image_url': product.image_url,
                'in_stock': product.is_digital or product.stock_quantity > 0,
                'stock_quantity': product.stock_quantity if not product.is_digital else None
            })
        
        return jsonify({
            'products': results,
            'total': len(results),
            'query': query,
            'filters': {
                'category': category,
                'min_price': min_price,
                'max_price': max_price,
                'sort_by': sort_by,
                'in_stock_only': in_stock_only
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error in advanced search: {e}")
        return jsonify({'products': [], 'total': 0, 'error': 'Search error'})

# ============= SEASONAL PRODUCTS =============

@app.route('/seasonal')
def seasonal_products():
    """Seasonal products page with filtering by season type"""
    page = request.args.get('page', 1, type=int)
    season = request.args.get('season', '')
    category = request.args.get('category', '')
    status = request.args.get('status', 'available')  # available, out_of_season, all
    sort_by = request.args.get('sort', 'season')
    
    # Build query for seasonal products
    query = Product.query.filter(
        Product.is_active == True,
        Product.is_seasonal == True
    )
    
    # Apply season filter
    if season:
        query = query.filter(Product.season_type == season)
    
    # Apply category filter
    if category:
        query = query.filter(Product.category == category)
    
    # Apply status filter
    if status == 'available':
        # Filter for currently available seasonal products
        current_month = datetime.utcnow().month
        query = query.filter(
            db.or_(
                db.and_(Product.seasonal_start.isnot(None), 
                       Product.seasonal_end.isnot(None),
                       db.or_(
                           db.and_(Product.seasonal_start <= datetime.utcnow(),
                                  Product.seasonal_end >= datetime.utcnow()),
                           # Handle cross-year seasons
                           db.and_(func.extract('year', Product.seasonal_start) != func.extract('year', Product.seasonal_end),
                                  db.or_(datetime.utcnow() >= Product.seasonal_start,
                                        datetime.utcnow() <= Product.seasonal_end))
                       )),
                # For products without specific dates, use season type
                db.and_(Product.seasonal_start.is_(None), Product.seasonal_end.is_(None))
            )
        )
    elif status == 'out_of_season':
        # This would require more complex filtering, skip for now
        pass
    
    # Apply sorting
    if sort_by == 'season':
        query = query.order_by(Product.season_type.asc(), Product.created_at.desc())
    elif sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    elif sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    else:
        query = query.order_by(Product.season_type.asc())
    
    # Paginate results
    products = query.paginate(page=page, per_page=12, error_out=False)
    
    # Get available seasons and categories
    seasons = db.session.query(Product.season_type).filter(
        Product.is_active == True,
        Product.is_seasonal == True,
        Product.season_type.isnot(None)
    ).distinct().all()
    seasons = [s[0] for s in seasons]
    
    categories = db.session.query(Product.category).filter(
        Product.is_active == True,
        Product.is_seasonal == True
    ).distinct().all()
    categories = [c[0] for c in categories]
    
    # Get seasonal statistics
    total_seasonal = Product.query.filter(
        Product.is_active == True,
        Product.is_seasonal == True
    ).count()
    
    current_seasonal = 0
    upcoming_seasonal = 0
    for product in Product.query.filter(Product.is_seasonal == True, Product.is_active == True).all():
        if product.is_currently_seasonal:
            current_seasonal += 1
        elif product.days_until_seasonal:
            upcoming_seasonal += 1
    
    # Season icon mapping
    season_icons = {
        'spring': 'seedling',
        'summer': 'sun',
        'fall': 'leaf',
        'autumn': 'leaf',
        'winter': 'snowflake',
        'holiday': 'gift',
        'christmas': 'tree',
        'valentine': 'heart',
        'halloween': 'pumpkin',
        'thanksgiving': 'drumstick-bite',
        'easter': 'egg',
        'new_year': 'fireworks',
        'back_to_school': 'graduation-cap'
    }
    
    return render_template('seasonal.html',
                         products=products,
                         seasons=seasons,
                         categories=categories,
                         current_season=season,
                         current_category=category,
                         current_status=status,
                         current_sort=sort_by,
                         total_seasonal=total_seasonal,
                         current_seasonal=current_seasonal,
                         upcoming_seasonal=upcoming_seasonal,
                         season_icons=season_icons,
                         now=datetime.utcnow())

@app.route('/api/seasonal/stats')
def api_seasonal_stats():
    """API endpoint for seasonal product statistics"""
    try:
        current_month = datetime.utcnow().month
        
        # Get all seasonal products
        seasonal_products = Product.query.filter(
            Product.is_active == True,
            Product.is_seasonal == True
        ).all()
        
        stats = {
            'total': len(seasonal_products),
            'available': 0,
            'upcoming': 0,
            'out_of_season': 0,
            'by_season': {}
        }
        
        for product in seasonal_products:
            # Count by availability status
            if product.is_currently_seasonal:
                stats['available'] += 1
            elif product.days_until_seasonal:
                stats['upcoming'] += 1
            else:
                stats['out_of_season'] += 1
            
            # Count by season type
            if product.season_type:
                if product.season_type not in stats['by_season']:
                    stats['by_season'][product.season_type] = 0
                stats['by_season'][product.season_type] += 1
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

# ============= NEW ARRIVALS =============

@app.route('/new-arrivals')
def new_arrivals():
    """New arrivals page with filtering and sorting"""
    page = request.args.get('page', 1, type=int)
    category = request.args.get('category', '')
    sort_by = request.args.get('sort', 'newest')
    days_filter = request.args.get('days', 30, type=int)
    
    # Ensure days_filter is an integer (fallback safety)
    try:
        days_filter = int(days_filter)
    except (ValueError, TypeError):
        days_filter = 30
    
    # Build query for new arrivals
    query = Product.query.filter(
        Product.is_active == True,
        Product.is_new_arrival == True
    )
    
    # Apply date-based filtering
    cutoff_date = datetime.utcnow() - timedelta(days=days_filter)
    query = query.filter(Product.created_at >= cutoff_date)
    
    # Apply category filter
    if category:
        query = query.filter(Product.category == category)
    
    # Apply sorting
    if sort_by == 'newest':
        query = query.order_by(Product.created_at.desc())
    elif sort_by == 'price_low':
        query = query.order_by(Product.price.asc())
    elif sort_by == 'price_high':
        query = query.order_by(Product.price.desc())
    elif sort_by == 'name':
        query = query.order_by(Product.name.asc())
    
    # Paginate results
    products = query.paginate(
        page=page, per_page=12, error_out=False
    )
    
    # Get categories for filter dropdown
    categories = db.session.query(Product.category).filter(
        Product.is_active == True,
        Product.is_new_arrival == True,
        Product.created_at >= cutoff_date
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    # Get new arrivals statistics
    total_new = query.count()
    today_count = Product.query.filter(
        Product.is_active == True,
        Product.is_new_arrival == True,
        Product.created_at >= datetime.utcnow().date()
    ).count()
    
    week_count = Product.query.filter(
        Product.is_active == True,
        Product.is_new_arrival == True,
        Product.created_at >= datetime.utcnow() - timedelta(days=7)
    ).count()
    
    return render_template('new_arrivals.html',
                         products=products,
                         categories=categories,
                         current_category=category,
                         current_sort=sort_by,
                         current_days=days_filter,
                         total_new=total_new,
                         today_count=today_count,
                         week_count=week_count,
                         now=datetime.utcnow())

@app.route('/api/new-arrivals/stats')
def api_new_arrivals_stats():
    """API endpoint for new arrivals statistics"""
    try:
        # Get new arrivals count by time period
        today = datetime.utcnow().date()
        week_ago = datetime.utcnow() - timedelta(days=7)
        month_ago = datetime.utcnow() - timedelta(days=30)
        
        stats = {
            'today': Product.query.filter(
                Product.is_active == True,
                Product.is_new_arrival == True,
                Product.created_at >= today
            ).count(),
            'week': Product.query.filter(
                Product.is_active == True,
                Product.is_new_arrival == True,
                Product.created_at >= week_ago
            ).count(),
            'month': Product.query.filter(
                Product.is_active == True,
                Product.is_new_arrival == True,
                Product.created_at >= month_ago
            ).count(),
            'total': Product.query.filter(
                Product.is_active == True,
                Product.is_new_arrival == True
            ).count()
        }
        
        # Get category breakdown
        categories = db.session.query(
            Product.category,
            db.func.count(Product.id).label('count')
        ).filter(
            Product.is_active == True,
            Product.is_new_arrival == True,
            Product.created_at >= month_ago
        ).group_by(Product.category).all()
        
        stats['categories'] = [{'name': cat[0], 'count': cat[1]} for cat in categories]
        
        return jsonify({'success': True, 'stats': stats})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})



@app.route('/sales-reports')
@require_login
def sales_reports():
    """Comprehensive sales reports dashboard"""
    from datetime import datetime, timedelta
    from sqlalchemy import func, text
    
    # Default date range (last 7 days)
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    try:
        # Calculate key metrics
        metrics = calculate_sales_metrics(start_date, end_date)
        
        # Get top products data
        top_products = get_top_products_data(start_date, end_date)
        
        # Get daily sales data
        daily_sales = get_daily_sales_data(start_date, end_date)
        
        # Get revenue trend data for chart
        revenue_labels, revenue_data = get_revenue_trend_data(start_date, end_date)
        
        # Get category performance data
        category_labels, category_data = get_category_performance_data(start_date, end_date)
        
        # Customer insights
        customer_insights = get_customer_insights(start_date, end_date)
        
        return render_template('sales_reports.html',
                             start_date=start_date.strftime('%Y-%m-%d'),
                             end_date=end_date.strftime('%Y-%m-%d'),
                             total_revenue=metrics['total_revenue'],
                             revenue_growth=metrics['revenue_growth'],
                             total_orders=metrics['total_orders'],
                             orders_growth=metrics['orders_growth'],
                             avg_order_value=metrics['avg_order_value'],
                             aov_growth=metrics['aov_growth'],
                             unique_customers=metrics['unique_customers'],
                             customers_growth=metrics['customers_growth'],
                             top_products=top_products,
                             daily_sales=daily_sales,
                             revenue_labels=revenue_labels,
                             revenue_data=revenue_data,
                             category_labels=category_labels,
                             category_data=category_data,
                             new_customers=customer_insights['new_customers'],
                             returning_customers=customer_insights['returning_customers'],
                             customer_retention_rate=customer_insights['retention_rate'],
                             avg_orders_per_customer=customer_insights['avg_orders_per_customer'])
                             
    except Exception as e:
        app.logger.error(f"Error loading sales reports: {e}")
        flash(f'Error loading sales reports: {str(e)}', 'error')
        return render_template('sales_reports.html',
                             start_date=start_date.strftime('%Y-%m-%d'),
                             end_date=end_date.strftime('%Y-%m-%d'),
                             total_revenue=0, revenue_growth=0,
                             total_orders=0, orders_growth=0,
                             avg_order_value=0, aov_growth=0,
                             unique_customers=0, customers_growth=0,
                             top_products=[], daily_sales=[],
                             revenue_labels=[], revenue_data=[],
                             category_labels=[], category_data=[],
                             new_customers=0, returning_customers=0,
                             customer_retention_rate=0, avg_orders_per_customer=0)

@app.route('/api/sales-reports', methods=['POST'])
@require_login
def api_sales_reports():
    """API endpoint for updating sales reports with custom date range"""
    try:
        data = request.get_json()
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
        
        # Calculate metrics for the new date range
        metrics = calculate_sales_metrics(start_date, end_date)
        
        # Get chart data
        revenue_labels, revenue_data = get_revenue_trend_data(start_date, end_date)
        category_labels, category_data = get_category_performance_data(start_date, end_date)
        
        return jsonify({
            'success': True,
            'total_revenue': metrics['total_revenue'],
            'revenue_growth': metrics['revenue_growth'],
            'total_orders': metrics['total_orders'],
            'orders_growth': metrics['orders_growth'],
            'avg_order_value': metrics['avg_order_value'],
            'aov_growth': metrics['aov_growth'],
            'unique_customers': metrics['unique_customers'],
            'customers_growth': metrics['customers_growth'],
            'revenue_labels': revenue_labels,
            'revenue_data': revenue_data,
            'category_labels': category_labels,
            'category_data': category_data
        })
        
    except Exception as e:
        app.logger.error(f"Error updating sales reports: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/export-sales-report')
@require_login
def export_sales_report():
    """Export sales report in CSV or PDF format"""
    try:
        format_type = request.args.get('format', 'csv')
        start_date = datetime.strptime(request.args.get('start_date'), '%Y-%m-%d')
        end_date = datetime.strptime(request.args.get('end_date'), '%Y-%m-%d')
        
        if format_type == 'csv':
            return export_sales_csv(start_date, end_date)
        elif format_type == 'pdf':
            return export_sales_pdf(start_date, end_date)
        else:
            return jsonify({'error': 'Invalid format'}), 400
            
    except Exception as e:
        app.logger.error(f"Error exporting sales report: {e}")
        return jsonify({'error': str(e)}), 500

def calculate_sales_metrics(start_date, end_date):
    """Calculate key sales metrics for the given date range"""
    try:
        # Current period metrics
        current_orders = Order.query.filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).all()
        
        current_revenue = sum(order.total_amount for order in current_orders)
        current_order_count = len(current_orders)
        current_avg_order_value = current_revenue / current_order_count if current_order_count > 0 else 0
        
        # Get unique customers
        unique_customers = len(set(order.user_id for order in current_orders))
        
        # Previous period for comparison
        period_diff = end_date - start_date
        prev_start = start_date - period_diff
        prev_end = start_date
        
        prev_orders = Order.query.filter(
            Order.created_at >= prev_start,
            Order.created_at <= prev_end,
            Order.status == 'delivered'
        ).all()
        
        prev_revenue = sum(order.total_amount for order in prev_orders)
        prev_order_count = len(prev_orders)
        prev_avg_order_value = prev_revenue / prev_order_count if prev_order_count > 0 else 0
        prev_unique_customers = len(set(order.user_id for order in prev_orders))
        
        # Calculate growth percentages
        revenue_growth = calculate_growth_percentage(current_revenue, prev_revenue)
        orders_growth = calculate_growth_percentage(current_order_count, prev_order_count)
        aov_growth = calculate_growth_percentage(current_avg_order_value, prev_avg_order_value)
        customers_growth = calculate_growth_percentage(unique_customers, prev_unique_customers)
        
        return {
            'total_revenue': int(current_revenue),
            'revenue_growth': revenue_growth,
            'total_orders': current_order_count,
            'orders_growth': orders_growth,
            'avg_order_value': int(current_avg_order_value),
            'aov_growth': aov_growth,
            'unique_customers': unique_customers,
            'customers_growth': customers_growth
        }
        
    except Exception as e:
        app.logger.error(f"Error calculating sales metrics: {e}")
        return {
            'total_revenue': 0, 'revenue_growth': 0,
            'total_orders': 0, 'orders_growth': 0,
            'avg_order_value': 0, 'aov_growth': 0,
            'unique_customers': 0, 'customers_growth': 0
        }

def calculate_growth_percentage(current, previous):
    """Calculate growth percentage between two values"""
    if previous == 0:
        return 100 if current > 0 else 0
    return round(((current - previous) / previous) * 100, 1)

def get_top_products_data(start_date, end_date, limit=10):
    """Get top performing products by revenue"""
    try:
        # Query to get top products with sales data
        top_products_query = db.session.query(
            Product,
            func.sum(OrderItem.quantity).label('quantity_sold'),
            func.sum(OrderItem.quantity * Product.price).label('total_revenue'),
            func.avg(ProductReview.rating).label('avg_rating')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).outerjoin(
            ProductReview, Product.id == ProductReview.product_id
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).group_by(
            Product.id
        ).order_by(
            func.sum(OrderItem.quantity * Product.price).desc()
        ).limit(limit)
        
        results = top_products_query.all()
        
        top_products = []
        for product, quantity_sold, total_revenue, avg_rating in results:
            top_products.append({
                'id': product.id,
                'name': product.name,
                'category': product.category,
                'price': product.price,
                'image_url': product.image_url,
                'quantity_sold': quantity_sold or 0,
                'total_revenue': total_revenue or 0,
                'avg_rating': avg_rating or 0
            })
        
        return top_products
        
    except Exception as e:
        app.logger.error(f"Error getting top products data: {e}")
        return []

def get_daily_sales_data(start_date, end_date):
    """Get daily sales breakdown for the date range"""
    try:
        daily_sales = db.session.query(
            func.date(Order.created_at).label('date'),
            func.count(Order.id).label('orders'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at).desc()
        ).all()
        
        return [{
            'date': result.date,
            'orders': result.orders,
            'revenue': result.revenue or 0
        } for result in daily_sales]
        
    except Exception as e:
        app.logger.error(f"Error getting daily sales data: {e}")
        return []

def get_revenue_trend_data(start_date, end_date):
    """Get revenue trend data for chart"""
    try:
        daily_revenue = db.session.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at)
        ).all()
        
        labels = []
        data = []
        
        for result in daily_revenue:
            labels.append(result.date.strftime('%m/%d'))
            data.append(float(result.revenue or 0))
        
        return labels, data
        
    except Exception as e:
        app.logger.error(f"Error getting revenue trend data: {e}")
        return [], []

def get_category_performance_data(start_date, end_date):
    """Get category performance data for pie chart"""
    try:
        category_revenue = db.session.query(
            Product.category,
            func.sum(OrderItem.quantity * Product.price).label('revenue')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).group_by(
            Product.category
        ).order_by(
            func.sum(OrderItem.quantity * Product.price).desc()
        ).limit(7).all()
        
        labels = []
        data = []
        
        for category, revenue in category_revenue:
            labels.append(category)
            data.append(float(revenue or 0))
        
        return labels, data
        
    except Exception as e:
        app.logger.error(f"Error getting category performance data: {e}")
        return [], []

def get_customer_insights(start_date, end_date):
    """Get customer insights and retention metrics"""
    try:
        # New customers (first order in this period)
        new_customers = db.session.query(
            func.count(func.distinct(Order.user_id))
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered',
            ~Order.user_id.in_(
                db.session.query(Order.user_id).filter(
                    Order.created_at < start_date,
                    Order.status == 'delivered'
                )
            )
        ).scalar() or 0
        
        # Returning customers
        total_customers = db.session.query(
            func.count(func.distinct(Order.user_id))
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).scalar() or 0
        
        returning_customers = total_customers - new_customers
        
        # Retention rate (customers who made multiple orders)
        repeat_customers = db.session.query(
            func.count(func.distinct(Order.user_id))
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).having(
            func.count(Order.id) > 1
        ).group_by(
            Order.user_id
        ).count()
        
        retention_rate = round((repeat_customers / total_customers * 100), 1) if total_customers > 0 else 0
        
        # Average orders per customer
        total_orders = db.session.query(
            func.count(Order.id)
        ).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status == 'delivered'
        ).scalar() or 0
        
        avg_orders_per_customer = round(total_orders / total_customers, 1) if total_customers > 0 else 0
        
        return {
            'new_customers': new_customers,
            'returning_customers': returning_customers,
            'retention_rate': retention_rate,
            'avg_orders_per_customer': avg_orders_per_customer
        }
        
    except Exception as e:
        app.logger.error(f"Error getting customer insights: {e}")
        return {
            'new_customers': 0,
            'returning_customers': 0,
            'retention_rate': 0,
            'avg_orders_per_customer': 0
        }

def export_sales_csv(start_date, end_date):
    """Export sales report as CSV"""
    import csv
    from io import StringIO
    
    try:
        output = StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['Date', 'Orders', 'Revenue', 'Average Order Value'])
        
        # Get daily sales data
        daily_sales = get_daily_sales_data(start_date, end_date)
        
        for day in daily_sales:
            avg_order_value = day['revenue'] / day['orders'] if day['orders'] > 0 else 0
            writer.writerow([
                day['date'].strftime('%Y-%m-%d'),
                day['orders'],
                day['revenue'],
                round(avg_order_value, 2)
            ])
        
        output.seek(0)
        
        response = make_response(output.getvalue())
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.csv'
        
        return response
        
    except Exception as e:
        app.logger.error(f"Error exporting CSV: {e}")
        return jsonify({'error': str(e)}), 500

def export_sales_pdf(start_date, end_date):
    """Export sales report as PDF (simplified version)"""
    try:
        # For now, return a simple text-based PDF export
        # In production, you might want to use libraries like ReportLab
        
        metrics = calculate_sales_metrics(start_date, end_date)
        top_products = get_top_products_data(start_date, end_date, 5)
        
        report_content = f"""
SALES REPORT
Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}

KEY METRICS:
- Total Revenue: ₩{metrics['total_revenue']:,}
- Total Orders: {metrics['total_orders']}
- Average Order Value: ₩{metrics['avg_order_value']:,}
- Unique Customers: {metrics['unique_customers']}

TOP PRODUCTS:
"""
        
        for i, product in enumerate(top_products, 1):
            report_content += f"{i}. {product['name']} - ₩{product['total_revenue']:,} ({product['quantity_sold']} sold)\n"
        
        response = make_response(report_content)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = f'attachment; filename=sales_report_{start_date.strftime("%Y%m%d")}_{end_date.strftime("%Y%m%d")}.txt'
        
        return response
        
    except Exception as e:
        app.logger.error(f"Error exporting PDF: {e}")
        return jsonify({'error': str(e)}), 500

@app.errorhandler(403)
def forbidden_error(error):
    """Handle 403 errors"""
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found_error(error):
    """Handle 404 errors"""
    return render_template('base.html', 
                         error_message="Content not found",
                         error_description="The content you're looking for doesn't exist."), 404

@app.route('/user-views-analytics')
@require_login
def user_views_analytics():
    """Comprehensive user views analytics dashboard"""
    try:
        # Get date range from query parameters
        days = request.args.get('days', 30, type=int)
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Get product view analytics
        product_views = ProductView.query.filter(
            ProductView.viewed_at >= start_date
        ).all()
        
        # Get content view analytics  
        content_views = ContentView.query.filter(
            ContentView.viewed_at >= start_date
        ).all()
        
        # Get session analytics
        user_sessions = UserSession.query.filter(
            UserSession.started_at >= start_date
        ).all()
        
        # Calculate product metrics
        product_metrics = []
        products = Product.query.filter_by(is_active=True).all()
        
        for product in products:
            p_views = [v for v in product_views if v.product_id == product.id]
            if p_views:
                unique_viewers = len(set(v.user_id for v in p_views))
                avg_duration = sum(v.view_duration for v in p_views if v.view_duration) / len(p_views)
                engagement_rate = len([v for v in p_views if v.scroll_depth > 0.5 or v.clicked_images]) / len(p_views) * 100
                
                product_metrics.append({
                    'id': product.id,
                    'name': product.name,
                    'category': product.category,
                    'total_views': len(p_views),
                    'unique_viewers': unique_viewers,
                    'avg_duration': round(avg_duration, 2),
                    'engagement_rate': round(engagement_rate, 2),
                    'seller': product.seller.first_name if product.seller else 'Unknown'
                })
        
        # Sort by total views
        product_metrics.sort(key=lambda x: x['total_views'], reverse=True)
        
        # Calculate daily analytics
        daily_analytics = []
        for i in range(days):
            date = start_date + timedelta(days=i)
            day_product_views = [v for v in product_views if v.viewed_at.date() == date.date()]
            day_content_views = [v for v in content_views if v.viewed_at.date() == date.date()]
            day_sessions = [s for s in user_sessions if s.started_at.date() == date.date()]
            
            daily_analytics.append({
                'date': date.strftime('%Y-%m-%d'),
                'product_views': len(day_product_views),
                'content_views': len(day_content_views),
                'unique_users': len(set([v.user_id for v in day_product_views + day_content_views])),
                'sessions': len(day_sessions),
                'avg_session_duration': round(sum(s.duration_minutes for s in day_sessions) / len(day_sessions), 2) if day_sessions else 0
            })
        
        # Device analytics
        device_breakdown = {'desktop': 0, 'mobile': 0, 'tablet': 0}
        for session in user_sessions:
            if session.device_type in device_breakdown:
                device_breakdown[session.device_type] += 1
        
        # Browser analytics
        browser_breakdown = {}
        for session in user_sessions:
            browser = session.browser or 'Unknown'
            browser_breakdown[browser] = browser_breakdown.get(browser, 0) + 1
        
        # Top referrers
        referrer_breakdown = {}
        for view in product_views + content_views:
            if view.referrer:
                domain = view.referrer.split('/')[2] if '/' in view.referrer else view.referrer
                referrer_breakdown[domain] = referrer_breakdown.get(domain, 0) + 1
        
        # Overall statistics
        total_product_views = len(product_views)
        total_content_views = len(content_views)
        total_unique_users = len(set([v.user_id for v in product_views + content_views]))
        total_sessions = len(user_sessions)
        avg_session_duration = sum(s.duration_minutes for s in user_sessions) / len(user_sessions) if user_sessions else 0
        
        return render_template('user_views_analytics.html',
                             product_metrics=product_metrics[:15],
                             daily_analytics=daily_analytics,
                             device_breakdown=device_breakdown,
                             browser_breakdown=dict(sorted(browser_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]),
                             referrer_breakdown=dict(sorted(referrer_breakdown.items(), key=lambda x: x[1], reverse=True)[:10]),
                             total_product_views=total_product_views,
                             total_content_views=total_content_views,
                             total_unique_users=total_unique_users,
                             total_sessions=total_sessions,
                             avg_session_duration=round(avg_session_duration, 2),
                             days=days)
    except Exception as e:
        app.logger.error(f"Error in user views analytics: {e}")
        flash('Error loading user views analytics', 'error')
        return redirect(url_for('index'))

# API Endpoints for User Engagement Tracking

@app.route('/api/track-engagement', methods=['POST'])
def track_engagement():
    """API endpoint to track user engagement metrics"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        engagement_type = data.get('type')  # 'product' or 'content'
        item_id = data.get('item_id')
        engagement_data = {
            'duration': data.get('duration', 0),
            'scroll_depth': data.get('scroll_depth', 0.0),
            'clicked_images': data.get('clicked_images', False),
            'viewed_reviews': data.get('viewed_reviews', False),
            'read_percentage': data.get('read_percentage', 0.0)
        }
        
        if engagement_type == 'product' and item_id:
            # Update existing product view with engagement data
            user_id = current_user.id if current_user.is_authenticated else get_user_id()
            session_id = get_session_id()
            
            # Find the most recent product view for this user/session
            product_view = ProductView.query.filter_by(
                user_id=user_id,
                product_id=item_id,
                session_id=session_id
            ).order_by(ProductView.viewed_at.desc()).first()
            
            if product_view:
                product_view.view_duration = engagement_data['duration']
                product_view.scroll_depth = engagement_data['scroll_depth']
                product_view.clicked_images = engagement_data['clicked_images']
                product_view.viewed_reviews = engagement_data['viewed_reviews']
                db.session.commit()
        
        elif engagement_type == 'content' and item_id:
            # Update existing content view with engagement data
            user_id = current_user.id if current_user.is_authenticated else get_user_id()
            session_id = get_session_id()
            
            # Find the most recent content view for this user/session
            content_view = ContentView.query.filter_by(
                user_id=user_id,
                content_id=item_id,
                session_id=session_id
            ).order_by(ContentView.viewed_at.desc()).first()
            
            if content_view:
                content_view.view_duration = engagement_data['duration']
                content_view.scroll_depth = engagement_data['scroll_depth']
                content_view.read_percentage = engagement_data['read_percentage']
                db.session.commit()
        
        return jsonify({'success': True, 'message': 'Engagement tracked successfully'})
    
    except Exception as e:
        app.logger.error(f"Error tracking engagement: {e}")
        return jsonify({'error': 'Failed to track engagement'}), 500

@app.route('/api/session-heartbeat', methods=['POST'])
def session_heartbeat():
    """API endpoint to update session activity"""
    try:
        session_id = get_session_id()
        user_id = current_user.id if current_user.is_authenticated else get_user_id()
        
        # Update session last activity
        user_session = UserSession.query.filter_by(session_id=session_id).first()
        if user_session:
            user_session.last_activity = datetime.utcnow()
            db.session.commit()
        
        return jsonify({'success': True})
    
    except Exception as e:
        app.logger.error(f"Error updating session heartbeat: {e}")
        return jsonify({'error': 'Failed to update session'}), 500

# Newsletter Routes

@app.route('/newsletter/subscribe', methods=['GET', 'POST'])
def newsletter_subscribe():
    """Newsletter subscription form with fashion preferences"""
    form = NewsletterSubscriptionForm()
    
    if form.validate_on_submit():
        try:
            # Check if email already exists
            existing_subscription = NewsletterSubscription.query.filter_by(
                email=form.email.data
            ).first()
            
            if existing_subscription and existing_subscription.is_active:
                flash(get_translation('newsletter_already_subscribed'), 'warning')
                return redirect(url_for('newsletter_subscribe'))
            
            # Create new subscription
            subscription = NewsletterSubscription()
            subscription.email = form.email.data
            subscription.first_name = form.first_name.data
            subscription.preferred_categories = ','.join(form.preferred_categories.data)
            subscription.style_preferences = ','.join(form.style_preferences.data)
            subscription.size_range = form.size_range.data
            subscription.budget_range = form.budget_range.data
            subscription.color_preferences = ','.join(form.color_preferences.data) if form.color_preferences.data else None
            subscription.frequency = form.frequency.data
            subscription.user_id = current_user.id if current_user.is_authenticated else None
            subscription.is_active = True
            subscription.subscription_date = datetime.utcnow()
            
            db.session.add(subscription)
            db.session.commit()
            
            # Send welcome email
            try:
                newsletter_service.send_welcome_email(subscription)
                flash(get_translation('newsletter_subscribed_success'), 'success')
            except Exception as e:
                app.logger.error(f"Error sending welcome email: {e}")
                flash(get_translation('newsletter_subscribed_no_email'), 'warning')
            
            return redirect(url_for('index'))
            
        except Exception as e:
            app.logger.error(f"Error creating newsletter subscription: {e}")
            flash(get_translation('error_occurred'), 'error')
            db.session.rollback()
    
    return render_template('newsletter_subscribe.html', form=form)

@app.route('/newsletter/unsubscribe/<token>')
def newsletter_unsubscribe(token):
    """Unsubscribe from newsletter using token"""
    try:
        subscription = NewsletterSubscription.query.filter_by(
            unsubscribe_token=token
        ).first()
        
        if not subscription:
            flash(get_translation('invalid_unsubscribe_link'), 'error')
            return redirect(url_for('index'))
        
        subscription.is_active = False
        subscription.unsubscribed_at = datetime.utcnow()
        db.session.commit()
        
        flash(get_translation('newsletter_unsubscribed'), 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        app.logger.error(f"Error unsubscribing from newsletter: {e}")
        flash(get_translation('error_occurred'), 'error')
        return redirect(url_for('index'))

@app.route('/newsletter/preview/<int:newsletter_id>')
@require_login
def newsletter_preview(newsletter_id):
    """Preview newsletter before sending (admin only)"""
    try:
        newsletter = FashionNewsletter.query.get_or_404(newsletter_id)
        
        # Generate preview data
        preview_data = newsletter_service.generate_newsletter_preview(newsletter)
        
        return render_template('newsletter_preview.html', 
                             newsletter=newsletter,
                             preview_data=preview_data)
        
    except Exception as e:
        app.logger.error(f"Error previewing newsletter: {e}")
        flash(get_translation('error_occurred'), 'error')
        return redirect(url_for('index'))

@app.route('/newsletter/send/<int:newsletter_id>', methods=['POST'])
@require_login
def send_newsletter(newsletter_id):
    """Send newsletter to all subscribers"""
    try:
        newsletter = FashionNewsletter.query.get_or_404(newsletter_id)
        
        if newsletter.sent_at:
            flash('Newsletter has already been sent', 'warning')
            return redirect(url_for('newsletter_preview', newsletter_id=newsletter_id))
        
        # Send newsletter using background task or immediate send
        result = newsletter_service.send_newsletter(newsletter)
        
        if result['success']:
            flash(f"Newsletter sent successfully to {result['sent_count']} subscribers", 'success')
        else:
            flash(f"Newsletter sending completed with {result['error_count']} errors", 'warning')
        
        return redirect(url_for('newsletter_analytics'))
        
    except Exception as e:
        app.logger.error(f"Error sending newsletter: {e}")
        flash(get_translation('error_occurred'), 'error')
        return redirect(url_for('index'))

@app.route('/newsletter/analytics')
@require_login
def newsletter_analytics():
    """Newsletter analytics dashboard"""
    try:
        # Get newsletter statistics
        total_subscribers = NewsletterSubscription.query.filter_by(is_active=True).count()
        total_sent = FashionNewsletter.query.filter(FashionNewsletter.sent_at.isnot(None)).count()
        
        # Recent newsletters
        recent_newsletters = FashionNewsletter.query.order_by(
            FashionNewsletter.created_at.desc()
        ).limit(10).all()
        
        # Subscription analytics
        subscription_data = db.session.query(
            func.date(NewsletterSubscription.subscription_date).label('date'),
            func.count(NewsletterSubscription.id).label('count')
        ).filter(
            NewsletterSubscription.subscription_date >= datetime.utcnow() - timedelta(days=30)
        ).group_by(
            func.date(NewsletterSubscription.subscription_date)
        ).order_by(
            func.date(NewsletterSubscription.subscription_date)
        ).all()
        
        # Category preferences
        category_stats = {}
        active_subscriptions = NewsletterSubscription.query.filter_by(is_active=True).all()
        
        for subscription in active_subscriptions:
            if subscription.preferred_categories:
                categories = subscription.preferred_categories.split(',')
                for category in categories:
                    category = category.strip()
                    category_stats[category] = category_stats.get(category, 0) + 1
        
        # Newsletter performance
        newsletter_analytics = NewsletterAnalytics.query.join(
            FashionNewsletter
        ).order_by(FashionNewsletter.sent_at.desc()).limit(5).all()
        
        return render_template('newsletter_analytics.html',
                             total_subscribers=total_subscribers,
                             total_sent=total_sent,
                             recent_newsletters=recent_newsletters,
                             subscription_data=subscription_data,
                             category_stats=category_stats,
                             newsletter_analytics=newsletter_analytics)
        
    except Exception as e:
        app.logger.error(f"Error in newsletter analytics: {e}")
        flash(get_translation('error_occurred'), 'error')
        return redirect(url_for('index'))

@app.route('/newsletter/create', methods=['GET', 'POST'])
@require_login
def create_newsletter():
    """Create a new fashion newsletter"""
    if request.method == 'POST':
        try:
            # Get form data
            subject = request.form.get('subject')
            template_type = request.form.get('template_type', 'weekly_inspiration')
            
            if not subject:
                flash('Newsletter subject is required', 'error')
                return redirect(url_for('create_newsletter'))
            
            # Create newsletter
            newsletter = FashionNewsletter()
            newsletter.subject = subject
            newsletter.template_type = template_type
            newsletter.created_by = current_user.id
            newsletter.created_at = datetime.utcnow()
            
            # Generate content based on template type
            newsletter.content = newsletter_service.generate_newsletter_content(template_type)
            
            db.session.add(newsletter)
            db.session.commit()
            
            flash('Newsletter created successfully', 'success')
            return redirect(url_for('newsletter_preview', newsletter_id=newsletter.id))
            
        except Exception as e:
            app.logger.error(f"Error creating newsletter: {e}")
            flash(get_translation('error_occurred'), 'error')
            db.session.rollback()
    
    return render_template('create_newsletter.html')

@app.route('/api/story/<int:story_id>/like', methods=['POST'])
@csrf.exempt
def api_story_like(story_id):
    """API endpoint to like a story"""
    try:
        story = Story.query.get_or_404(story_id)
        story.increment_likes()
        
        # Track user interaction for recommendation algorithm
        if current_user.is_authenticated:
            track_story_interaction(current_user.id, story_id, 'like')
        
        return jsonify({
            'success': True,
            'likes': story.like_count,
            'message': 'Story liked successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error liking story: {str(e)}'
        }), 500

@app.route('/api/story/<int:story_id>/view', methods=['POST'])
@csrf.exempt
def api_story_view(story_id):
    """API endpoint to track story view"""
    try:
        story = Story.query.get_or_404(story_id)
        story.increment_views()
        
        # Track user interaction for recommendation algorithm
        if current_user.is_authenticated:
            track_story_interaction(current_user.id, story_id, 'view')
        
        return jsonify({
            'success': True,
            'views': story.view_count,
            'message': 'Story view tracked'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error tracking view: {str(e)}'
        }), 500

@app.route('/api/stories/next/<int:current_story_id>')
def api_get_next_stories(current_story_id):
    """Get next recommended stories based on current story"""
    try:
        # Get current story
        current_story = Story.query.get_or_404(current_story_id)
        
        # Get all active stories except current one
        all_stories = Story.get_active_stories(limit=50)
        remaining_stories = [s for s in all_stories if s.id != current_story_id]
        
        # Apply recommendation algorithm
        if current_user.is_authenticated:
            recommended_stories = get_personalized_story_recommendations(current_user.id, remaining_stories)
        else:
            recommended_stories = get_trending_story_recommendations(remaining_stories)
        
        # Return top 10 recommended stories
        next_stories = recommended_stories[:10]
        
        stories_data = []
        for story in next_stories:
            stories_data.append({
                'id': story.id,
                'title': story.get_localized_title(session.get('language', 'en')),
                'content': story.get_localized_content(session.get('language', 'en')),
                'image_url': story.image_url,
                'story_type': story.story_type,
                'author_name': story.author_name,
                'view_count': story.view_count,
                'like_count': story.like_count,
                'click_count': story.click_count,
                'time_remaining': story.time_remaining_korean(),
                'is_expired': story.is_expired(),
                'linked_product_id': story.linked_product_id,
                'background_color': story.background_color or '#007bff'
            })
        
        return jsonify({
            'success': True,
            'stories': stories_data
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error getting recommendations: {str(e)}'
        }), 500

def track_story_interaction(user_id, story_id, interaction_type):
    """Track story interactions for recommendation algorithm"""
    try:
        # Create a story interaction record for learning
        # This data will be used to improve future recommendations
        
        # For now, we'll log the interaction and potentially store in user interaction table
        print(f"Story interaction tracked: User {user_id}, Story {story_id}, Type {interaction_type}")
        
        # In future iterations, could create dedicated StoryInteraction table:
        # story_interaction = StoryInteraction()
        # story_interaction.user_id = user_id
        # story_interaction.story_id = story_id
        # story_interaction.interaction_type = interaction_type
        # story_interaction.created_at = datetime.now()
        # db.session.add(story_interaction)
        # db.session.commit()
        
    except Exception as e:
        print(f"Error tracking story interaction: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

"""
Fashion Newsletter Service
Handles newsletter generation, personalization, and delivery
"""

import os
import uuid
import secrets
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from flask import render_template_string, url_for
from app import db
from models import (
    NewsletterSubscription, FashionNewsletter, NewsletterAnalytics,
    Product, User
)

class FashionNewsletterService:
    """Service for managing fashion newsletter campaigns"""
    
    def __init__(self):
        self.sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')
        
    def create_subscription(self, email: str, preferences: Dict[str, Any], 
                          user_id: Optional[str] = None) -> NewsletterSubscription:
        """Create a new newsletter subscription with preferences"""
        
        # Generate unique subscription token
        subscription_token = secrets.token_urlsafe(32)
        
        subscription = NewsletterSubscription()
        subscription.email = email
        subscription.user_id = user_id
        subscription.first_name = preferences.get('first_name', '')
        subscription.preferred_categories = preferences.get('categories', ['Clothing', 'Accessories'])
        subscription.style_preferences = preferences.get('styles', ['casual', 'trendy'])
        subscription.size_range = preferences.get('size_range', 'M')
        subscription.budget_range = preferences.get('budget_range', 'mid-range')
        subscription.color_preferences = preferences.get('colors', ['black', 'white', 'blue'])
        subscription.frequency = preferences.get('frequency', 'weekly')
        subscription.subscription_token = subscription_token
        
        db.session.add(subscription)
        db.session.commit()
        
        return subscription
    
    def generate_personalized_content(self, subscription: NewsletterSubscription) -> Dict[str, Any]:
        """Generate personalized fashion content for a subscriber"""
        
        # Get products matching subscriber preferences
        featured_products = self._get_personalized_products(subscription)
        
        # Get trending items in preferred categories
        trending_items = self._get_trending_products(subscription.preferred_categories)
        
        # Generate style tips based on preferences
        style_tips = self._generate_style_tips(subscription)
        
        # Get seasonal recommendations
        seasonal_items = self._get_seasonal_recommendations()
        
        # Create content structure
        content = {
            'subscriber_name': subscription.first_name or 'Fashion Lover',
            'featured_products': featured_products,
            'trending_items': trending_items,
            'style_tips': style_tips,
            'seasonal_items': seasonal_items,
            'categories': subscription.preferred_categories,
            'style_preferences': subscription.style_preferences,
            'unsubscribe_url': self._generate_unsubscribe_url(subscription.subscription_token)
        }
        
        return content
    
    def _get_personalized_products(self, subscription: NewsletterSubscription) -> List[Dict[str, Any]]:
        """Get products personalized for subscriber preferences"""
        
        # Query products based on preferences
        query = db.session.query(Product).filter(Product.is_active == True)
        
        # Filter by preferred categories
        if subscription.preferred_categories:
            query = query.filter(Product.category.in_(subscription.preferred_categories))
        
        # Filter by budget range
        if subscription.budget_range:
            if subscription.budget_range == 'budget':
                query = query.filter(Product.price <= 50)
            elif subscription.budget_range == 'mid-range':
                query = query.filter(Product.price.between(50, 200))
            elif subscription.budget_range == 'luxury':
                query = query.filter(Product.price >= 200)
        
        # Get recent products first
        products = query.order_by(Product.created_at.desc()).limit(6).all()
        
        return [self._format_product_for_newsletter(product) for product in products]
    
    def _get_trending_products(self, categories: List[str]) -> List[Dict[str, Any]]:
        """Get trending products in specified categories"""
        
        # Get products with high view counts (simulating trending)
        trending_products = db.session.query(Product).filter(
            Product.is_active == True,
            Product.category.in_(categories) if categories else True
        ).order_by(Product.created_at.desc()).limit(4).all()
        
        return [self._format_product_for_newsletter(product) for product in trending_products]
    
    def _get_seasonal_recommendations(self) -> List[Dict[str, Any]]:
        """Get seasonal product recommendations"""
        
        # Determine current season
        current_month = datetime.now().month
        if current_month in [12, 1, 2]:
            season = 'winter'
        elif current_month in [3, 4, 5]:
            season = 'spring'
        elif current_month in [6, 7, 8]:
            season = 'summer'
        else:
            season = 'fall'
        
        # Get seasonal products
        seasonal_products = db.session.query(Product).filter(
            Product.is_active == True,
            Product.is_seasonal == True,
            Product.season_type == season
        ).limit(3).all()
        
        return [self._format_product_for_newsletter(product) for product in seasonal_products]
    
    def _generate_style_tips(self, subscription: NewsletterSubscription) -> List[Dict[str, str]]:
        """Generate style tips based on subscriber preferences"""
        
        tips = []
        style_prefs = subscription.style_preferences or ['casual']
        
        style_tips_database = {
            'casual': [
                {
                    'title': 'Effortless Everyday Style',
                    'content': 'Mix comfortable basics with one statement piece for an elevated casual look.'
                },
                {
                    'title': 'Layering Mastery',
                    'content': 'Master the art of layering with lightweight cardigans and versatile scarves.'
                }
            ],
            'formal': [
                {
                    'title': 'Power Dressing',
                    'content': 'Choose well-tailored pieces in neutral colors for a professional, confident appearance.'
                },
                {
                    'title': 'Evening Elegance',
                    'content': 'Elevate your evening look with metallic accessories and classic silhouettes.'
                }
            ],
            'trendy': [
                {
                    'title': 'Trend Spotting',
                    'content': 'Incorporate one trending piece into your existing wardrobe for a fresh, modern look.'
                },
                {
                    'title': 'Color of the Season',
                    'content': 'Experiment with seasonal color palettes to stay current with fashion trends.'
                }
            ],
            'vintage': [
                {
                    'title': 'Timeless Pieces',
                    'content': 'Invest in classic vintage-inspired pieces that transcend seasonal trends.'
                },
                {
                    'title': 'Modern Vintage Mix',
                    'content': 'Pair vintage finds with contemporary accessories for a unique, personalized style.'
                }
            ]
        }
        
        # Select tips based on preferences
        for style in style_prefs:
            if style in style_tips_database:
                tips.extend(style_tips_database[style][:1])  # One tip per style
        
        # Add general tips if no specific style tips
        if not tips:
            tips = [
                {
                    'title': 'Color Coordination',
                    'content': 'Create cohesive outfits by choosing a color palette and sticking to it throughout your look.'
                }
            ]
        
        return tips[:3]  # Maximum 3 tips
    
    def _format_product_for_newsletter(self, product: Product) -> Dict[str, Any]:
        """Format product data for newsletter inclusion"""
        
        return {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'image_url': product.image_url,
            'category': product.category,
            'description': product.description[:100] + '...' if len(product.description) > 100 else product.description,
            'product_url': url_for('product_detail', product_id=product.id, _external=True),
            'is_new': product.is_new_arrival,
            'is_seasonal': product.is_seasonal
        }
    
    def _generate_unsubscribe_url(self, token: str) -> str:
        """Generate unsubscribe URL for newsletter"""
        return url_for('newsletter_unsubscribe', token=token, _external=True)
    
    def create_newsletter_campaign(self, title: str, newsletter_type: str = 'weekly_inspiration') -> FashionNewsletter:
        """Create a new newsletter campaign"""
        
        newsletter = FashionNewsletter()
        newsletter.title = title
        newsletter.subject_line = f"Your Weekly Fashion Inspiration - {title}"
        newsletter.newsletter_type = newsletter_type
        newsletter.status = 'draft'
        
        # Generate content template
        newsletter.content_html = self._generate_newsletter_template()
        
        db.session.add(newsletter)
        db.session.commit()
        
        return newsletter
    
    def _generate_newsletter_template(self) -> str:
        """Generate HTML template for newsletter"""
        
        template = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Fashion Inspiration Newsletter</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; }
                .container { max-width: 600px; margin: 0 auto; background: #ffffff; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .product-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin: 20px 0; }
                .product-card { border: 1px solid #eee; border-radius: 8px; overflow: hidden; text-decoration: none; color: inherit; }
                .product-image { width: 100%; height: 200px; object-fit: cover; }
                .product-info { padding: 15px; }
                .product-name { font-weight: bold; margin-bottom: 5px; }
                .product-price { color: #667eea; font-weight: bold; }
                .tips-section { background: #f8f9fa; padding: 20px; margin: 20px 0; border-radius: 8px; }
                .tip { margin-bottom: 15px; }
                .tip-title { font-weight: bold; color: #667eea; }
                .footer { background: #333; color: white; padding: 20px; text-align: center; font-size: 14px; }
                .unsubscribe { color: #ccc; text-decoration: none; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Fashion Inspiration</h1>
                    <p>Curated just for you, {{subscriber_name}}</p>
                </div>
                
                <div class="content">
                    <h2>Featured Picks For You</h2>
                    <div class="product-grid">
                        {% for product in featured_products %}
                        <a href="{{product.product_url}}" class="product-card">
                            {% if product.image_url %}
                            <img src="{{product.image_url}}" alt="{{product.name}}" class="product-image">
                            {% endif %}
                            <div class="product-info">
                                <div class="product-name">{{product.name}}</div>
                                <div class="product-price">${{product.price}}</div>
                            </div>
                        </a>
                        {% endfor %}
                    </div>
                    
                    <h2>Trending Now</h2>
                    <div class="product-grid">
                        {% for product in trending_items %}
                        <a href="{{product.product_url}}" class="product-card">
                            {% if product.image_url %}
                            <img src="{{product.image_url}}" alt="{{product.name}}" class="product-image">
                            {% endif %}
                            <div class="product-info">
                                <div class="product-name">{{product.name}}</div>
                                <div class="product-price">${{product.price}}</div>
                            </div>
                        </a>
                        {% endfor %}
                    </div>
                    
                    <div class="tips-section">
                        <h2>Style Tips Just For You</h2>
                        {% for tip in style_tips %}
                        <div class="tip">
                            <div class="tip-title">{{tip.title}}</div>
                            <div>{{tip.content}}</div>
                        </div>
                        {% endfor %}
                    </div>
                </div>
                
                <div class="footer">
                    <p>Thanks for being part of our fashion community!</p>
                    <p><a href="{{unsubscribe_url}}" class="unsubscribe">Unsubscribe</a></p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return template
    
    def send_newsletter_to_subscriber(self, newsletter: FashionNewsletter, 
                                    subscription: NewsletterSubscription) -> bool:
        """Send newsletter to a specific subscriber"""
        
        try:
            # Generate personalized content
            content_data = self.generate_personalized_content(subscription)
            
            # Render email content
            html_content = render_template_string(newsletter.content_html, **content_data)
            
            # Track sending event
            self._track_newsletter_event(newsletter.id, subscription.id, 'sent')
            
            # Update subscription stats
            subscription.total_emails_sent += 1
            subscription.last_sent = datetime.now()
            
            # Update newsletter stats
            newsletter.total_sent += 1
            
            db.session.commit()
            
            return True
            
        except Exception as e:
            print(f"Error sending newsletter: {e}")
            return False
    
    def send_weekly_newsletters(self) -> Dict[str, Any]:
        """Send weekly newsletters to all active subscribers"""
        
        # Get active weekly subscribers
        subscribers = db.session.query(NewsletterSubscription).filter(
            NewsletterSubscription.is_active == True,
            NewsletterSubscription.frequency == 'weekly'
        ).all()
        
        # Create or get this week's newsletter
        newsletter = self._get_or_create_weekly_newsletter()
        
        sent_count = 0
        failed_count = 0
        
        for subscription in subscribers:
            # Check if already sent this week
            if self._was_sent_this_week(subscription):
                continue
                
            success = self.send_newsletter_to_subscriber(newsletter, subscription)
            if success:
                sent_count += 1
            else:
                failed_count += 1
        
        # Update newsletter status
        newsletter.status = 'sent'
        newsletter.sent_at = datetime.now()
        db.session.commit()
        
        return {
            'newsletter_id': newsletter.id,
            'sent_count': sent_count,
            'failed_count': failed_count,
            'total_subscribers': len(subscribers)
        }
    
    def _get_or_create_weekly_newsletter(self) -> FashionNewsletter:
        """Get existing weekly newsletter or create new one"""
        
        # Check for existing newsletter this week
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        
        newsletter = db.session.query(FashionNewsletter).filter(
            FashionNewsletter.newsletter_type == 'weekly_inspiration',
            FashionNewsletter.created_at >= week_start,
            FashionNewsletter.status.in_(['draft', 'scheduled'])
        ).first()
        
        if not newsletter:
            # Create new weekly newsletter
            newsletter = self.create_newsletter_campaign(
                f"Fashion Inspiration - Week of {datetime.now().strftime('%B %d, %Y')}",
                'weekly_inspiration'
            )
        
        return newsletter
    
    def _was_sent_this_week(self, subscription: NewsletterSubscription) -> bool:
        """Check if newsletter was already sent to subscriber this week"""
        
        if not subscription.last_sent:
            return False
        
        week_start = datetime.now() - timedelta(days=datetime.now().weekday())
        return subscription.last_sent >= week_start
    
    def _track_newsletter_event(self, newsletter_id: int, subscription_id: int, 
                               event_type: str, event_data: Dict = None):
        """Track newsletter events for analytics"""
        
        analytics = NewsletterAnalytics()
        analytics.newsletter_id = newsletter_id
        analytics.subscription_id = subscription_id
        analytics.event_type = event_type
        analytics.event_data = event_data or {}
        
        db.session.add(analytics)
        db.session.commit()
    
    def unsubscribe(self, token: str) -> bool:
        """Unsubscribe user with given token"""
        
        subscription = db.session.query(NewsletterSubscription).filter(
            NewsletterSubscription.subscription_token == token,
            NewsletterSubscription.is_active == True
        ).first()
        
        if subscription:
            subscription.is_active = False
            subscription.unsubscribed_at = datetime.now()
            db.session.commit()
            return True
        
        return False
    
    def get_subscription_stats(self) -> Dict[str, Any]:
        """Get newsletter subscription statistics"""
        
        total_subscribers = db.session.query(NewsletterSubscription).filter(
            NewsletterSubscription.is_active == True
        ).count()
        
        weekly_subscribers = db.session.query(NewsletterSubscription).filter(
            NewsletterSubscription.is_active == True,
            NewsletterSubscription.frequency == 'weekly'
        ).count()
        
        monthly_subscribers = db.session.query(NewsletterSubscription).filter(
            NewsletterSubscription.is_active == True,
            NewsletterSubscription.frequency == 'monthly'
        ).count()
        
        # Get recent newsletter performance
        recent_newsletter = db.session.query(FashionNewsletter).filter(
            FashionNewsletter.status == 'sent'
        ).order_by(FashionNewsletter.sent_at.desc()).first()
        
        stats = {
            'total_subscribers': total_subscribers,
            'weekly_subscribers': weekly_subscribers,
            'monthly_subscribers': monthly_subscribers,
            'recent_newsletter': None
        }
        
        if recent_newsletter:
            open_rate = (recent_newsletter.total_opened / recent_newsletter.total_sent * 100) if recent_newsletter.total_sent > 0 else 0
            click_rate = (recent_newsletter.total_clicked / recent_newsletter.total_sent * 100) if recent_newsletter.total_sent > 0 else 0
            
            stats['recent_newsletter'] = {
                'title': recent_newsletter.title,
                'sent_at': recent_newsletter.sent_at,
                'total_sent': recent_newsletter.total_sent,
                'total_opened': recent_newsletter.total_opened,
                'total_clicked': recent_newsletter.total_clicked,
                'open_rate': round(open_rate, 2),
                'click_rate': round(click_rate, 2)
            }
        
        return stats
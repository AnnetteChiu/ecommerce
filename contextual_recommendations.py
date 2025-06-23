"""
Contextual Product Recommendation Engine
Displays product suggestions based on user interaction context
"""

import logging
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from typing import List, Dict, Any, Optional
from sqlalchemy import func, desc, and_
from app import db
from models import Product, UserInteraction, CartItem, Wishlist, Order, OrderItem, ProductReview

class ContextualRecommendationEngine:
    """Generate contextual product recommendations based on user interactions"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def get_contextual_suggestions(self, user_id: str, context: str, 
                                 current_product_id: Optional[int] = None,
                                 limit: int = 6) -> List[Dict[str, Any]]:
        """
        Get contextual product suggestions based on user interaction context
        
        Args:
            user_id: User identifier
            context: Context type (viewing, cart, checkout, search, etc.)
            current_product_id: Current product being viewed
            limit: Maximum number of suggestions
            
        Returns:
            List of contextual product recommendations
        """
        try:
            suggestions = []
            
            if context == 'product_view':
                suggestions = self._get_product_view_suggestions(user_id, current_product_id, limit)
            elif context == 'cart':
                suggestions = self._get_cart_based_suggestions(user_id, limit)
            elif context == 'checkout':
                suggestions = self._get_checkout_suggestions(user_id, limit)
            elif context == 'search':
                suggestions = self._get_search_based_suggestions(user_id, limit)
            elif context == 'category_browse':
                suggestions = self._get_category_browse_suggestions(user_id, limit)
            elif context == 'homepage':
                suggestions = self._get_homepage_suggestions(user_id, limit)
            elif context == 'wishlist':
                suggestions = self._get_wishlist_suggestions(user_id, limit)
            else:
                suggestions = self._get_general_suggestions(user_id, limit)
                
            return self._enrich_suggestions(suggestions)
            
        except Exception as e:
            self.logger.error(f"Error generating contextual suggestions: {e}")
            return self._get_fallback_suggestions(limit)
    
    def _get_product_view_suggestions(self, user_id: str, product_id: int, limit: int) -> List[Product]:
        """Get suggestions when viewing a product"""
        if not product_id:
            return []
            
        current_product = Product.query.get(product_id)
        if not current_product:
            return []
            
        suggestions = []
        
        # 1. Similar products in same category
        category_products = Product.query.filter(
            and_(
                Product.category == current_product.category,
                Product.id != product_id,
                Product.is_active == True
            )
        ).order_by(desc(Product.created_at)).limit(3).all()
        suggestions.extend(category_products)
        
        # 2. Products frequently bought together
        together_products = self._get_frequently_bought_together(product_id, limit//2)
        suggestions.extend(together_products)
        
        # 3. Products viewed by similar users
        similar_user_products = self._get_similar_user_products(user_id, product_id, limit//2)
        suggestions.extend(similar_user_products)
        
        return self._deduplicate_products(suggestions, limit)
    
    def _get_cart_based_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get suggestions based on cart contents"""
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        if not cart_items:
            return self._get_general_suggestions(user_id, limit)
        
        cart_categories = [item.product.category for item in cart_items if item.product]
        cart_product_ids = [item.product_id for item in cart_items]
        
        suggestions = []
        
        # 1. Complementary products for cart categories
        for category in set(cart_categories):
            complementary = self._get_complementary_products(category, cart_product_ids, limit//2)
            suggestions.extend(complementary)
        
        # 2. Products often bought with cart items
        for item in cart_items:
            together_products = self._get_frequently_bought_together(item.product_id, 2)
            suggestions.extend(together_products)
        
        return self._deduplicate_products(suggestions, limit)
    
    def _get_checkout_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get last-minute suggestions during checkout"""
        cart_items = CartItem.query.filter_by(user_id=user_id).all()
        
        suggestions = []
        
        # 1. Low-cost add-ons and accessories
        for item in cart_items:
            if item.product and item.product.category:
                accessories = Product.query.filter(
                    and_(
                        Product.category.in_(['Accessories', 'Add-ons']),
                        Product.price < 50,  # Low-cost items
                        Product.is_active == True
                    )
                ).limit(2).all()
                suggestions.extend(accessories)
        
        # 2. Digital products (courses, warranties)
        digital_products = Product.query.filter(
            and_(
                Product.category.in_(['Digital', 'Services', 'Warranties']),
                Product.price < 100,
                Product.is_active == True
            )
        ).limit(2).all()
        suggestions.extend(digital_products)
        
        return self._deduplicate_products(suggestions, limit)
    
    def _get_search_based_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get suggestions based on recent search history"""
        # Get recent user interactions that might indicate search behavior
        recent_views = UserInteraction.query.filter(
            and_(
                UserInteraction.user_id == user_id,
                UserInteraction.interaction_type == 'view',
                UserInteraction.timestamp >= datetime.now() - timedelta(days=7)
            )
        ).order_by(desc(UserInteraction.timestamp)).limit(10).all()
        
        if not recent_views:
            return self._get_general_suggestions(user_id, limit)
        
        # Analyze categories from recent views
        viewed_categories = [interaction.content.category for interaction in recent_views 
                           if hasattr(interaction, 'content') and interaction.content]
        
        category_counts = Counter(viewed_categories)
        top_categories = [cat for cat, _ in category_counts.most_common(3)]
        
        suggestions = []
        for category in top_categories:
            category_products = Product.query.filter(
                and_(
                    Product.category == category,
                    Product.is_active == True
                )
            ).order_by(desc(Product.created_at)).limit(limit//len(top_categories)).all()
            suggestions.extend(category_products)
        
        return self._deduplicate_products(suggestions, limit)
    
    def _get_category_browse_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get suggestions when browsing categories"""
        # Get most popular products across all categories
        popular_products = Product.query.filter(
            Product.is_active == True
        ).order_by(desc(Product.created_at)).limit(limit).all()
        
        return popular_products
    
    def _get_homepage_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get personalized homepage suggestions"""
        suggestions = []
        
        # 1. Based on user's purchase history
        user_orders = Order.query.filter_by(user_id=user_id).all()
        if user_orders:
            purchased_categories = []
            for order in user_orders:
                for item in order.items:
                    if item.product:
                        purchased_categories.append(item.product.category)
            
            if purchased_categories:
                top_category = Counter(purchased_categories).most_common(1)[0][0]
                category_suggestions = Product.query.filter(
                    and_(
                        Product.category == top_category,
                        Product.is_active == True
                    )
                ).limit(limit//2).all()
                suggestions.extend(category_suggestions)
        
        # 2. New arrivals
        new_products = Product.query.filter(
            Product.is_active == True
        ).order_by(desc(Product.created_at)).limit(limit//2).all()
        suggestions.extend(new_products)
        
        return self._deduplicate_products(suggestions, limit)
    
    def _get_wishlist_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get suggestions based on wishlist items"""
        wishlist_items = Wishlist.query.filter_by(user_id=user_id).all()
        if not wishlist_items:
            return self._get_general_suggestions(user_id, limit)
        
        suggestions = []
        
        # Get similar products to wishlist items
        for item in wishlist_items:
            if item.product:
                similar = Product.query.filter(
                    and_(
                        Product.category == item.product.category,
                        Product.id != item.product_id,
                        Product.price.between(
                            item.product.price * 0.8,
                            item.product.price * 1.2
                        ),
                        Product.is_active == True
                    )
                ).limit(2).all()
                suggestions.extend(similar)
        
        return self._deduplicate_products(suggestions, limit)
    
    def _get_frequently_bought_together(self, product_id: int, limit: int) -> List[Product]:
        """Find products frequently bought together with given product"""
        # Query orders containing the product
        orders_with_product = db.session.query(Order.id).join(OrderItem).filter(
            OrderItem.product_id == product_id
        ).subquery()
        
        # Find other products in those orders
        together_products = db.session.query(
            Product,
            func.count(OrderItem.product_id).label('frequency')
        ).join(OrderItem).join(Order).filter(
            and_(
                Order.id.in_(orders_with_product),
                OrderItem.product_id != product_id,
                Product.is_active == True
            )
        ).group_by(Product.id).order_by(desc('frequency')).limit(limit).all()
        
        return [product for product, _ in together_products]
    
    def _get_similar_user_products(self, user_id: str, product_id: int, limit: int) -> List[Product]:
        """Find products viewed by users with similar preferences"""
        # Get users who also viewed this product
        similar_users = db.session.query(UserInteraction.user_id).filter(
            and_(
                UserInteraction.content_id == product_id,
                UserInteraction.user_id != user_id,
                UserInteraction.interaction_type == 'view'
            )
        ).distinct().limit(20).all()
        
        if not similar_users:
            return []
        
        similar_user_ids = [u[0] for u in similar_users]
        
        # Get products viewed by similar users
        similar_products = db.session.query(
            Product,
            func.count(UserInteraction.content_id).label('view_count')
        ).join(UserInteraction, Product.id == UserInteraction.content_id).filter(
            and_(
                UserInteraction.user_id.in_(similar_user_ids),
                UserInteraction.content_id != product_id,
                Product.is_active == True
            )
        ).group_by(Product.id).order_by(desc('view_count')).limit(limit).all()
        
        return [product for product, _ in similar_products]
    
    def _get_complementary_products(self, category: str, exclude_ids: List[int], limit: int) -> List[Product]:
        """Get complementary products for a category"""
        complementary_categories = {
            'Electronics': ['Accessories', 'Digital'],
            'Fashion': ['Accessories', 'Beauty'],
            'Home': ['Decor', 'Kitchen'],
            'Sports': ['Fitness', 'Outdoor'],
            'Books': ['Digital', 'Education']
        }
        
        target_categories = complementary_categories.get(category, ['Accessories'])
        
        products = Product.query.filter(
            and_(
                Product.category.in_(target_categories),
                ~Product.id.in_(exclude_ids) if exclude_ids else True,
                Product.is_active == True
            )
        ).limit(limit).all()
        
        return products
    
    def _get_general_suggestions(self, user_id: str, limit: int) -> List[Product]:
        """Get general product suggestions when no specific context"""
        return Product.query.filter(
            Product.is_active == True
        ).order_by(desc(Product.created_at)).limit(limit).all()
    
    def _get_fallback_suggestions(self, limit: int) -> List[Dict[str, Any]]:
        """Fallback suggestions when recommendations fail"""
        try:
            products = Product.query.filter(
                Product.is_active == True
            ).order_by(desc(Product.created_at)).limit(limit).all()
            
            return self._enrich_suggestions(products)
        except:
            return []
    
    def _deduplicate_products(self, products: List[Product], limit: int) -> List[Product]:
        """Remove duplicate products and limit results"""
        seen_ids = set()
        unique_products = []
        
        for product in products:
            if product.id not in seen_ids:
                seen_ids.add(product.id)
                unique_products.append(product)
                if len(unique_products) >= limit:
                    break
        
        return unique_products
    
    def _enrich_suggestions(self, products: List[Product]) -> List[Dict[str, Any]]:
        """Enrich product suggestions with additional context"""
        enriched = []
        
        for product in products:
            suggestion = {
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': float(product.price),
                'image_url': product.image_url,
                'category': product.category,
                'is_active': product.is_active,
                'rating': self._get_product_rating(product.id),
                'review_count': self._get_review_count(product.id),
                'is_new': self._is_new_product(product),
                'is_popular': self._is_popular_product(product.id)
            }
            enriched.append(suggestion)
        
        return enriched
    
    def _get_product_rating(self, product_id: int) -> float:
        """Get average rating for a product"""
        avg_rating = db.session.query(func.avg(ProductReview.rating)).filter(
            ProductReview.product_id == product_id
        ).scalar()
        
        return round(float(avg_rating or 0), 1)
    
    def _get_review_count(self, product_id: int) -> int:
        """Get review count for a product"""
        return ProductReview.query.filter_by(product_id=product_id).count()
    
    def _is_new_product(self, product: Product) -> bool:
        """Check if product is new (created within last 30 days)"""
        if not product.created_at:
            return False
        return product.created_at >= datetime.now() - timedelta(days=30)
    
    def _is_popular_product(self, product_id: int) -> bool:
        """Check if product is popular based on recent interactions"""
        recent_interactions = UserInteraction.query.filter(
            and_(
                UserInteraction.content_id == product_id,
                UserInteraction.timestamp >= datetime.now() - timedelta(days=7)
            )
        ).count()
        
        return recent_interactions > 5


def get_contextual_recommendations(user_id: str, context: str, 
                                 current_product_id: Optional[int] = None,
                                 limit: int = 6) -> List[Dict[str, Any]]:
    """
    Get contextual product recommendations
    
    Args:
        user_id: User identifier
        context: Context type (viewing, cart, checkout, search, etc.)
        current_product_id: Current product being viewed
        limit: Maximum number of suggestions
        
    Returns:
        List of contextual product recommendations
    """
    engine = ContextualRecommendationEngine()
    return engine.get_contextual_suggestions(user_id, context, current_product_id, limit)


def track_contextual_interaction(user_id: str, context: str, 
                               action: str, product_id: Optional[int] = None,
                               metadata: Optional[Dict] = None):
    """
    Track user interaction for contextual learning
    
    Args:
        user_id: User identifier
        context: Context where interaction occurred
        action: Action performed (click, add_to_cart, purchase, etc.)
        product_id: Product involved in interaction
        metadata: Additional context data
    """
    try:
        interaction = UserInteraction()
        interaction.user_id = user_id
        interaction.content_id = product_id
        interaction.interaction_type = f"{context}_{action}"
        interaction.score = 1.0
        interaction.timestamp = datetime.now()
        
        if metadata:
            # Store metadata as JSON if your UserInteraction model supports it
            pass
        
        db.session.add(interaction)
        db.session.commit()
        
    except Exception as e:
        logging.error(f"Error tracking contextual interaction: {e}")
        db.session.rollback()
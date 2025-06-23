#!/usr/bin/env python3
"""
Create test user views data for demonstration
"""
import os
import sys
sys.path.append('.')

from app import app, db
from models import ProductView, ContentView, UserSession, Product, Content, User
from datetime import datetime, timedelta
import random
import uuid

def create_test_views():
    """Create realistic test view data"""
    with app.app_context():
        print("Creating test user views data...")
        
        # Get existing products and users
        products = Product.query.filter_by(is_active=True).all()
        users = User.query.all()
        
        if not products:
            print("No products found. Please create some products first.")
            return
        
        if not users:
            print("No users found. Please create a user account first.")
            return
        else:
            user_ids = [user.id for user in users]  # Use existing users only
        
        # Create test sessions
        sessions = []
        for i, user_id in enumerate(user_ids):
            session_id = str(uuid.uuid4())
            device_types = ['desktop', 'mobile', 'tablet']
            browsers = ['Chrome', 'Firefox', 'Safari', 'Edge']
            
            session = UserSession()
            session.user_id = user_id
            session.session_id = session_id
            session.ip_address = f"192.168.1.{100 + i}"
            session.user_agent = f"Mozilla/5.0 ({random.choice(['Windows', 'Mac', 'Linux'])})"
            session.device_type = random.choice(device_types)
            session.browser = random.choice(browsers)
            session.page_views = random.randint(3, 15)
            session.products_viewed = random.randint(1, 8)
            session.started_at = datetime.utcnow() - timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59)
            )
            session.last_activity = session.started_at + timedelta(
                minutes=random.randint(5, 60)
            )
            
            db.session.add(session)
            sessions.append(session)
        
        db.session.commit()
        print(f"Created {len(sessions)} test sessions")
        
        # Create product views
        product_views = []
        for session in sessions:
            # Each session views 1-5 products
            viewed_products = random.sample(products, min(len(products), random.randint(1, 5)))
            
            for product in viewed_products:
                view = ProductView()
                view.user_id = session.user_id
                view.product_id = product.id
                view.session_id = session.session_id
                view.ip_address = session.ip_address
                view.user_agent = session.user_agent
                view.referrer = random.choice([
                    'https://google.com/search',
                    'https://facebook.com',
                    'https://twitter.com',
                    '',  # Direct traffic
                    'https://replit.com'
                ])
                
                # Realistic engagement metrics
                view.view_duration = random.randint(15, 300)  # 15 seconds to 5 minutes
                view.scroll_depth = random.uniform(0.2, 1.0)
                view.clicked_images = random.choice([True, False])
                view.viewed_reviews = random.choice([True, False])
                
                # Vary view times across the past 30 days
                view.viewed_at = datetime.utcnow() - timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59)
                )
                
                product_views.append(view)
                db.session.add(view)
        
        db.session.commit()
        print(f"Created {len(product_views)} product views")
        
        # Create content views if content exists
        contents = Content.query.filter_by(status='published').all()
        if contents:
            content_views = []
            for session in sessions[:7]:  # Some sessions also view content
                viewed_content = random.sample(contents, min(len(contents), random.randint(1, 3)))
                
                for content in viewed_content:
                    view = ContentView()
                    view.user_id = session.user_id
                    view.content_id = content.id
                    view.session_id = session.session_id
                    view.ip_address = session.ip_address
                    view.user_agent = session.user_agent
                    view.referrer = random.choice([
                        'https://google.com/search',
                        'https://bing.com/search',
                        '',
                        'https://social-media.com'
                    ])
                    
                    view.view_duration = random.randint(30, 600)  # 30 seconds to 10 minutes
                    view.scroll_depth = random.uniform(0.3, 1.0)
                    view.read_percentage = random.uniform(0.4, 1.0)
                    
                    view.viewed_at = datetime.utcnow() - timedelta(
                        days=random.randint(0, 30),
                        hours=random.randint(0, 23)
                    )
                    
                    content_views.append(view)
                    db.session.add(view)
            
            db.session.commit()
            print(f"Created {len(content_views)} content views")
        
        print("Test user views data created successfully!")
        print("\nSummary:")
        print(f"- Sessions: {len(sessions)}")
        print(f"- Product views: {len(product_views)}")
        if contents:
            print(f"- Content views: {len(content_views)}")
        print(f"- Products tracked: {len(products)}")
        print(f"- Users/Sessions: {len(user_ids)}")

if __name__ == "__main__":
    create_test_views()
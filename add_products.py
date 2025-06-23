#!/usr/bin/env python3
"""
Script to add more products to the platform
"""
import os
import sys
from datetime import datetime, timedelta
import random

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app, db
from models import Product, User
from sqlalchemy import func
import uuid

def add_sample_products():
    """Add a comprehensive set of sample products"""
    
    with app.app_context():
        # Get the first user or create a default seller
        seller = User.query.first()
        if not seller:
            print("No users found. Please create a user first.")
            return
        
        products_data = [
            # Electronics
            {
                'name': 'iPhone 15 Pro Max',
                'description': 'Latest iPhone with titanium design, A17 Pro chip, and advanced camera system. Perfect for photography and gaming.',
                'price': 1290000,
                'category': 'Electronics',
                'stock_quantity': 25,
                'is_digital': False,
                'weight': 0.221,
                'dimensions': '6.7 x 3.02 x 0.32 inches'
            },
            {
                'name': 'Samsung Galaxy S24 Ultra',
                'description': 'Premium Android smartphone with S Pen, 200MP camera, and AI features. Professional photography capabilities.',
                'price': 1390000,
                'category': 'Electronics',
                'stock_quantity': 18,
                'is_digital': False,
                'weight': 0.232,
                'dimensions': '6.79 x 3.11 x 0.34 inches'
            },
            {
                'name': 'MacBook Air M3',
                'description': 'Ultra-thin laptop with M3 chip, 15-inch Liquid Retina display, and all-day battery life. Perfect for work and creativity.',
                'price': 1690000,
                'category': 'Electronics',
                'stock_quantity': 12,
                'is_digital': False,
                'weight': 1.51,
                'dimensions': '13.4 x 9.35 x 0.44 inches'
            },
            {
                'name': 'Sony WH-1000XM5',
                'description': 'Industry-leading noise canceling headphones with premium sound quality and 30-hour battery life.',
                'price': 390000,
                'category': 'Electronics',
                'stock_quantity': 45,
                'is_digital': False,
                'weight': 0.25,
                'dimensions': '10.7 x 7.3 x 3.2 inches'
            },
            {
                'name': 'iPad Pro 12.9" M4',
                'description': 'Most advanced iPad with M4 chip, Ultra Retina XDR display, and support for Apple Pencil Pro.',
                'price': 1390000,
                'category': 'Electronics',
                'stock_quantity': 22,
                'is_digital': False,
                'weight': 0.682,
                'dimensions': '11.04 x 8.46 x 0.25 inches'
            },
            
            # Fashion
            {
                'name': 'Premium Wool Coat',
                'description': 'Elegant winter coat made from 100% premium wool. Classic design with modern tailoring for sophisticated style.',
                'price': 450000,
                'category': 'Fashion',
                'stock_quantity': 15,
                'is_digital': False,
                'weight': 1.2,
                'dimensions': 'Various sizes available'
            },
            {
                'name': 'Designer Leather Handbag',
                'description': 'Luxury leather handbag with gold hardware and silk lining. Timeless design perfect for any occasion.',
                'price': 680000,
                'category': 'Fashion',
                'stock_quantity': 8,
                'is_digital': False,
                'weight': 0.8,
                'dimensions': '12 x 8 x 4 inches'
            },
            {
                'name': 'Cashmere Scarf',
                'description': 'Ultra-soft cashmere scarf in multiple colors. Perfect accessory for cold weather with luxurious feel.',
                'price': 180000,
                'category': 'Fashion',
                'stock_quantity': 30,
                'is_digital': False,
                'weight': 0.2,
                'dimensions': '70 x 28 inches'
            },
            {
                'name': 'Designer Sunglasses',
                'description': 'Premium sunglasses with polarized lenses and titanium frame. UV400 protection with style.',
                'price': 320000,
                'category': 'Fashion',
                'stock_quantity': 25,
                'is_digital': False,
                'weight': 0.03,
                'dimensions': '5.5 x 2 x 1 inches'
            },
            {
                'name': 'Silk Evening Dress',
                'description': 'Elegant silk evening dress with hand-embroidered details. Perfect for special occasions and formal events.',
                'price': 890000,
                'category': 'Fashion',
                'stock_quantity': 6,
                'is_digital': False,
                'weight': 0.5,
                'dimensions': 'Various sizes available'
            },
            
            # Home & Garden
            {
                'name': 'Smart Robot Vacuum',
                'description': 'AI-powered robot vacuum with mapping technology, auto-empty station, and smartphone control.',
                'price': 890000,
                'category': 'Home & Garden',
                'stock_quantity': 20,
                'is_digital': False,
                'weight': 3.8,
                'dimensions': '13.8 x 13.8 x 3.6 inches'
            },
            {
                'name': 'Air Purifier Pro',
                'description': 'HEPA air purifier for large rooms. Removes 99.97% of particles and allergens with smart connectivity.',
                'price': 450000,
                'category': 'Home & Garden',
                'stock_quantity': 15,
                'is_digital': False,
                'weight': 7.5,
                'dimensions': '11 x 11 x 24 inches'
            },
            {
                'name': 'Smart Thermostat',
                'description': 'Energy-saving smart thermostat with learning algorithms and smartphone control. Reduces energy costs.',
                'price': 280000,
                'category': 'Home & Garden',
                'stock_quantity': 35,
                'is_digital': False,
                'weight': 0.5,
                'dimensions': '4.2 x 4.2 x 0.9 inches'
            },
            {
                'name': 'Ergonomic Office Chair',
                'description': 'Premium office chair with lumbar support, breathable mesh, and adjustable features for all-day comfort.',
                'price': 650000,
                'category': 'Home & Garden',
                'stock_quantity': 12,
                'is_digital': False,
                'weight': 25,
                'dimensions': '26 x 26 x 40-44 inches'
            },
            {
                'name': 'Smart LED Strip Lights',
                'description': '16 million color LED strip lights with music sync and smartphone control. Perfect for ambient lighting.',
                'price': 85000,
                'category': 'Home & Garden',
                'stock_quantity': 50,
                'is_digital': False,
                'weight': 0.3,
                'dimensions': '16.4 feet length'
            },
            
            # Books & Media
            {
                'name': 'Premium E-book Collection',
                'description': 'Curated collection of 1000+ bestselling e-books across various genres. Instant digital download.',
                'price': 120000,
                'category': 'Books & Media',
                'stock_quantity': 999,
                'is_digital': True,
                'weight': 0,
                'dimensions': 'Digital content'
            },
            {
                'name': 'Photography Masterclass',
                'description': 'Complete digital photography course with 50+ hours of video content and practice exercises.',
                'price': 180000,
                'category': 'Books & Media',
                'stock_quantity': 999,
                'is_digital': True,
                'weight': 0,
                'dimensions': 'Digital content'
            },
            {
                'name': 'Premium Audiobook Subscription',
                'description': 'One-year subscription to premium audiobook service with unlimited access to 100,000+ titles.',
                'price': 150000,
                'category': 'Books & Media',
                'stock_quantity': 999,
                'is_digital': True,
                'weight': 0,
                'dimensions': 'Digital subscription'
            },
            {
                'name': 'Hardcover Art Book Collection',
                'description': 'Limited edition collection of art books featuring works from world-renowned artists and museums.',
                'price': 280000,
                'category': 'Books & Media',
                'stock_quantity': 8,
                'is_digital': False,
                'weight': 3.5,
                'dimensions': '12 x 9 x 2 inches each'
            },
            {
                'name': 'Language Learning Software',
                'description': 'Complete language learning software for 25+ languages with AI-powered conversation practice.',
                'price': 200000,
                'category': 'Books & Media',
                'stock_quantity': 999,
                'is_digital': True,
                'weight': 0,
                'dimensions': 'Digital software'
            },
            
            # Sports & Fitness
            {
                'name': 'Smart Fitness Watch',
                'description': 'Advanced fitness tracker with heart rate monitoring, GPS, and 7-day battery life. Water resistant.',
                'price': 420000,
                'category': 'Sports & Fitness',
                'stock_quantity': 28,
                'is_digital': False,
                'weight': 0.055,
                'dimensions': '1.7 x 1.7 x 0.5 inches'
            },
            {
                'name': 'Premium Yoga Mat',
                'description': 'Eco-friendly yoga mat with superior grip and cushioning. Made from natural rubber and cork.',
                'price': 95000,
                'category': 'Sports & Fitness',
                'stock_quantity': 40,
                'is_digital': False,
                'weight': 2.5,
                'dimensions': '72 x 24 x 0.25 inches'
            },
            {
                'name': 'Adjustable Dumbbells Set',
                'description': 'Space-saving adjustable dumbbells from 5-50 lbs per dumbbell. Perfect for home gym workouts.',
                'price': 680000,
                'category': 'Sports & Fitness',
                'stock_quantity': 15,
                'is_digital': False,
                'weight': 45,
                'dimensions': '16 x 8 x 8 inches per dumbbell'
            },
            {
                'name': 'Wireless Bluetooth Earbuds',
                'description': 'Sports earbuds with secure fit, sweat resistance, and 8-hour battery life. Perfect for workouts.',
                'price': 150000,
                'category': 'Sports & Fitness',
                'stock_quantity': 35,
                'is_digital': False,
                'weight': 0.05,
                'dimensions': '1.2 x 0.8 x 0.8 inches each'
            },
            {
                'name': 'Resistance Bands Set',
                'description': 'Complete resistance bands set with 5 resistance levels and door anchor. Full-body workout solution.',
                'price': 65000,
                'category': 'Sports & Fitness',
                'stock_quantity': 60,
                'is_digital': False,
                'weight': 1.2,
                'dimensions': '48 inches length'
            }
        ]
        
        # Add seasonal flags to some products
        seasonal_products = [
            ('Premium Wool Coat', 'winter', datetime(2024, 12, 1), datetime(2025, 2, 28)),
            ('Cashmere Scarf', 'winter', datetime(2024, 11, 15), datetime(2025, 3, 15)),
            ('Smart LED Strip Lights', 'holiday', datetime(2024, 11, 1), datetime(2025, 1, 15)),
            ('Silk Evening Dress', 'valentine', datetime(2025, 1, 15), datetime(2025, 2, 28))
        ]
        
        created_count = 0
        
        for product_data in products_data:
            # Check if product already exists
            existing = Product.query.filter_by(name=product_data['name']).first()
            if existing:
                print(f"Product '{product_data['name']}' already exists, skipping...")
                continue
            
            # Create new product
            product = Product()
            product.name = product_data['name']
            product.description = product_data['description']
            product.price = product_data['price']
            product.category = product_data['category']
            product.stock_quantity = product_data['stock_quantity']
            product.is_digital = product_data['is_digital']
            # Note: weight and dimensions fields not available in current Product model
            product.seller_id = seller.id
            product.created_at = datetime.now()
            product.updated_at = datetime.now()
            
            # Add seasonal information if applicable
            for seasonal_name, season_type, start_date, end_date in seasonal_products:
                if product.name == seasonal_name:
                    product.is_seasonal = True
                    product.season_type = season_type
                    product.seasonal_start = start_date
                    product.seasonal_end = end_date
                    product.seasonal_year = 2025
                    break
            
            # Add new arrival flag for recently added products
            if random.choice([True, False]):
                product.is_new_arrival = True
                product.featured_until = datetime.now() + timedelta(days=30)
            
            db.session.add(product)
            created_count += 1
        
        try:
            db.session.commit()
            print(f"Successfully added {created_count} new products!")
            
            # Display summary
            total_products = Product.query.count()
            categories = db.session.query(Product.category, func.count(Product.id)).group_by(Product.category).all()
            
            print(f"\nTotal products in database: {total_products}")
            print("\nProducts by category:")
            for category, count in categories:
                print(f"  {category}: {count}")
                
        except Exception as e:
            db.session.rollback()
            print(f"Error adding products: {e}")

if __name__ == "__main__":
    add_sample_products()
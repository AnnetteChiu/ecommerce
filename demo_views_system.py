#!/usr/bin/env python3
"""
Demonstrate the user views tracking system capabilities
"""
import os
import sys
sys.path.append('.')

from app import app, db
from models import ProductView, ContentView, UserSession, Product
from datetime import datetime, timedelta
from sqlalchemy import func

def demonstrate_views_system():
    """Show the current state of the user views tracking system"""
    with app.app_context():
        print("=== User Views Tracking System Demonstration ===\n")
        
        # Check current data
        total_product_views = ProductView.query.count()
        total_content_views = ContentView.query.count()
        total_sessions = UserSession.query.count()
        
        print(f"📊 Current Analytics Data:")
        print(f"   • Product Views: {total_product_views:,}")
        print(f"   • Content Views: {total_content_views:,}")
        print(f"   • User Sessions: {total_sessions:,}")
        
        if total_product_views > 0:
            # Show recent activity
            recent_views = ProductView.query.order_by(ProductView.viewed_at.desc()).limit(5).all()
            print(f"\n🔍 Recent Product Views:")
            for view in recent_views:
                product = Product.query.get(view.product_id)
                print(f"   • {product.name if product else 'Unknown'} - {view.viewed_at.strftime('%Y-%m-%d %H:%M')}")
                print(f"     Duration: {view.view_duration}s, Scroll: {view.scroll_depth:.1%}")
            
            # Show engagement metrics
            avg_duration = db.session.query(func.avg(ProductView.view_duration)).scalar() or 0
            avg_scroll = db.session.query(func.avg(ProductView.scroll_depth)).scalar() or 0
            image_clicks = ProductView.query.filter_by(clicked_images=True).count()
            
            print(f"\n📈 Engagement Metrics:")
            print(f"   • Average View Duration: {avg_duration:.1f} seconds")
            print(f"   • Average Scroll Depth: {avg_scroll:.1%}")
            print(f"   • Users Who Clicked Images: {image_clicks}")
        
        # Show device breakdown
        if total_sessions > 0:
            device_stats = db.session.query(
                UserSession.device_type,
                func.count(UserSession.id)
            ).group_by(UserSession.device_type).all()
            
            print(f"\n📱 Device Analytics:")
            for device, count in device_stats:
                print(f"   • {device.title()}: {count} sessions")
        
        print(f"\n🎯 Features Available:")
        print(f"   • Real-time engagement tracking")
        print(f"   • Session management with device detection")
        print(f"   • Scroll depth and interaction monitoring")
        print(f"   • Analytics dashboard with Chart.js visualizations")
        print(f"   • API endpoints for tracking data")
        print(f"   • Export functionality for reports")
        
        print(f"\n📍 Access Points:")
        print(f"   • Analytics Dashboard: /user-views-analytics")
        print(f"   • API Tracking: /api/track-engagement")
        print(f"   • Session Heartbeat: /api/session-heartbeat")
        
        print(f"\n✨ The system automatically tracks:")
        print(f"   • Product page visits and time spent")
        print(f"   • Scroll behavior and content engagement")
        print(f"   • Image interactions and review viewing")
        print(f"   • User sessions across devices")
        print(f"   • Referrer sources and traffic patterns")

if __name__ == "__main__":
    demonstrate_views_system()
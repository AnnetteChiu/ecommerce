#!/usr/bin/env python3
"""
Create test stories to demonstrate Limited-Time Stories functionality
"""

from datetime import datetime, timedelta
from app import app, db
from models import Story, User, Product

def create_test_stories():
    """Create realistic test stories for demonstration"""
    
    with app.app_context():
        # Get a test user (first user in database)
        user = User.query.first()
        if not user:
            print("No users found in database")
            return
        
        # Get some products for linking
        products = Product.query.limit(3).all()
        
        # Create test stories with various types and expiry times
        test_stories = [
            {
                'title': 'Flash Sale - 50% Off All Accessories',
                'title_ko': '플래시 세일 - 모든 액세서리 50% 할인',
                'content': 'Limited time flash sale on all fashion accessories! Hurry, only 6 hours remaining!',
                'content_ko': '모든 패션 액세서리 한정 시간 플래시 세일! 서둘러요, 6시간만 남았어요!',
                'story_type': 'promotion',
                'expires_at': datetime.utcnow() + timedelta(hours=6),
                'priority': 5,
                'background_color': '#ff6b6b',
                'text_color': '#ffffff',
                'is_featured': True,
                'linked_product_id': products[0].id if products else None
            },
            {
                'title': 'New Summer Collection Arrived',
                'title_ko': '새로운 여름 컬렉션 출시',
                'content': 'Discover our latest summer fashion trends with vibrant colors and lightweight fabrics.',
                'content_ko': '생생한 색상과 가벼운 원단으로 만든 최신 여름 패션 트렌드를 만나보세요.',
                'story_type': 'product',
                'expires_at': datetime.utcnow() + timedelta(days=2),
                'priority': 4,
                'background_color': '#4ecdc4',
                'text_color': '#ffffff',
                'is_featured': True,
                'linked_product_id': products[1].id if len(products) > 1 else None
            },
            {
                'title': 'Fashion Week Special Event',
                'title_ko': '패션 위크 특별 이벤트',
                'content': 'Join us for an exclusive fashion week showcase featuring top designers.',
                'content_ko': '최고 디자이너들이 참여하는 독점 패션 위크 쇼케이스에 참여하세요.',
                'story_type': 'event',
                'expires_at': datetime.utcnow() + timedelta(hours=12),
                'priority': 3,
                'background_color': '#a8e6cf',
                'text_color': '#2d3436',
                'is_featured': False
            },
            {
                'title': 'Sustainable Fashion Initiative',
                'title_ko': '지속 가능한 패션 이니셔티브',
                'content': 'Learn about our commitment to eco-friendly fashion and sustainable practices.',
                'content_ko': '친환경 패션과 지속 가능한 관행에 대한 우리의 약속에 대해 알아보세요.',
                'story_type': 'news',
                'expires_at': datetime.utcnow() + timedelta(days=1),
                'priority': 2,
                'background_color': '#74b9ff',
                'text_color': '#ffffff',
                'is_featured': False
            },
            {
                'title': 'Weekend Style Tips',
                'title_ko': '주말 스타일 팁',
                'content': 'Get ready for the weekend with our curated style guide and fashion tips.',
                'content_ko': '우리의 큐레이션된 스타일 가이드와 패션 팁으로 주말을 준비하세요.',
                'story_type': 'general',
                'expires_at': datetime.utcnow() + timedelta(hours=30),
                'priority': 1,
                'background_color': '#fd79a8',
                'text_color': '#ffffff',
                'is_featured': False,
                'linked_product_id': products[2].id if len(products) > 2 else None
            }
        ]
        
        # Create stories
        created_count = 0
        for story_data in test_stories:
            # Check if story with similar title already exists
            existing = Story.query.filter_by(title=story_data['title']).first()
            if existing:
                print(f"Story '{story_data['title']}' already exists, skipping...")
                continue
            
            story = Story()
            story.title = story_data['title']
            story.title_ko = story_data.get('title_ko')
            story.content = story_data['content']
            story.content_ko = story_data.get('content_ko')
            story.story_type = story_data['story_type']
            story.expires_at = story_data['expires_at']
            story.priority = story_data['priority']
            story.background_color = story_data['background_color']
            story.text_color = story_data['text_color']
            story.is_featured = story_data.get('is_featured', False)
            story.user_id = user.id
            story.author_name = user.first_name or user.email or "Fashion Team"
            story.linked_product_id = story_data.get('linked_product_id')
            
            db.session.add(story)
            created_count += 1
        
        db.session.commit()
        
        print(f"✅ Created {created_count} test stories successfully!")
        print(f"Total active stories: {len(Story.get_active_stories())}")
        
        # Display created stories
        active_stories = Story.get_active_stories()
        print("\n📚 Active Stories:")
        for story in active_stories:
            time_remaining = story.time_remaining_korean()
            print(f"- {story.title} ({story.story_type}) - {time_remaining}")

if __name__ == "__main__":
    create_test_stories()
"""
Internationalization and localization support for the content management system
"""

# Korean translations for the website interface
TRANSLATIONS = {
    'ko': {
        # Navigation
        'content': '콘텐츠',
        'gallery': '갤러리',
        'file_manager': '파일 관리자',
        'trending': '인기',
        'analytics': '분석',
        'trading_view': '트레이딩 뷰',
        'ai_insights': 'AI 인사이트',
        'cf_analytics': 'CF 분석',
        'database_admin': '데이터베이스 관리',
        'for_you': '추천',
        'advanced': '고급',
        'cf_tutorial': 'CF 튜토리얼',
        'cf_visualization': 'CF 시각화',
        'create': '만들기',
        'my_dashboard': '내 대시보드',
        'logout': '로그아웃',
        
        # Content Management
        'title': '제목',
        'content_text': '내용',
        'category': '카테고리',
        'status': '상태',
        'author': '작성자',
        'tags': '태그',
        'image': '이미지',
        'files': '파일',
        'created_at': '생성일',
        'updated_at': '수정일',
        
        # Status
        'draft': '초안',
        'published': '게시됨',
        'archived': '보관됨',
        
        # Categories
        'blog_post': '블로그 포스트',
        'news_article': '뉴스 기사',
        'product_description': '제품 설명',
        'documentation': '문서',
        'tutorial': '튜토리얼',
        'case_study': '사례 연구',
        'whitepaper': '백서',
        'press_release': '보도 자료',
        'user_guide': '사용자 가이드',
        'technical_spec': '기술 사양',
        
        # Actions
        'edit': '편집',
        'delete': '삭제',
        'save': '저장',
        'cancel': '취소',
        'submit': '제출',
        'create_content': '콘텐츠 만들기',
        'update_content': '콘텐츠 업데이트',
        'view_content': '콘텐츠 보기',
        'upload': '업로드',
        'download': '다운로드',
        
        # Messages
        'content_created': '콘텐츠가 성공적으로 생성되었습니다',
        'content_updated': '콘텐츠가 성공적으로 업데이트되었습니다',
        'content_deleted': '콘텐츠가 성공적으로 삭제되었습니다',
        'file_uploaded': '파일이 성공적으로 업로드되었습니다',
        'error_occurred': '오류가 발생했습니다',
        'permission_denied': '권한이 거부되었습니다',
        'content_not_found': '콘텐츠를 찾을 수 없습니다',
        
        # Forms
        'required_field': '필수 입력란',
        'optional': '선택사항',
        'characters': '문자',
        'words': '단어',
        'days_old': '일 전',
        'select_option': '옵션 선택',
        
        # Dashboard
        'welcome': '환영합니다',
        'total_content': '총 콘텐츠',
        'published_content': '게시된 콘텐츠',
        'draft_content': '초안 콘텐츠',
        'recent_activity': '최근 활동',
        'recommendations': '추천',
        'performance': '성능',
        'statistics': '통계',
        
        # File Management
        'file_type': '파일 유형',
        'file_size': '파일 크기',
        'upload_date': '업로드 날짜',
        'owner': '소유자',
        'documents': '문서',
        'images': '이미지',
        'videos': '비디오',
        'audio': '오디오',
        'archives': '압축 파일',
        
        # Search and Filter
        'search': '검색',
        'filter': '필터',
        'all_categories': '모든 카테고리',
        'all_status': '모든 상태',
        'sort_by': '정렬 기준',
        'newest_first': '최신순',
        'oldest_first': '오래된순',
        'title_az': '제목 A-Z',
        'title_za': '제목 Z-A',
        
        # Pagination
        'previous': '이전',
        'next': '다음',
        'page': '페이지',
        'of': '/',
        'showing': '표시 중',
        'results': '결과',
        
        # Time
        'just_now': '방금 전',
        'minutes_ago': '분 전',
        'hours_ago': '시간 전',
        'days_ago': '일 전',
        'weeks_ago': '주 전',
        'months_ago': '달 전',
        
        # Analytics
        'views': '조회수',
        'interactions': '상호작용',
        'users': '사용자',
        'engagement': '참여도',
        'growth': '성장률',
        'trends': '트렌드',
        'insights': '인사이트',
        'reports': '보고서',
        
        # AI Features
        'ai_analysis': 'AI 분석',
        'relevance_score': '관련성 점수',
        'quality_score': '품질 점수',
        'engagement_score': '참여도 점수',
        'recommendations_for_you': '맞춤 추천',
        'ai_suggestions': 'AI 제안',
        
        # User Interface
        'home': '홈',
        'shop': '쇼핑',
        'cart': '장바구니',
        'wishlist': '위시리스트',
        'orders': '주문',
        'profile': '프로필',
        'settings': '설정',
        'help': '도움말',
        'contact': '연락처',
        'about': '소개',
        
        # E-commerce
        'products': '상품',
        'product': '상품',
        'price': '가격',
        'discount': '할인',
        'sale': '세일',
        'featured': '추천 상품',
        'new_arrivals': '신상품',
        'seasonal': '시즌 상품',
        'digital': '디지털',
        'physical': '실물',
        'in_stock': '재고 있음',
        'out_of_stock': '품절',
        'add_to_cart': '장바구니에 추가',
        'add_to_wishlist': '위시리스트에 추가',
        'buy_now': '지금 구매',
        'checkout': '결제',
        'payment': '결제',
        'shipping': '배송',
        'delivery': '배달',
        'order_total': '주문 총액',
        'subtotal': '소계',
        'tax': '세금',
        'shipping_cost': '배송비',
        'free_shipping': '무료 배송',
        
        # Product Details
        'description': '설명',
        'specifications': '사양',
        'reviews': '리뷰',
        'rating': '평점',
        'quantity': '수량',
        'size': '크기',
        'color': '색상',
        'material': '소재',
        'brand': '브랜드',
        'model': '모델',
        'warranty': '보증',
        
        # Shopping Cart
        'your_cart': '장바구니',
        'cart_empty': '장바구니가 비어있습니다',
        'item': '항목',
        'items': '항목들',
        'remove': '제거',
        'update': '업데이트',
        'continue_shopping': '쇼핑 계속하기',
        'proceed_to_checkout': '결제 진행',
        
        # User Account
        'login': '로그인',
        'register': '회원가입',
        'signin': '로그인',
        'signup': '회원가입',
        'username': '사용자명',
        'email': '이메일',
        'password': '비밀번호',
        'confirm_password': '비밀번호 확인',
        'first_name': '이름',
        'last_name': '성',
        'full_name': '전체 이름',
        'phone': '전화번호',
        'address': '주소',
        'city': '도시',
        'country': '국가',
        'postal_code': '우편번호',
        
        # Content Creation
        'create_content': '콘텐츠 생성',
        'edit_content': '콘텐츠 편집',
        'delete_content': '콘텐츠 삭제',
        'save': '저장',
        'cancel': '취소',
        'publish': '게시',
        'unpublish': '게시 취소',
        'archive': '보관',
        'duplicate': '복제',
        'preview': '미리보기',
        'draft_saved': '초안 저장됨',
        'auto_save': '자동 저장',
        
        # File Management
        'upload': '업로드',
        'download': '다운로드',
        'file_size': '파일 크기',
        'file_type': '파일 형식',
        'upload_date': '업로드 날짜',
        'file_name': '파일명',
        'choose_file': '파일 선택',
        'drag_drop': '파일을 드래그하여 업로드',
        'max_file_size': '최대 파일 크기',
        'allowed_formats': '허용된 형식',
        
        # Messages and Notifications
        'success': '성공',
        'error': '오류',
        'warning': '경고',
        'info': '정보',
        'message': '메시지',
        'notification': '알림',
        'alert': '알림',
        'confirm': '확인',
        'yes': '예',
        'no': '아니오',
        'ok': '확인',
        'close': '닫기',
        'dismiss': '무시',
        
        # Time and Date
        'today': '오늘',
        'yesterday': '어제',
        'tomorrow': '내일',
        'this_week': '이번 주',
        'last_week': '지난 주',
        'this_month': '이번 달',
        'last_month': '지난 달',
        'this_year': '올해',
        'last_year': '작년',
        'date': '날짜',
        'time': '시간',
        'created': '생성됨',
        'modified': '수정됨',
        'published_at': '게시일',
        
        # Navigation and Layout
        'menu': '메뉴',
        'sidebar': '사이드바',
        'header': '헤더',
        'footer': '푸터',
        'main_content': '주요 콘텐츠',
        'back': '뒤로',
        'forward': '앞으로',
        'go_back': '뒤로 가기',
        'go_home': '홈으로',
        'breadcrumb': '경로',
        
        # Stats and Analytics
        'statistics': '통계',
        'total': '총계',
        
        # Social Media Sharing
        'share_product': '제품 공유',
        'copy_link': '링크 복사',
        'count': '개수',
        'percentage': '비율',
        'average': '평균',
        'maximum': '최대',
        'minimum': '최소',
        'chart': '차트',
        'graph': '그래프',
        'report': '보고서',
        'export': '내보내기',
        'import': '가져오기',
        
        # Content Types
        'story': '스토리',
        'stories': '스토리들',
        'article': '기사',
        'post': '게시물',
        'page': '페이지',
        'comment': '댓글',
        'reply': '답글',
        'like': '좋아요',
        'share': '공유',
        'bookmark': '북마크',
        'favorite': '즐겨찾기',
        
        # Search and Discovery
        'search_results': '검색 결과',
        'no_results': '결과 없음',
        'search_placeholder': '검색어를 입력하세요',
        'advanced_search': '고급 검색',
        'suggestions': '제안',
        'popular': '인기',
        'recommended': '추천',
        'related': '관련',
        'similar': '유사',
        'trending_topics': '인기 주제',
        
        # Actions
        'submit': '제출',
        'send': '보내기',
        'reply': '답글',
        'forward': '전달',
        'copy': '복사',
        'paste': '붙여넣기',
        'cut': '잘라내기',
        'undo': '실행 취소',
        'redo': '다시 실행',
        'refresh': '새로고침',
        'reload': '다시 로드',
        'reset': '재설정',
        'clear': '지우기',
        
        # Seasonal and Special
        'spring': '봄',
        'summer': '여름',
        'autumn': '가을',
        'fall': '가을',
        'winter': '겨울',
        'holiday': '휴일',
        'christmas': '크리스마스',
        'valentine': '발렌타인',
        'easter': '부활절',
        'halloween': '할로윈',
        'thanksgiving': '추수감사절',
        'new_year': '신년',
        'back_to_school': '개학',
        
        # Status Messages
        'loading': '로딩 중',
        'saving': '저장 중',
        'uploading': '업로드 중',
        'processing': '처리 중',
        'completed': '완료',
        'failed': '실패',
        'pending': '대기 중',
        'cancelled': '취소됨',
        'expired': '만료됨',
        'active': '활성',
        'inactive': '비활성',
        'enabled': '활성화됨',
        'disabled': '비활성화됨',
        
        # Language and Localization
        'language': '언어',
        'korean': '한국어',
        'english': '영어',
        'change_language': '언어 변경',
        'select_language': '언어 선택',
        
        # Hero Banner and Marketing
        'discover': '발견하다',
        'explore': '탐험하다',
        'experience': '경험하다',
        'marketplace': '마켓플레이스',
        'premium': '프리미엄',
        'quality': '품질',
        'exclusive': '독점',
        'limited_time': '한정 시간',
        'special_offer': '특별 제안',
        'best_seller': '베스트셀러',
        'featured_products': '추천 상품',
        'latest_updates': '최신 업데이트',
        'personalized': '맞춤형',
        'recommendations': '추천',
        'tailored': '맞춤',
        'just_for_you': '당신만을 위한',
        
        # Call to Action
        'shop_now': '지금 쇼핑하기',
        'learn_more': '더 알아보기',
        'get_started': '시작하기',
        
        # Recommendation Wizard
        'recommendation_wizard': '추천 마법사',
        'find_perfect_products': '완벽한 상품을 찾아드립니다',
        'select_categories': '카테고리 선택',
        'choose_product_categories': '관심있는 상품 카테고리를 선택하세요',
        'electronics': '전자제품',
        'fashion': '패션',
        'home_garden': '홈 & 가든',
        'sports': '스포츠',
        'books': '도서',
        'beauty': '뷰티',
        'budget_range': '예산 범위',
        'select_budget_range': '원하는 예산 범위를 설정하세요',
        'minimum': '최소',
        'maximum': '최대',
        'quick_presets': '빠른 설정',
        'shopping_preferences': '쇼핑 선호도',
        'tell_us_preferences': '쇼핑 선호도를 알려주세요',
        'brand_preference': '브랜드 선호도',
        'premium_brands': '프리미엄 브랜드',
        'value_brands': '가성비 브랜드',
        'no_preference': '상관없음',
        'product_condition': '상품 상태',
        'new_only': '새 상품만',
        'used_acceptable': '중고 상품 허용',
        'important_factors': '중요한 요소',
        'shipping': '배송',
        'style_preferences': '스타일 선호도',
        'select_preferred_styles': '선호하는 스타일을 선택하세요',
        'modern': '모던',
        'classic': '클래식',
        'minimalist': '미니멀',
        'luxury': '럭셔리',
        'casual': '캐주얼',
        'trendy': '트렌디',
        'results': '결과',
        'generating_recommendations': '추천 상품 생성 중',
        'finding_perfect_matches': '완벽한 매치를 찾고 있습니다',
        'your_recommendations': '맞춤 추천 상품',
        'save_preferences': '선호도 저장',
        'start_over': '다시 시작',
        'previous': '이전',
        'next': '다음',
        'get_recommendations': '추천받기',
        'match': '일치',
        'view_details': '상세보기',
        'added_to_cart': '장바구니에 추가됨',
        'preferences_saved': '선호도가 저장되었습니다',
        'error_generating': '추천 생성 중 오류',
        'please_try_again': '다시 시도해주세요',
        'try_again': '다시 시도',
        'recommendations_ready': '추천 완료',
        'your_preferences': '선택하신 조건',
        'no_matches_found': '조건에 맞는 상품을 찾을 수 없습니다',
        'try_adjusting_criteria': '검색 조건을 조정해보세요',
        'adjust_preferences': '조건 수정',
        'refine_search': '검색 세분화',
        'final_step': '완료',
        'sign_up_now': '지금 가입하기',
        'try_free': '무료 체험',
        'download_now': '지금 다운로드',
        'contact_us': '문의하기',
        'view_details': '자세히 보기',
        'read_more': '더 읽기',
        'see_all': '모두 보기',
        'loading': '로딩 중...',
        'no_data': '데이터가 없습니다',
        'error': '오류',
        'success': '성공',
        'warning': '경고',
        'info': '정보',
        'confirm': '확인',
        'yes': '예',
        'no': '아니오',
        'close': '닫기',
        'refresh': '새로고침',
        'settings': '설정',
        'help': '도움말',
        'about': '정보',
        'contact': '연락처',
        'privacy': '개인정보보호',
        'terms': '이용약관',
        
        # Language
        'language': '언어',
        'english': 'English',
        'korean': '한국어',
        'change_language': '언어 변경',
        'language_changed': '언어가 변경되었습니다',
        
        # Sales Reports
        'sales_reports': '매출 보고서',
        'comprehensive_sales_analysis': '종합적인 매출 분석 및 인사이트',
        'from_date': '시작 날짜',
        'to_date': '종료 날짜',
        'period': '기간',
        'today': '오늘',
        'yesterday': '어제',
        'this_week': '이번 주',
        'this_month': '이번 달',
        'this_quarter': '이번 분기',
        'this_year': '올해',
        'custom_range': '사용자 지정 범위',
        'apply_filter': '필터 적용',
        'total_revenue': '총 매출',
        'total_orders': '총 주문 수',
        'avg_order_value': '평균 주문 금액',
        'unique_customers': '고유 고객 수',
        'previous_period': '이전 기간',
        'revenue_trend': '매출 추이',
        'top_categories': '상위 카테고리',
        'top_products': '상위 제품',
        'rank': '순위',
        'product': '제품',
        'quantity_sold': '판매 수량',
        'revenue': '매출',
        'avg_rating': '평균 평점',
        'daily_sales': '일별 매출',
        'date': '날짜',
        'orders': '주문',
        'customer_insights': '고객 인사이트',
        'new_customers': '신규 고객',
        'returning_customers': '재방문 고객',
        'retention_rate': '고객 유지율',
        'avg_orders_per_customer': '고객당 평균 주문 수',
        'please_select_date_range': '날짜 범위를 선택해주세요',
        'error_loading_reports': '보고서 로딩 오류',
        
        # Newsletter translations
        'newsletter_subscription': '패션 뉴스레터',
        'newsletter_description': '개인 맞춤형 패션 영감과 독점 혜택을 받아보세요',
        'subscribe_to_newsletter': '뉴스레터 구독',
        'fashion_preferences': '패션 선호도',
        'newsletter_benefits': '뉴스레터 혜택',
        'personalized_fashion_recommendations': '당신의 스타일에 맞는 개인 맞춤 패션 추천',
        'exclusive_style_tips': '패션 전문가의 독점 스타일링 팁',
        'early_access_new_arrivals': '신상품 및 컬렉션 우선 접근',
        'seasonal_fashion_trends': '시즌별 패션 트렌드 및 컬러 팔레트',
        'special_discounts_offers': '특별 할인 및 회원 전용 혜택',
        'newsletter_privacy_notice': '개인정보를 존중합니다. 언제든지 구독 해지 가능합니다.',
        'newsletter_preview': '뉴스레터 미리보기',
        'weekly_fashion_inspiration': '주간 패션 영감',
        'trending_fashion_items': '당신을 위해 큐레이션된 트렌드 패션 아이템',
        'styling_tips_guides': '스타일링 팁 및 가이드',
        'personalized_product_picks': '개인 맞춤 상품 추천',
        'exclusive_offers': '독점 혜택',
        'member_only_discounts': '회원 전용 최대 30% 할인',
        'early_sale_access': '세일 및 프로모션 우선 접근',
        'limited_edition_alerts': '한정판 및 콜라보레이션 알림',
        'newsletter_already_subscribed': '이미 뉴스레터를 구독 중인 이메일입니다',
        'newsletter_subscribed_success': '구독 완료! 환영 메시지를 이메일에서 확인하세요.',
        'newsletter_subscribed_no_email': '구독은 완료되었지만 환영 이메일을 보낼 수 없었습니다.',
        'invalid_unsubscribe_link': '유효하지 않은 구독 해지 링크',
        'newsletter_unsubscribed': '뉴스레터 구독이 해지되었습니다',
    }
}

# Default language
DEFAULT_LANGUAGE = 'en'

def get_translation(key, language='en'):
    """
    Get translation for a given key and language
    
    Args:
        key: Translation key
        language: Language code (default: 'en')
        
    Returns:
        Translated string or original key if not found
    """
    if language in TRANSLATIONS and key in TRANSLATIONS[language]:
        return TRANSLATIONS[language][key]
    return key

def get_available_languages():
    """
    Get list of available languages
    
    Returns:
        Dictionary of language codes and names
    """
    return {
        'en': 'English',
        'ko': '한국어'
    }

def translate_dict(data, language='en'):
    """
    Translate a dictionary of values
    
    Args:
        data: Dictionary to translate
        language: Target language
        
    Returns:
        Dictionary with translated values
    """
    if not isinstance(data, dict):
        return data
        
    translated = {}
    for key, value in data.items():
        if isinstance(value, str):
            translated[key] = get_translation(value, language)
        elif isinstance(value, dict):
            translated[key] = translate_dict(value, language)
        elif isinstance(value, list):
            translated[key] = [get_translation(item, language) if isinstance(item, str) else item for item in value]
        else:
            translated[key] = value
    
    return translated
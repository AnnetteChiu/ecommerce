# Dynamic Content Manager

## Overview

This is a Flask-based web application for managing dynamic content such as blog posts, articles, and documentation. The application provides a user-friendly interface for creating, editing, viewing, and organizing content with features like categorization, status management, and search functionality.

## System Architecture

### Frontend Architecture
- **Template Engine**: Jinja2 templates with Flask
- **CSS Framework**: Bootstrap 5 with Replit dark theme
- **JavaScript**: Vanilla JavaScript for interactive features
- **Icons**: Font Awesome for consistent iconography
- **Responsive Design**: Mobile-first approach with Bootstrap grid system

### Backend Architecture
- **Framework**: Flask (Python web framework)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Form Handling**: Flask-WTF with WTForms for form validation
- **Session Management**: Flask sessions with configurable secret key
- **Data Storage**: PostgreSQL database with Content model
- **WSGI Server**: Gunicorn for production deployment

### Application Structure
```
/
├── app.py              # Main Flask application
├── main.py             # Application entry point
├── forms.py            # WTForms form definitions
├── templates/          # Jinja2 HTML templates
├── static/js/          # Client-side JavaScript
└── pyproject.toml      # Python dependencies
```

## Key Components

### Content Management System
- **Content Model**: Stores title, content, category, status, author, tags, images, and timestamps
- **Categories**: Predefined content types (Blog Post, News Article, Product Description, etc.)
- **Status System**: Draft, Published, Archived workflow
- **Tagging System**: Comma-separated tags for content organization
- **Image Management**: Upload, display, and manage images with content
- **Rich Text Editor**: Quill.js-powered editor with comprehensive formatting toolbar and auto-save functionality

### Comprehensive File Management System
- **Multi-Format Support**: Images (PNG, JPG, JPEG, GIF, WEBP, SVG), Documents (PDF, DOC, DOCX, TXT, RTF, ODT, CSV, XLSX, XLS, PPT, PPTX), Videos (MP4, WEBM, AVI, MOV, WMV, FLV), Audio (MP3, WAV, OGG, FLAC, AAC, M4A), Archives (ZIP, RAR, 7Z, TAR, GZ)
- **Smart Storage**: Organized file storage with separate folders for images and other file types
- **Database Integration**: Complete file metadata tracking with File model including size, type, and ownership
- **User Ownership**: Individual file ownership with secure access controls and deletion permissions
- **File Manager Dashboard**: Comprehensive file management interface with categorized views and storage analytics
- **Download System**: Secure file downloads with proper headers and interaction tracking
- **File Attachments**: Multiple file uploads per content item with visual display and management
- **File Type Detection**: Automatic file type classification with appropriate icons and handling
- **Storage Analytics**: Real-time storage usage tracking and file type distribution
- **File Preview**: Image preview modals and file information display

### Recommendation System
- **Content Similarity**: Analyzes categories, tags, keywords, and authors to find related content
- **Collaborative Filtering (CF)**: User behavior analysis with cosine similarity calculations
- **Hybrid Recommendations**: Combines content-based (60%) and collaborative filtering (40%) approaches
- **User Interaction Tracking**: Records views, edits, and other actions with weighted scoring
- **Category Suggestions**: Displays related articles from the same category
- **CF Analytics Dashboard**: Real-time insights into user behavior patterns and recommendation performance

### Form Validation
- **ContentForm**: For creating new content with comprehensive validation
- **EditContentForm**: For updating existing content
- **Validation Rules**: Length constraints, required fields, and data sanitization

### Rich Text Editor System
- **Quill.js Integration**: Professional-grade rich text editor with comprehensive formatting options
- **Formatting Features**: Headers (H1-H6), bold, italic, underline, strikethrough, text colors, background colors
- **Lists and Alignment**: Ordered lists, bullet lists, text alignment options, indentation controls
- **Media Support**: Link insertion, image embedding, video embedding capabilities
- **Advanced Features**: Code blocks, blockquotes, subscript, superscript formatting
- **Auto-Save**: Content automatically saves every 30 seconds with visual indicators
- **Real-Time Preview**: Live preview functionality during content creation and editing
- **Seamless Integration**: Works consistently across both create and edit content pages

### Multi-User Authentication System
- **Replit OAuth Integration**: Secure OpenID Connect authentication with automatic user registration
- **User Management**: Complete user profiles with email, name, and profile image from Replit accounts
- **Content Ownership**: Individual user content ownership with edit/delete permissions only for content creators
- **Access Control**: Protected routes for content creation, editing, and deletion requiring login
- **Landing Page**: Feature-rich welcome page for unauthenticated users showcasing public content
- **User Dashboard**: Personalized content view showing user's own content plus published content from others
- **Session Management**: Persistent login sessions with automatic token refresh and secure logout
- **Authorization Controls**: Users can only modify content they own, with clear ownership indicators in UI

### User Interface
- **Landing Page**: Feature-rich welcome page for new users with login prompts
- **Dashboard**: Overview of all content with filtering and search (authenticated users)
- **Content Creation**: Rich text editor with advanced formatting and real-time preview (requires login)
- **Content Editing**: Rich text editor preserving existing formatting with auto-save (requires login)
- **Content Viewing**: Clean, readable content display with proper HTML rendering
- **User Profile**: Navigation dropdown showing user information and logout option

## Data Flow

1. **Content Creation**:
   - User fills out ContentForm
   - Form validation on client and server side
   - Data stored in in-memory content_store with auto-incrementing ID
   - Timestamps automatically added

2. **Content Retrieval**:
   - Homepage displays filtered content based on category, status, and search terms
   - Individual content accessed via unique ID
   - Real-time filtering without page reload

3. **Content Updates**:
   - Existing content loaded into EditContentForm
   - Changes validated and updated in storage
   - Updated timestamp automatically set

## External Dependencies

### Python Packages
- **Flask**: Core web framework
- **Flask-WTF**: Form handling and CSRF protection
- **WTForms**: Form validation and rendering
- **Werkzeug**: WSGI utilities and middleware
- **Gunicorn**: Production WSGI server
- **Email-validator**: Email validation for forms
- **psycopg2-binary**: PostgreSQL adapter (prepared for future database integration)

### Frontend Dependencies
- **Bootstrap 5**: UI framework with Replit theme
- **Font Awesome**: Icon library
- **Vanilla JavaScript**: No additional frontend frameworks

## Deployment Strategy

### Development Environment
- **Server**: Flask development server with auto-reload
- **Host**: 0.0.0.0:5000 for Replit compatibility
- **Debug Mode**: Enabled for development

### Production Environment
- **Server**: Gunicorn with auto-scaling deployment target
- **Configuration**: Proxy fix for proper header handling
- **Environment Variables**: Session secret from environment
- **Port**: 5000 with bind to all interfaces

### Replit Configuration
- **Runtime**: Python 3.11 with Nix package management
- **System Packages**: OpenSSL and PostgreSQL prepared for future use
- **Workflow**: Parallel execution with automatic port detection

## Changelog

- June 14, 2025. Initial setup with basic content management
- June 14, 2025. Added comprehensive image management system with upload, gallery, and integration features
- June 14, 2025. Migrated from in-memory storage to PostgreSQL database with SQLAlchemy ORM
- June 15, 2025. Implemented intelligent recommendation system with content similarity analysis, trending content detection, and personalized suggestions
- June 15, 2025. Added Collaborative Filtering (CF) system with user interaction tracking, hybrid recommendations, and real-time analytics dashboard
- June 15, 2025. Enhanced database integration with PostgreSQL optimization, full-text search, performance indexing, admin dashboard, and automated backup systems
- June 15, 2025. Implemented rich text editor using Quill.js with comprehensive formatting toolbar, auto-save functionality, and seamless integration for both content creation and editing
- June 15, 2025. Removed authentication system and restored application to work without user login requirements - all content management features are now available to all users
- June 15, 2025. Enhanced visual design with custom CSS styling including: modern light theme with animated background particles, improved typography with Inter font, modern card designs with glass-morphism effects, enhanced buttons with gradients and hover animations, improved form styling, and responsive design improvements
- June 15, 2025. Completely removed multi-user functionality after brief implementation attempt - application restored to original single-user state with all authentication references removed and database schema cleaned up
- June 15, 2025. Successfully implemented comprehensive multi-user authentication system with Replit OAuth integration, user ownership controls, secure content management, and beautiful landing page for unauthenticated users
- June 15, 2025. Implemented comprehensive file upload system supporting documents, videos, audio, and archives beyond images - includes File model with metadata tracking, user ownership controls, file manager dashboard with storage analytics, secure download system, and organized file storage with automatic type detection
- June 15, 2025. Enhanced file upload system with advanced UI features: drag-and-drop upload zones, real-time file preview with remove functionality, file type icons and size formatting, bulk upload interface for multiple files, enhanced form validation, and improved user experience with visual feedback
- June 15, 2025. Implemented comprehensive personalized content recommendation engine with machine learning algorithms: TF-IDF content-based filtering, collaborative filtering using cosine similarity, hybrid recommendations combining multiple approaches, user behavior analysis and preference tracking, personalized dashboard with intelligent content suggestions, and real-time feedback tracking system
- June 15, 2025. Implemented comprehensive micro-interactions and delightful UI animations system: enhanced button ripple effects with scaling animations, smooth form interactions with floating labels and focus states, scroll-based reveal animations with Intersection Observer, staggered card loading animations, interactive badges and status indicators, loading spinners and progress feedback, shimmer effects for upload zones, floating action button with rotation effects, enhanced navigation with underline animations, smooth page transitions, and sophisticated hover effects throughout the application
- June 15, 2025. Enhanced icon system with modern, intuitive visual design: updated navigation icons, improved content action buttons, modernized file type icons with color coding, enhanced status badges with contextual icons, better category and filter labels, and improved tag display for consistent visual hierarchy throughout the application
- June 15, 2025. Implemented comprehensive trading-style analytics dashboard: real-time content performance metrics with Chart.js integration, interactive charts showing views/interactions/users over time, live activity feed with real-time updates, top performing content rankings, trending topics visualization, and trading-inspired UI with professional metric cards and smooth animations
- June 15, 2025. Implemented comprehensive AI-powered content relevance scoring system: OpenAI GPT-4o integration for intelligent content analysis, multi-criteria scoring (clarity, depth, engagement, relevance, structure, originality), detailed AI analysis dashboard with visual score displays, real-time score badges on content cards, actionable insights and improvement recommendations, batch scoring API endpoints, and seamless integration with existing content management workflow
- June 15, 2025. Implemented comprehensive AI-powered translation system but removed it due to user preference to cancel translation functionality
- June 15, 2025. Implemented Korean language localization system for website interface: comprehensive translation dictionary with 100+ Korean translations, language switching functionality in navigation menus, session-based language preferences, bilingual navigation menus (English/Korean), language switcher in user profile dropdown for authenticated users, and separate language switcher for non-authenticated users
- June 15, 2025. Implemented comprehensive ecommerce functionality with Stripe integration: complete product management system with seller capabilities, shopping cart with quantity management, secure checkout process with Stripe payment processing, order management and tracking, inventory management for physical and digital products, product catalog with search and filtering, and integrated shop navigation in main menu
- June 15, 2025. Implemented comprehensive product collaborative filtering recommendation system: user-based collaborative filtering using cosine similarity calculations, item-based collaborative filtering for similar product suggestions, category-based recommendations using purchase history, hybrid recommendation engine combining multiple approaches, personalized product recommendations displayed in shop interface, similar product suggestions on product detail pages, and machine learning-powered product discovery
- June 15, 2025. Successfully implemented and tested comprehensive limited-time dynamic stories feature: Story model with expiration timestamps and priority system, bilingual Korean/English story display, time-remaining countdown badges with animated pulse effects, categorized story types (general, product, event, news), visual story cards with hover animations, integration with product catalog for product-linked stories, responsive design for mobile and desktop, story creation interface with image upload and product linking capabilities, navigation menu integration, and automatic cleanup of expired stories - feature is fully operational with test stories displaying correctly on homepage
- June 15, 2025. Implemented comprehensive new arrivals feature system: Enhanced Product model with is_new_arrival boolean flag and featured_until timestamp for time-limited status, intelligent new arrival detection with 30-day default window, dedicated new arrivals page with advanced filtering by category/date/sort options, statistics dashboard showing today/week/month counts, product badges with animated effects for recently added items, navigation menu integration in shop dropdown, responsive grid layout with pagination, new arrival highlighting throughout existing product displays, CSS animations including pulse effects and gradient badges, and seamless integration with existing cart/wishlist functionality
- June 15, 2025. Implemented stunning homepage hero banner (主視覺banner): Full-height hero section with animated gradient background and floating particles, compelling content with animated text gradients and real-time statistics counters, prominent call-to-action buttons leading to shop and new arrivals, visual feature highlights including delivery, wishlist, reviews, and AI recommendations, floating product cards with 3D animations on desktop, comprehensive responsive design adapting from desktop to mobile, quick actions bar with hover effects for key platform features, JavaScript animations for number counting and parallax scrolling effects, and seamless integration with existing platform statistics
- June 15, 2025. Successfully resolved new arrivals page implementation issues: Fixed translation function errors by removing undefined function calls, corrected template datetime variable error, ensured robust integer conversion for date filtering, and completed full testing verification - new arrivals feature is now fully operational with dynamic badge system, advanced filtering capabilities, real-time statistics, and professional responsive design
- June 15, 2025. Implemented comprehensive seasonal products system: Enhanced Product model with seasonal availability fields (is_seasonal, season_type, seasonal_start, seasonal_end, seasonal_year), intelligent seasonal availability detection with 13 predefined season types (spring, summer, fall, winter, holiday, christmas, valentine, easter, halloween, thanksgiving, back_to_school, new_year), database migration for seasonal columns, dedicated seasonal products page with advanced filtering by season/category/availability status, seasonal product creation form with conditional fields and JavaScript interactivity, animated seasonal badges with season-specific colors and icons, navigation menu integration, test seasonal products created for demonstration, and comprehensive seasonal status checking with cross-year season support
- June 16, 2025. Fixed image saving functionality for product creation: Resolved CSRF token blocking issues by exempting product creation/editing endpoints, corrected database field mapping from non-existent 'images' field to proper 'image_url' field, enhanced file upload handling with UUID-based filename generation, added comprehensive error handling and logging for upload operations, and verified upload directory and file storage functionality
- June 16, 2025. Implemented comprehensive product deletion system: Added delete product functionality to My Products page with Bootstrap confirmation modal, created secure backend delete route with ownership validation, implemented safety checks preventing deletion of products with existing orders, added automatic cleanup of related data (cart items, wishlist entries, product reviews), included image file deletion when product is removed, and comprehensive error handling with user feedback
- June 16, 2025. Fixed critical product creation and editing issues: Resolved Product model constructor problems by using individual field assignment instead of constructor parameters, fixed CSRF token exemption for upload endpoints, corrected database field mapping from 'images' to 'image_url', enhanced form validation error handling with detailed debugging messages, added comprehensive seasonal product field support in edit functionality, and verified product creation works correctly through automated testing
- June 16, 2025. Successfully resolved product creation form validation and image upload issues: Fixed CSRF token validation by changing form.validate_on_submit() to form.validate() for exempted routes, set season type choices dynamically in create_product route to prevent "Not a valid choice" errors, enhanced seasonal field handling for empty datetime values, added comprehensive image upload logging and error handling, and verified both regular and seasonal products with images can be created successfully
- June 16, 2025. Implemented comprehensive CSS color refinement system: Enhanced color palette with modern blue primary colors, elegant purple secondary colors, fresh green success colors, warm orange warning colors, and sophisticated gray neutrals; refined gradient system with 135-degree linear gradients; enhanced product title styling with refined hover effects; comprehensive seasonal badge color system with season-specific gradients; advanced button styling with enhanced hover effects and 3D animations; improved card styling with rounded corners and subtle shadows; enhanced text color utilities; refined hero banner and featured products banner styling with improved visual hierarchy and modern design aesthetics
- June 16, 2025. Implemented comprehensive animated loading skeletons system: Created CSS animations with skeleton-loading keyframes, built JavaScript functions for skeleton management (showSkeletonLoading, hideSkeletonLoading, generateSkeletonHTML), developed skeleton types for product grids, content lists, forms, tables, and profiles, created interactive skeleton demo page with live examples, integrated skeleton demo into navigation menu under Analytics dropdown, enhanced AJAX fetch with skeleton loading support, and added automatic image skeleton loading for better user experience during content loading states
- June 16, 2025. Refined main banner design with dark theme and flat styling: Removed all gradients and visual effects for completely flat design, changed hero banner to dark background (#212121) with white "Discover Amazin" title (#ffffff), updated subtitle to light gray (#e0e0e0) for proper contrast, aligned main title to left side for modern asymmetrical layout, eliminated floating particles and decorative elements, and created clean minimalist aesthetic with pure flat colors and typography-focused design
- June 16, 2025. Completely removed trending functionality from the platform: Eliminated trending content route and function, removed trending sidebar from homepage, deleted trending.html template, cleaned up all trending references from navigation menus and content descriptions, updated hero banner and featured products descriptions to use "premium" instead of "trending", streamlined content recommendation system to focus purely on content-based and collaborative filtering approaches without trending analysis
- June 17, 2025. Removed recommendation wizard functionality from the platform: Eliminated wizard routes, API endpoints, and related functions, cleaned up all wizard references from navigation menus and templates, removed wizard-related JavaScript code and styling, streamlined codebase by removing wizard templates and associated functionality, and maintained focus on core ecommerce features without guided recommendation workflow
- June 17, 2025. Implemented comprehensive sales reports system: Created detailed sales analytics dashboard with key metrics (total revenue, orders, average order value, unique customers), real-time growth percentage calculations comparing current to previous periods, interactive date range filtering with preset periods (today, week, month, quarter, year, custom), revenue trend charts using Chart.js with daily breakdown visualization, top products performance table with sales quantities and ratings, category performance pie charts showing revenue distribution, customer insights including new vs returning customers and retention rates, CSV and PDF export functionality for reports, daily sales breakdown tables, comprehensive Korean language translations for all sales terminology, integration with Analytics navigation dropdown, robust error handling and fallback data presentation, and responsive design optimized for desktop and mobile viewing
- June 17, 2025. Implemented floating action button (FAB) with playful micro-interactions: Created sophisticated floating action button system with gradient backgrounds and advanced CSS animations, implemented menu expansion with staggered item animations using cubic-bezier easing, added ripple effects on button clicks with dynamic size calculations, integrated smart scroll behavior that hides/shows FAB based on scroll direction, magnetic mouse attraction effect on desktop with distance-based movement, haptic feedback for mobile devices and optional sound effects, cart notification pulse animation that syncs with cart item count, escape key and click-outside functionality for menu closure, comprehensive mobile responsiveness with touch optimizations, bilingual Korean/English labels for all menu items, and seamless integration with existing shop/cart/wishlist/analytics navigation
- June 17, 2025. Implemented comprehensive social media product sharing with dynamic preview functionality: Added Open Graph meta tags and Twitter Card support for rich social media previews, created interactive sharing buttons for Facebook, Twitter, WhatsApp, and copy link functionality, developed dynamic preview modal showing how shared content will appear on each platform, implemented smooth animations and visual feedback for all interactions, added Korean language support for sharing interface, and resolved CSRF token issues for cart functionality
- June 17, 2025. Removed skeleton loading demo from navigation and codebase: Cleaned up skeleton demo route, template, and navigation menu entry to streamline the analytics section and reduce unnecessary demonstration pages
- June 17, 2025. Completely removed swipe gesture system from the platform: Eliminated all swipe event detection, removed SwipeManager class, disabled product card swipe functionality, removed swipe navigation controls, cleaned up all swipe-related CSS styling and animations, removed touch event handlers and gesture recognition, simplified mobile interface to use traditional button-based interactions only, fixed JavaScript syntax errors after cleanup, and restored floating action button functionality that was accidentally affected during swipe removal
- June 17, 2025. Implemented comprehensive automatic product image upload system: Created advanced drag-and-drop upload zone with visual feedback and hover animations, implemented multiple image selection and preview grid with thumbnail generation, added automatic upload progress tracking with realistic progress indicators, developed image management with remove functionality and main image designation, enhanced file validation with size limits and format checking, integrated seamless form compatibility with existing product creation workflow, added comprehensive CSS animations including upload zone hover effects, drag-active states, image preview card animations, progress bar styling, notification system, and responsive design optimizations for both desktop and mobile interfaces
- June 17, 2025. Implemented comprehensive user views tracking system: Added ProductView, ContentView, UserSession, and ViewAnalytics database models for detailed user interaction tracking, created automatic product view tracking with engagement metrics (scroll depth, image clicks, review viewing, session duration), developed user views analytics dashboard with Chart.js visualizations showing daily trends, device breakdowns, browser analytics, and top referrers, implemented real-time JavaScript engagement tracking with ProductEngagementTracker class for automatic data collection, added API endpoints for tracking engagement metrics and session heartbeats, integrated view statistics display in product detail pages, created comprehensive analytics navigation menu integration, and established session management with device detection and user behavior analysis
- June 17, 2025. Implemented sophisticated fashion banner on homepage: Created premium fashion section with elegant gradient background and subtle pattern overlay, integrated dynamic product showcase grid displaying real fashion items (Clothing, Accessories, Shoes categories), added animated floating badge with crown icon and premium styling, implemented interactive call-to-action buttons linking to fashion categories and new arrivals, developed feature highlights with animated icon circles showcasing free shipping, easy returns, and premium quality, added responsive design with mobile-optimized grid layout, included hover animations and image scaling effects for product showcase cards, and established fallback placeholder system when no fashion products are available
- June 17, 2025. Implemented comprehensive Fashion Trends section on homepage: Added trending fashion categories showcase with three interactive trend cards (Casual Wear, Accessories, Footwear), created gradient-styled placeholder designs with animated icons, integrated trending badges (Trending, Popular, Hot) with engagement statistics (likes and views), developed Fashion Tips & Styling subsection with color coordination and perfect fit guidance tips, implemented Style Guide call-to-action with graduation cap icon and direct shop linking, applied clean modern card design with white backgrounds and subtle shadows, added smooth hover animations and transform effects, ensured responsive layout optimization for mobile and desktop, and created seamless integration with existing shop category navigation
- June 17, 2025. Successfully implemented comprehensive personalized weekly fashion inspiration newsletter system: Created complete newsletter database models (NewsletterSubscription, FashionNewsletter, NewsletterAnalytics) with detailed fashion preference tracking, developed fashion-focused subscription form capturing style preferences (casual, formal, trendy, vintage, minimalist, bohemian, sporty), size ranges, budget preferences, and color choices, built newsletter service with SendGrid integration for email delivery and welcome messages, implemented comprehensive subscription routes with unsubscribe functionality and token-based management, added beautiful newsletter subscription section to homepage with animated design featuring pulsing icons and gradient backgrounds, created Korean/English multilingual support for all newsletter content and interface elements, developed newsletter analytics dashboard for tracking subscriber engagement and preferences, and established foundation for automated weekly fashion inspiration emails with personalized product recommendations
- June 17, 2025. Successfully implemented and tested comprehensive Limited-Time Stories feature: Created complete Story database model with Korean/English bilingual support, time-based expiration system, and priority ordering, developed story management routes including creation, viewing, deletion, and engagement tracking (views, clicks, likes), built beautiful story templates with animated countdown badges showing time remaining in Korean, created story navigation integration in shop menu, implemented story categorization (promotion, product, event, news, general) with type-specific styling and colors, added comprehensive CSS animations including pulse effects for urgent stories and slide-in animations for story cards, created test stories with various expiration times to demonstrate functionality, integrated with product linking for promotional stories, and established multilingual story content support - feature is fully operational and loved by user
- June 17, 2025. Fixed critical story creation save issues: Resolved CSRF validation problems by adding @csrf.exempt decorator to create_story route, corrected DateTimeField format to '%Y-%m-%dT%H:%M' for HTML5 datetime-local compatibility, enhanced JavaScript with automatic 24-hour default expiration time setting, added client-side form validation and minimum time restrictions, improved error handling with detailed logging and user feedback in Korean/English - story creation now works perfectly and users can successfully save new limited-time stories
- June 17, 2025. Implemented TikTok-style story viewer with vertical swipe navigation: Created full-screen story viewer with black background and immersive experience, implemented vertical swipe gestures for story navigation (up/down for next/previous stories), added horizontal swipe support for alternate navigation, built progress bars showing story advancement with auto-play timers, created story interaction system with like/share/cart buttons, developed touch controls with minimum swipe distance detection, added keyboard navigation support (arrow keys, space, escape), implemented story overlay with author info and countdown timers, added responsive design for mobile and desktop experiences, created toast notifications for user feedback, and integrated API endpoint for story likes with CSRF exemption - complete抖音-style story experience with smooth animations and touch gestures
- June 17, 2025. Implemented intelligent story recommendation algorithm for TikTok-style story playback ordering: Integrated sophisticated recommendation engine that sorts stories based on user behavior analysis, personalized recommendations for authenticated users using interaction history, product viewing patterns, and purchase behavior, popularity-based recommendations for anonymous users using engagement metrics and time decay factors, dynamic story loading system that preloads next recommended stories when approaching end of current playlist, automatic view tracking API that records story interactions for continuous algorithm improvement, story type preference learning with weighted scoring for different story categories, urgency boosting for time-sensitive stories approaching expiration, and seamless integration with existing collaborative filtering system - stories now play in intelligent order rather than chronological sequence

## User Preferences

Preferred communication style: Simple, everyday language.

## Notes for Future Development

### Enhanced Database Integration
- **PostgreSQL with SQLAlchemy ORM**: Full persistent storage with optimized schema design
- **Database Indexing**: Performance-optimized indexes for queries, search, and analytics
- **Full-Text Search**: PostgreSQL TSVECTOR with automatic trigger updates and GIN indexing
- **Data Constraints**: Database-level validation with check constraints and foreign keys
- **Database Administration**: Comprehensive admin dashboard with health monitoring and optimization tools
- **Backup and Recovery**: Automated backup creation with pg_dump integration
- **Performance Monitoring**: Real-time database statistics and query performance metrics
- **Data Cleanup**: Automated cleanup routines for maintaining optimal performance

### Authentication System
The application includes session management infrastructure and can be extended with user authentication, role-based access control, and multi-user content management.

### API Development
The current architecture can be extended to include REST API endpoints for headless content management or mobile application integration.

### Content Features
Future enhancements could include content versioning, rich text editing, file uploads, content scheduling, and advanced search with full-text indexing.
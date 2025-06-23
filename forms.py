from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SelectField, SubmitField, DecimalField, IntegerField, BooleanField, DateTimeField, SelectMultipleField, EmailField
from wtforms.validators import DataRequired, Length, NumberRange, Optional, Email

class ContentForm(FlaskForm):
    """Form for creating new content"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        Length(min=1, max=10000, message='Content must be between 1 and 10000 characters')
    ])
    
    category = SelectField('Category', validators=[DataRequired(message='Category is required')])
    
    status = SelectField('Status', validators=[DataRequired(message='Status is required')])
    
    author = StringField('Author', validators=[
        DataRequired(message='Author is required'),
        Length(min=1, max=100, message='Author must be between 1 and 100 characters')
    ])
    
    tags = StringField('Tags', validators=[
        Length(max=500, message='Tags must be less than 500 characters')
    ], description='Separate tags with commas')
    
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'], 'Only image files are allowed!')
    ], description='Upload an image (JPG, PNG, GIF, WEBP, SVG)')
    
    files = FileField('Additional Files', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'mp4', 'webm', 'avi', 'mov', 'wmv', 'flv', 
                    'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'zip', 'rar', '7z', 'tar', 'gz', 
                    'csv', 'xlsx', 'xls', 'ppt', 'pptx'], 'File type not allowed!')
    ], description='Upload documents, videos, audio, or archive files')
    
    submit = SubmitField('Create Content')

class EditContentForm(FlaskForm):
    """Form for editing existing content"""
    title = StringField('Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    
    content = TextAreaField('Content', validators=[
        DataRequired(message='Content is required'),
        Length(min=1, max=10000, message='Content must be between 1 and 10000 characters')
    ])
    
    category = SelectField('Category', validators=[DataRequired(message='Category is required')])
    
    status = SelectField('Status', validators=[DataRequired(message='Status is required')])
    
    author = StringField('Author', validators=[
        DataRequired(message='Author is required'),
        Length(min=1, max=100, message='Author must be between 1 and 100 characters')
    ])
    
    tags = StringField('Tags', validators=[
        Length(max=500, message='Tags must be less than 500 characters')
    ], description='Separate tags with commas')
    
    image = FileField('Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp', 'svg'], 'Only image files are allowed!')
    ], description='Upload a new image (JPG, PNG, GIF, WEBP, SVG) - leave empty to keep current image')
    
    files = FileField('Additional Files', validators=[
        FileAllowed(['pdf', 'doc', 'docx', 'txt', 'rtf', 'odt', 'mp4', 'webm', 'avi', 'mov', 'wmv', 'flv', 
                    'mp3', 'wav', 'ogg', 'flac', 'aac', 'm4a', 'zip', 'rar', '7z', 'tar', 'gz', 
                    'csv', 'xlsx', 'xls', 'ppt', 'pptx'], 'File type not allowed!')
    ], description='Upload additional documents, videos, audio, or archive files')
    
    submit = SubmitField('Update Content')

# Ecommerce Forms

class ProductForm(FlaskForm):
    """Form for creating/editing products"""
    name = StringField('Product Name', validators=[
        DataRequired(message='Product name is required'),
        Length(min=1, max=200, message='Product name must be between 1 and 200 characters')
    ])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message='Description is required'),
        Length(min=1, max=2000, message='Description must be between 1 and 2000 characters')
    ])
    
    price = DecimalField('Price ($)', validators=[
        DataRequired(message='Price is required'),
        NumberRange(min=0.01, message='Price must be greater than $0.01')
    ], places=2)
    
    category = SelectField('Category', validators=[DataRequired(message='Category is required')])
    
    stock_quantity = IntegerField('Stock Quantity', validators=[
        DataRequired(message='Stock quantity is required'),
        NumberRange(min=0, message='Stock quantity must be 0 or more')
    ])
    
    is_digital = BooleanField('Digital Product')
    
    # Seasonal Product Fields
    is_seasonal = BooleanField('Seasonal Product', description='Check if this product is only available during specific seasons')
    
    season_type = SelectField('Season Type', choices=[
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
    ], description='Select the season when this product is unavailable')
    
    seasonal_start = DateTimeField('Seasonal Start Date', 
                                 description='When seasonal availability starts (optional, leave empty to use season type)',
                                 validators=[Optional()])
    
    seasonal_end = DateTimeField('Seasonal End Date',
                               description='When seasonal availability ends (optional, leave empty to use season type)',
                               validators=[Optional()])
    
    seasonal_year = IntegerField('Seasonal Year', 
                               description='Specific year for seasonal item (optional, leave empty for recurring seasons)',
                               validators=[Optional()])
    
    image = FileField('Product Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ], description='Upload product image (JPG, PNG, GIF, WEBP)')
    
    submit = SubmitField('Save Product')

class AddToCartForm(FlaskForm):
    """Form for adding products to cart"""
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, max=100, message='Quantity must be between 1 and 100')
    ], default=1)
    
    submit = SubmitField('Add to Cart')

class UpdateCartForm(FlaskForm):
    """Form for updating cart item quantity"""
    quantity = IntegerField('Quantity', validators=[
        DataRequired(message='Quantity is required'),
        NumberRange(min=1, max=100, message='Quantity must be between 1 and 100')
    ])
    
    submit = SubmitField('Update')

class CheckoutForm(FlaskForm):
    """Form for checkout shipping information"""
    shipping_name = StringField('Full Name', validators=[
        DataRequired(message='Full name is required'),
        Length(min=1, max=100, message='Name must be between 1 and 100 characters')
    ])
    
    shipping_address = TextAreaField('Address', validators=[
        DataRequired(message='Address is required'),
        Length(min=1, max=500, message='Address must be between 1 and 500 characters')
    ])
    
    shipping_city = StringField('City', validators=[
        DataRequired(message='City is required'),
        Length(min=1, max=100, message='City must be between 1 and 100 characters')
    ])
    
    shipping_state = StringField('State/Province', validators=[
        DataRequired(message='State/Province is required'),
        Length(min=1, max=100, message='State/Province must be between 1 and 100 characters')
    ])
    
    shipping_zip = StringField('ZIP/Postal Code', validators=[
        DataRequired(message='ZIP/Postal Code is required'),
        Length(min=1, max=20, message='ZIP/Postal Code must be between 1 and 20 characters')
    ])
    
    shipping_country = StringField('Country', validators=[
        DataRequired(message='Country is required'),
        Length(min=1, max=100, message='Country must be between 1 and 100 characters')
    ], default='United States')
    
    submit = SubmitField('Proceed to Payment')

class StoryForm(FlaskForm):
    """Form for creating limited-time stories"""
    title = StringField('Story Title', validators=[
        DataRequired(message='Title is required'),
        Length(min=1, max=200, message='Title must be between 1 and 200 characters')
    ])
    
    content = TextAreaField('Story Content', validators=[
        Length(max=1000, message='Content must be less than 1000 characters')
    ], description='Brief description or content for the story')
    
    story_type = SelectField('Story Type', choices=[
        ('general', 'General'),
        ('product', 'Product'),
        ('event', 'Event'),
        ('news', 'News')
    ], validators=[DataRequired(message='Story type is required')])
    
    expires_at = DateTimeField('Expires At', validators=[
        DataRequired(message='Expiration time is required')
    ], description='When this story should expire (YYYY-MM-DD HH:MM)', format='%Y-%m-%dT%H:%M')
    
    priority = IntegerField('Priority', validators=[
        NumberRange(min=1, max=10, message='Priority must be between 1 and 10')
    ], default=1, description='Higher numbers appear first (1-10)')
    
    image = FileField('Story Image', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Only image files are allowed!')
    ], description='Upload an image for the story')
    
    product_id = SelectField('Related Product (Optional)', 
                           choices=[('', 'No product')], 
                           description='Link to a product if this is a product story')
    
    submit = SubmitField('Create Story')

class NewsletterSubscriptionForm(FlaskForm):
    """Form for newsletter subscription with fashion preferences"""
    email = EmailField('Email Address', validators=[
        DataRequired(message='Email is required'),
        Email(message='Please enter a valid email address')
    ])
    
    first_name = StringField('First Name', validators=[
        Optional(),
        Length(max=100, message='First name must be less than 100 characters')
    ])
    
    preferred_categories = SelectMultipleField('Fashion Categories', 
        choices=[
            ('Clothing', 'Clothing'),
            ('Accessories', 'Accessories'),
            ('Shoes', 'Shoes'),
            ('Bags', 'Bags'),
            ('Jewelry', 'Jewelry')
        ],
        validators=[DataRequired(message='Please select at least one category')]
    )
    
    style_preferences = SelectMultipleField('Style Preferences',
        choices=[
            ('casual', 'Casual'),
            ('formal', 'Formal'),
            ('trendy', 'Trendy'),
            ('vintage', 'Vintage'),
            ('minimalist', 'Minimalist'),
            ('bohemian', 'Bohemian'),
            ('sporty', 'Sporty')
        ],
        validators=[DataRequired(message='Please select at least one style preference')]
    )
    
    size_range = SelectField('Size Range', 
        choices=[
            ('XS', 'Extra Small (XS)'),
            ('S', 'Small (S)'),
            ('M', 'Medium (M)'),
            ('L', 'Large (L)'),
            ('XL', 'Extra Large (XL)'),
            ('XXL', '2XL'),
            ('varied', 'Varied/Multiple Sizes')
        ],
        validators=[Optional()]
    )
    
    budget_range = SelectField('Budget Range',
        choices=[
            ('budget', 'Budget-Friendly (Under $50)'),
            ('mid-range', 'Mid-Range ($50-$200)'),
            ('luxury', 'Luxury ($200+)'),
            ('varied', 'Varied Budget')
        ],
        validators=[Optional()]
    )
    
    color_preferences = SelectMultipleField('Favorite Colors',
        choices=[
            ('black', 'Black'),
            ('white', 'White'),
            ('gray', 'Gray'),
            ('navy', 'Navy'),
            ('blue', 'Blue'),
            ('red', 'Red'),
            ('pink', 'Pink'),
            ('green', 'Green'),
            ('yellow', 'Yellow'),
            ('brown', 'Brown'),
            ('beige', 'Beige'),
            ('purple', 'Purple')
        ],
        validators=[Optional()]
    )
    
    frequency = SelectField('Email Frequency',
        choices=[
            ('weekly', 'Weekly'),
            ('monthly', 'Monthly')
        ],
        validators=[DataRequired()],
        default='weekly'
    )
    
    submit = SubmitField('Subscribe to Fashion Newsletter')

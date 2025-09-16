from flask import Blueprint, request, jsonify
import re
import time
from jinja2 import Template

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat', methods=['POST'])
def chat():
    """Chat endpoint with SSTI vulnerability in issue reporting"""
    try:
        data = request.json
        action = data.get('action', '')
        message = data.get('message', '').strip()

        if action == 'menu':
            return jsonify({
                'response': 'Hello! Welcome to bl1tz Store Customer Support! 👋\n\nHow can I assist you today?',
                'buttons': [
                    {'text': '🛍️ Product Information', 'action': 'products'},
                    {'text': '📦 Order Status', 'action': 'orders'},
                    {'text': '🔄 Returns & Exchanges', 'action': 'returns'},
                    {'text': '🎯 Promotions & Deals', 'action': 'promotions'},
                    {'text': '🐛 Report Issue', 'action': 'report_issue'},
                    {'text': '💬 General Support', 'action': 'general'}
                ]
            })

        elif action == 'products':
            return jsonify({
                'response': 'Great! I can help you with product information. 🛍️\n\nWhat would you like to know?',
                'buttons': [
                    {'text': 'Electronics', 'action': 'category_electronics'},
                    {'text': 'Fashion', 'action': 'category_fashion'},
                    {'text': 'Home & Garden', 'action': 'category_home'},
                    {'text': 'Sports & Fitness', 'action': 'category_sports'},
                    {'text': 'Books', 'action': 'category_books'},
                    {'text': '← Back to Menu', 'action': 'menu'}
                ]
            })

        elif action == 'orders':
            return jsonify({
                'response': 'I can help you track your order! 📦\n\nPlease choose an option:',
                'buttons': [
                    {'text': 'Track Package', 'action': 'track_package'},
                    {'text': 'Order History', 'action': 'order_history'},
                    {'text': 'Shipping Information', 'action': 'shipping_info'},
                    {'text': '← Back to Menu', 'action': 'menu'}
                ]
            })

        elif action == 'returns':
            return jsonify({
                'response': 'I can assist with returns and exchanges! 🔄\n\nWhat do you need help with?',
                'buttons': [
                    {'text': 'Start Return Process', 'action': 'start_return'},
                    {'text': 'Return Policy', 'action': 'return_policy'},
                    {'text': 'Exchange Item', 'action': 'exchange_item'},
                    {'text': '← Back to Menu', 'action': 'menu'}
                ]
            })

        elif action == 'promotions':
            return jsonify({
                'response': 'Check out our amazing current deals! 🎯\n\n• 25% off Gaming Laptops (Code: GAME25)\n• Buy 2 Get 1 Free on accessories\n• Free shipping on orders over $100\n• Student discount: Extra 10% off',
                'buttons': [
                    {'text': 'View Electronics Deals', 'action': 'electronics_deals'},
                    {'text': 'Fashion Sales', 'action': 'fashion_deals'},
                    {'text': 'Apply Discount Code', 'action': 'apply_discount'},
                    {'text': '← Back to Menu', 'action': 'menu'}
                ]
            })

        elif action == 'report_issue':
            return jsonify({
                'response': 'I\'m sorry to hear you\'re experiencing an issue! 🐛\n\nOur technical team takes all reports seriously. Please describe your issue and I\'ll create a support ticket for you.',
                'input_mode': True,
                'input_placeholder': 'Describe your issue in detail...',
                'input_action': 'submit_issue'
            })

        elif action == 'submit_issue':
            if not message:
                return jsonify({'response': 'Please provide a description of your issue.'})

            if len(message) > 200:
                return jsonify({'response': 'Issue description is too long. Please keep it under 200 characters.'})

            blocked_patterns = [
                r'__import__',
                r'exec\s*\(',
                r'eval\s*\(',
                r'subprocess',
                r'\.system\s*\(',
                r'\.popen\s*\(',
                r'\.chr\s*\(',
                r'\.os\.',
                r'__globals__',
                r'__builtins__',
                r'\.read\s*\(',
                r'\.chr\s*\(',
                r'\.listdir\s*\(',
                r'/',
                r'\.\.',
            ]

            for pattern in blocked_patterns:
                if re.search(pattern, message, re.IGNORECASE):
                    return jsonify({"response": "Sorry, your issue description contains restricted content. Blocked patterns: '__import__', 'exec', 'eval', 'subprocess', 'system', 'popen', 'chr', 'os', '__globals__', '__builtins__', 'read', 'listdir', '/', '..'"})

            ticket_id = f"BLZ-{int(time.time())}"
            try:
                summary_template = f"""
Issue Ticket Summary:
━━━━━━━━━━━━━━━━━━━━━
Ticket ID: {ticket_id}
Status: Open
Priority: Normal

Customer Description:
{message}

Our technical team will review this ticket within 24 hours.
""".strip()

                template = Template(summary_template)
                ticket_summary = template.render()

                return jsonify({
                    'response': f'✅ Support ticket created successfully!\n\n{ticket_summary}\n\nIs there anything else I can help you with?',
                    'buttons': [
                        {'text': 'Create Another Ticket', 'action': 'report_issue'},
                        {'text': 'Check Ticket Status', 'action': 'ticket_status'},
                        {'text': '← Back to Menu', 'action': 'menu'}
                    ]
                })

            except Exception as e:
                return jsonify({'response': f'❌ Error creating ticket: {str(e)}\n\nPlease try again or contact our support team directly.'})

        elif action == 'general':
            return jsonify({
                'response': 'I\'m here to help with general questions! 💬\n\nWhat would you like to know?',
                'buttons': [
                    {'text': 'Store Hours', 'action': 'store_hours'},
                    {'text': 'Contact Information', 'action': 'contact_info'},
                    {'text': 'About bl1tz Store', 'action': 'about_store'},
                    {'text': '← Back to Menu', 'action': 'menu'}
                ]
            })

        elif action in ['category_electronics', 'category_fashion', 'category_home', 'category_sports', 'category_books']:
            category = action.replace('category_', '').title().replace('_', ' & ')
            return jsonify({
                'response': f'Here are our popular {category} items:\n\n• High-quality products\n• Competitive prices\n• Fast shipping\n• Great customer reviews\n\nWould you like me to show you specific products?',
                'buttons': [
                    {'text': 'Show Popular Items', 'action': f'popular_{action.split("_")[1]}'},
                    {'text': 'Price Range Filter', 'action': 'price_filter'},
                    {'text': '← Back to Products', 'action': 'products'}
                ]
            })

        elif action == 'store_hours':
            return jsonify({
                'response': '🕒 bl1tz Store Hours:\n\nOnline Store: 24/7 available\nCustomer Support: 24/7 live chat\nPhone Support: Mon-Fri 8AM-8PM EST\nEmail Support: 24/7 (2-hour response)',
                'buttons': [{'text': '← Back to Menu', 'action': 'menu'}]
            })

        elif action == 'contact_info':
            return jsonify({
                'response': '📞 Contact bl1tz Store:\n\nPhone: 1-800-BL1TZ-24\nEmail: support@bl1tz.com\nLive Chat: Available now!\nAddress: 123 Commerce St, Tech City, TC 12345',
                'buttons': [{'text': '← Back to Menu', 'action': 'menu'}]
            })

        else:
            return jsonify({
                'response': 'I didn\'t understand that request. Let me show you the main menu.',
                'buttons': [
                    {'text': '🛍️ Product Information', 'action': 'products'},
                    {'text': '📦 Order Status', 'action': 'orders'},
                    {'text': '🔄 Returns & Exchanges', 'action': 'returns'},
                    {'text': '🎯 Promotions & Deals', 'action': 'promotions'},
                    {'text': '🐛 Report Issue', 'action': 'report_issue'},
                    {'text': '💬 General Support', 'action': 'general'}
                ]
            })

    except Exception as e:
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.'})

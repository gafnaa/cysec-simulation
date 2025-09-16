import re
import logging
from typing import Optional, List, Dict

class XSSProtection:
    DANGEROUS_CHARS = {
        '\\': '\\\\',
        '<': '\\<',
        '>': '\\>',
        '"': '\\"',
        "'": "\\'",
        '&': '\\&',
        '(': '\\(',
        ')': '\\)',
        '{': '\\{',
        '}': '\\}',
        '[': '\\[',
        ']': '\\]',
        '=': '\\=',
        ';': '\\;',
        ':': '\\:',
        '!': '\\!',
        '@': '\\@',
        '#': '\\#',
        '$': '\\$',
        '%': '\\%',
        '^': '\\^',
        '*': '\\*',
        '`': '\\`',
        '~': '\\~',
        '|': '\\|',
        '\n': '\\\\n',
        '\r': '\\\\r',
        '\t': '\\\\t',
    }

    DANGEROUS_PATTERNS = [
        r'javascript\s*:',
        r'data\s*:\s*text/html',
        r'data\s*:\s*application/javascript',
        r'<\s*script[^>]*>.*?</\s*script\s*>',
        r'<\s*script[^>]*>',
        r'</\s*script\s*>',
        r'<\s*iframe[^>]*>',
        r'</\s*iframe\s*>',
        r'<\s*object[^>]*>',
        r'</\s*object\s*>',
        r'<\s*embed[^>]*>',
        r'<\s*applet[^>]*>',
        r'</\s*applet\s*>',
        r'<\s*link[^>]*>',
        r'<\s*meta[^>]*>',
        r'<\s*style[^>]*>.*?</\s*style\s*>',
        r'<\s*style[^>]*>',
        r'</\s*style\s*>',
        r'<\s*form[^>]*>',
        r'</\s*form\s*>',
        r'<\s*input[^>]*>',
        r'<\s*textarea[^>]*>',
        r'</\s*textarea\s*>',
        r'<\s*button[^>]*>',
        r'</\s*button\s*>',
        r'<\s*select[^>]*>',
        r'</\s*select\s*>',
        r'on\w+\s*=\s*["\'][^"\']*["\']',
        r'on\w+\s*=\s*\w+',
        r'data\s*:[^,]*,',
        r'base64\s*,',
        r'expression\s*\(',
        r'url\s*\(\s*["\']?\s*javascript:',
        r'url\s*\(\s*["\']?\s*data:',
        r'alert\s*\(',
        r'confirm\s*\(',
        r'prompt\s*\(',
        r'eval\s*\(',
        r'setTimeout\s*\(',
        r'setInterval\s*\(',
        r'Function\s*\(',
        r'constructor\s*\(',
        r'vbscript\s*:',
        r'livescript\s*:',
        r'mocha\s*:',
        r'file\s*:',
        r'ftp\s*://',
        r'<\s*xml[^>]*>',
        r'</\s*xml\s*>',
        r'<\s*xsl:[^>]*>',
        r'<\s*svg[^>]*>.*?</\s*svg\s*>',
        r'import\s+',
        r'@import\s+',
    ]
    
    SUSPICIOUS_SEQUENCES = [
        '&lt;', '&gt;', '&amp;', '&quot;', '&#',
        'String.fromCharCode', 'unescape', 'decodeURI',
        'window.', 'document.', 'location.',
        'innerHTML', 'outerHTML', 'insertAdjacentHTML'
    ]
    
    @classmethod
    def sanitize_search_input(cls, user_input: Optional[str]) -> str:
        if not user_input or not isinstance(user_input, str):
            return ""
        if len(user_input) > 1000:
            user_input = user_input[:1000]
        
        sanitized = user_input
        
        for pattern in cls.DANGEROUS_PATTERNS:
            try:
                sanitized = re.sub(pattern, '[..]', sanitized, flags=re.IGNORECASE | re.DOTALL)
            except re.error:
                continue
        
        for char in ['\\'] + [c for c in cls.DANGEROUS_CHARS.keys() if c != '\\']:
            if char in sanitized:
                sanitized = sanitized.replace(char, cls.DANGEROUS_CHARS[char])
        
        sanitized = cls._clean_encoding_bypasses(sanitized)
        
        return sanitized
    
    @classmethod
    def _clean_encoding_bypasses(cls, text: str) -> str:
        text = re.sub(r'&[#\w]+;', '[ENTITY]', text)
        text = re.sub(r'\\u[0-9a-fA-F]{4}', '[UNICODE]', text)
        text = re.sub(r'\\x[0-9a-fA-F]{2}', '[HEX]', text)
        text = re.sub(r'%[0-9a-fA-F]{2}', '[ENCODED]', text)
        
        return text
    
    @classmethod
    def is_potentially_malicious(cls, user_input: Optional[str]) -> bool:
        if not user_input or not isinstance(user_input, str):
            return False
        
        for pattern in cls.DANGEROUS_PATTERNS:
            try:
                if re.search(pattern, user_input, flags=re.IGNORECASE | re.DOTALL):
                    return True
            except re.error:
                continue
        
        lower_input = user_input.lower()
        for sequence in cls.SUSPICIOUS_SEQUENCES:
            if sequence.lower() in lower_input:
                return True
        special_char_count = sum(1 for char in user_input if char in cls.DANGEROUS_CHARS)
        if len(user_input) > 0 and special_char_count > len(user_input) * 0.4:
            return True
        
        encoding_indicators = ['%', '&', '\\u', '\\x']
        encoding_count = sum(1 for indicator in encoding_indicators if indicator in user_input)
        if encoding_count >= 2:
            return True
        
        if len(user_input) > 1000:
            return True
        
        return False
    
    @classmethod
    def get_safety_report(cls, user_input: Optional[str]) -> Dict[str, any]:
        if not user_input:
            return {
                'is_safe': True,
                'original_length': 0,
                'sanitized_length': 0,
                'patterns_found': [],
                'risk_level': 'NONE'
            }
        
        is_malicious = cls.is_potentially_malicious(user_input)
        sanitized = cls.sanitize_search_input(user_input)
        patterns_found = []
        for pattern in cls.DANGEROUS_PATTERNS:
            try:
                if re.search(pattern, user_input, flags=re.IGNORECASE | re.DOTALL):
                    patterns_found.append(pattern)
            except re.error:
                continue
        
        if not is_malicious:
            risk_level = 'LOW'
        elif len(patterns_found) <= 2:
            risk_level = 'MEDIUM'
        else:
            risk_level = 'HIGH'
        
        return {
            'is_safe': not is_malicious,
            'original_length': len(user_input),
            'sanitized_length': len(sanitized),
            'patterns_found': patterns_found[:5],
            'risk_level': risk_level,
            'special_char_ratio': sum(1 for c in user_input if c in cls.DANGEROUS_CHARS) / len(user_input),
            'sanitized_input': sanitized
        }
xss_protection = XSSProtection()
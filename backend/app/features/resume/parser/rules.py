"""
Rule-based extraction for structured data from text.
Uses regex patterns to extract emails, phones, dates, etc.
"""
import re
from datetime import datetime
from typing import Any

import phonenumbers

from app.core.logging import get_logger

logger = get_logger(__name__)


class ExtractionRules:
    """Rule-based extractors for resume data."""
    
    # Regex patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(?:\+?\d{1,3}[-.\s]?)?(?:\(?\d{2,4}\)?[-.\s]?)?\d{3,4}[-.\s]?\d{3,4}'
    URL_PATTERN = r'https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&/=]*)'
    
    # Date patterns (various formats)
    DATE_PATTERNS = [
        r'(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* ?\d{4}',
        r'\d{1,2}/\d{4}',
        r'\d{4}',
    ]
    
    # Section headers
    SECTION_HEADERS = {
        'education': [
            r'\b(?:education|academic|qualification|degree)\b',
            r'\b(?:university|college|school|institute)\b'
        ],
        'experience': [
            r'\b(?:experience|employment|work history|career)\b',
            r'\b(?:professional experience)\b'
        ],
        'projects': [
            r'\b(?:projects?|portfolio)\b',
            r'\b(?:academic projects?|personal projects?)\b'
        ],
        'skills': [
            r'\b(?:skills?|technical skills?|technologies)\b',
            r'\b(?:competencies|expertise|proficiency)\b'
        ],
        'certifications': [
            r'\b(?:certifications?|certificates?|licenses?)\b'
        ],
        'achievements': [
            r'\b(?:achievements?|awards?|honors?|accomplishments?)\b'
        ]
    }
    
    @staticmethod
    def extract_email(text: str) -> list[str]:
        """Extract email addresses."""
        emails = re.findall(ExtractionRules.EMAIL_PATTERN, text, re.IGNORECASE)
        return list(set(emails))  # Remove duplicates
    
    @staticmethod
    def extract_phone(text: str) -> list[str]:
        """Extract and validate phone numbers."""
        potential_phones = re.findall(ExtractionRules.PHONE_PATTERN, text)
        
        valid_phones = []
        for phone in potential_phones:
            try:
                # Clean phone number
                cleaned = re.sub(r'[^\d+]', '', phone)
                if len(cleaned) >= 10:
                    # Try to parse with phonenumbers library
                    try:
                        parsed = phonenumbers.parse(cleaned, None)
                        if phonenumbers.is_valid_number(parsed):
                            formatted = phonenumbers.format_number(
                                parsed,
                                phonenumbers.PhoneNumberFormat.INTERNATIONAL
                            )
                            valid_phones.append(formatted)
                        else:
                            valid_phones.append(cleaned)
                    except:
                        valid_phones.append(cleaned)
            except:
                continue
        
        return list(set(valid_phones))
    
    @staticmethod
    def extract_urls(text: str) -> list[dict[str, str]]:
        """Extract URLs and categorize them."""
        urls = re.findall(ExtractionRules.URL_PATTERN, text, re.IGNORECASE)
        
        categorized = []
        for url in urls:
            url_lower = url.lower()
            
            if 'linkedin.com' in url_lower:
                url_type = 'linkedin'
            elif 'github.com' in url_lower:
                url_type = 'github'
            elif 'twitter.com' in url_lower or 'x.com' in url_lower:
                url_type = 'twitter'
            else:
                url_type = 'other'
            
            categorized.append({
                'type': url_type,
                'url': url
            })
        
        return categorized
    
    @staticmethod
    def extract_dates(text: str) -> list[str]:
        """Extract date strings from text."""
        dates = []
        for pattern in ExtractionRules.DATE_PATTERNS:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)
        return dates
    
    @staticmethod
    def parse_date(date_str: str) -> dict[str, Any] | None:
        """
        Parse date string into structured format.
        
        Returns:
            Dict with year, month, display or None
        """
        if not date_str:
            return None
        
        date_str = date_str.strip()
        
        # Try to extract year
        year_match = re.search(r'\d{4}', date_str)
        if not year_match:
            return None
        
        year = int(year_match.group())
        
        # Try to extract month
        month_names = {
            'jan': 1, 'feb': 2, 'mar': 3, 'apr': 4,
            'may': 5, 'jun': 6, 'jul': 7, 'aug': 8,
            'sep': 9, 'oct': 10, 'nov': 11, 'dec': 12
        }
        
        month = None
        for month_name, month_num in month_names.items():
            if month_name in date_str.lower():
                month = month_num
                break
        
        return {
            'year': year,
            'month': month,
            'display': date_str
        }
    
    @staticmethod
    def detect_sections(text: str) -> dict[str, list[tuple[int, int]]]:
        """
        Detect section boundaries in text.
        
        Returns:
            Dict mapping section names to list of (start, end) positions
        """
        sections = {}
        lines = text.split('\n')
        
        for section_name, patterns in ExtractionRules.SECTION_HEADERS.items():
            section_positions = []
            
            current_pos = 0
            for line_num, line in enumerate(lines):
                line_lower = line.lower().strip()
                
                # Check if line matches any section header pattern
                for pattern in patterns:
                    if re.search(pattern, line_lower):
                        # Found section start
                        start_pos = current_pos
                        
                        # Find section end (next section or end of text)
                        end_pos = len(text)
                        for next_line_num in range(line_num + 1, len(lines)):
                            next_line = lines[next_line_num].lower().strip()
                            # Check if it's another section header
                            is_header = False
                            for other_section, other_patterns in ExtractionRules.SECTION_HEADERS.items():
                                for other_pattern in other_patterns:
                                    if re.search(other_pattern, next_line):
                                        is_header = True
                                        break
                                if is_header:
                                    break
                            
                            if is_header:
                                end_pos = current_pos + sum(len(l) + 1 for l in lines[line_num:next_line_num])
                                break
                        
                        section_positions.append((start_pos, end_pos))
                        break
                
                current_pos += len(line) + 1
            
            if section_positions:
                sections[section_name] = section_positions
        
        return sections
    
    @staticmethod
    def extract_skills(text: str) -> list[str]:
        """
        Extract technical skills from text.
        
        This is a simplified version - production would use a skill database.
        """
        # Common technical skills (simplified list)
        common_skills = [
            # Languages
            'Python', 'JavaScript', 'Java', 'C\\+\\+', 'C#', 'Ruby', 'Go', 'Rust',
            'TypeScript', 'PHP', 'Swift', 'Kotlin', 'R', 'MATLAB', 'Scala',
            
            # Web
            'React', 'Angular', 'Vue', 'Node\\.js', 'Express', 'Django', 'Flask',
            'FastAPI', 'Spring', 'ASP\\.NET', 'Laravel', 'Rails',
            
            # Databases
            'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Elasticsearch',
            'SQLite', 'Oracle', 'SQL Server', 'Cassandra', 'DynamoDB',
            
            # Cloud
            'AWS', 'Azure', 'GCP', 'Docker', 'Kubernetes', 'Terraform',
            
            # Tools
            'Git', 'Linux', 'Bash', 'CI/CD', 'Jenkins', 'GitHub Actions'
        ]
        
        found_skills = []
        for skill in common_skills:
            pattern = r'\b' + skill + r'\b'
            if re.search(pattern, text, re.IGNORECASE):
                # Get the actual matched text to preserve casing
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    found_skills.append(match.group())
        
        return list(set(found_skills))
    
    @staticmethod
    def extract_name_from_top(text: str) -> str | None:
        """
        Extract name from top of document.
        Assumes name is in first few lines.
        """
        lines = text.split('\n')
        
        # Look at first 5 non-empty lines
        for line in lines[:5]:
            line = line.strip()
            if not line:
                continue
            
            # Skip lines that are likely headers/emails
            if '@' in line or 'resume' in line.lower():
                continue
            
            # Simple heuristic: name is 2-4 words, starts with capital
            words = line.split()
            if 2 <= len(words) <= 4 and words[0][0].isupper():
                return line
        
        return None

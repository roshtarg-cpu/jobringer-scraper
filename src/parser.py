"""Parser functions for extracting job data from jobringer.com."""
import re
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def _extract_next_data(html):
    """Extract __NEXT_DATA__ JSON if present."""
    match = re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>', html, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except:
            pass
    return None


def parse_job_listing(html, url):
    """Parse a job detail page and extract all fields."""
    soup = BeautifulSoup(html, 'lxml')
    
    job_data = {
        'jobTitle': None,
        'company': None,
        'location': None,
        'salary': None,
        'experience': None,
        'jobType': None,
        'skills': None,
        'postedDate': None,
        'description': None,
        'url': url,
        'scrapedAt': datetime.now(timezone.utc).isoformat()
    }
    
    # Try __NEXT_DATA__ first
    next_data = _extract_next_data(html)
    if next_data:
        # Parse from structured data if available
        pass
    
    # Fallback to HTML parsing
    try:
        # Job title - usually in h1
        title_tag = soup.find('h1')
        if title_tag:
            job_data['jobTitle'] = title_tag.get_text(strip=True)
        
        # Company - look for common patterns
        company_selectors = [
            ('span', {'class': re.compile(r'company', re.I)}),
            ('div', {'class': re.compile(r'company', re.I)}),
            ('a', {'class': re.compile(r'company', re.I)}),
        ]
        for tag, attrs in company_selectors:
            company_tag = soup.find(tag, attrs)
            if company_tag:
                job_data['company'] = company_tag.get_text(strip=True)
                break
        
        # Location
        location_selectors = [
            ('span', {'class': re.compile(r'location|city', re.I)}),
            ('div', {'class': re.compile(r'location|city', re.I)}),
        ]
        for tag, attrs in location_selectors:
            location_tag = soup.find(tag, attrs)
            if location_tag:
                job_data['location'] = location_tag.get_text(strip=True)
                break
        
        # Salary - look for currency symbols
        salary_pattern = re.compile(r'(₹|Rs\.?|INR)\s*[\d,]+([-–]\s*(₹|Rs\.?|INR)?\s*[\d,]+)?(\s*(per|\/)\s*(month|annum|year))?', re.I)
        salary_match = salary_pattern.search(html)
        if salary_match:
            job_data['salary'] = salary_match.group(0).strip()
        
        # Experience
        exp_pattern = re.compile(r'(\d+[\s-]*(?:to|-)[\s-]*\d+|fresher|\d+\+?)\s*(?:years?|yrs?)', re.I)
        exp_match = exp_pattern.search(html)
        if exp_match:
            job_data['experience'] = exp_match.group(0).strip()
        
        # Job type
        job_type_keywords = ['full-time', 'part-time', 'contract', 'remote', 'work from home', 'permanent']
        for keyword in job_type_keywords:
            if keyword.lower() in html.lower():
                job_data['jobType'] = keyword.title()
                break
        
        # Skills - look for skills section
        skills_selectors = [
            ('div', {'class': re.compile(r'skill|requirement|qualification', re.I)}),
            ('ul', {'class': re.compile(r'skill|requirement|qualification', re.I)}),
        ]
        for tag, attrs in skills_selectors:
            skills_tag = soup.find(tag, attrs)
            if skills_tag:
                skills_text = skills_tag.get_text(' ', strip=True)
                job_data['skills'] = skills_text[:500]  # Limit length
                break
        
        # Posted date
        date_pattern = re.compile(r'(\d{1,2}[\s/-]\d{1,2}[\s/-]\d{2,4}|(?:posted|updated)\s+\d+\s+(?:day|hour|week)s?\s+ago)', re.I)
        date_match = date_pattern.search(html)
        if date_match:
            job_data['postedDate'] = date_match.group(0).strip()
        
        # Description - main content area
        desc_selectors = [
            ('div', {'class': re.compile(r'description|detail|content|job-detail', re.I)}),
            ('div', {'id': re.compile(r'description|detail|content', re.I)}),
        ]
        for tag, attrs in desc_selectors:
            desc_tag = soup.find(tag, attrs)
            if desc_tag:
                # Clean up the description
                desc_text = desc_tag.get_text('\n', strip=True)
                job_data['description'] = desc_text[:2000]  # Limit length
                break
        
    except Exception as e:
        print(f'Error parsing job data: {e}')
    
    return job_data


def parse_job_links(html):
    """Extract job listing URLs from a search/listing page."""
    soup = BeautifulSoup(html, 'lxml')
    links = []
    
    # Look for job links - common patterns
    job_link_patterns = [
        re.compile(r'/job[s]?/[\w-]+'),
        re.compile(r'/vacancy/[\w-]+'),
        re.compile(r'/position/[\w-]+'),
        re.compile(r'job-\d+'),
        re.compile(r'/[\w-]+-job-in-'),
    ]
    
    for link_tag in soup.find_all('a', href=True):
        href = link_tag.get('href', '')
        
        for pattern in job_link_patterns:
            if pattern.search(href):
                # Make absolute URL if needed
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = f'https://jobringer.com{href}'
                else:
                    full_url = f'https://jobringer.com/{href}'
                
                if full_url not in links:
                    links.append(full_url)
                break
    
    return links

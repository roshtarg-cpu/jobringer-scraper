"""Parser functions for extracting job data from jobringer.com."""
import re
import json
from datetime import datetime, timezone
from bs4 import BeautifulSoup


def _extract_json_ld(html):
    """Extract JSON-LD structured data if present."""
    match = re.search(r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>', html, re.DOTALL)
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
    
    # Try JSON-LD first (most reliable source)
    json_ld = _extract_json_ld(html)
    if json_ld:
        try:
            if 'title' in json_ld:
                job_data['jobTitle'] = json_ld['title']
            if 'hiringOrganization' in json_ld and 'name' in json_ld['hiringOrganization']:
                job_data['company'] = json_ld['hiringOrganization']['name']
            if 'employmentType' in json_ld:
                job_data['jobType'] = json_ld['employmentType']
            if 'datePosted' in json_ld:
                job_data['postedDate'] = json_ld['datePosted']
            if 'description' in json_ld:
                job_data['description'] = json_ld['description'][:2000]
        except Exception as e:
            print(f'Error parsing JSON-LD: {e}')
    
    # Parse HTML structure (jobringer-specific IDs and structure)
    try:
        # Job title - specific ID
        if not job_data['jobTitle']:
            title_tag = soup.find('h1', {'id': 'job-title'})
            if not title_tag:
                title_tag = soup.find('h1')
            if title_tag:
                job_data['jobTitle'] = title_tag.get_text(strip=True)
        
        # Company - specific ID
        if not job_data['company']:
            company_tag = soup.find('p', {'id': 'job-company'})
            if not company_tag:
                # Fallback to link with company details
                company_link = soup.find('a', href=re.compile(r'company-details'))
                if company_link:
                    company_tag = company_link.find('p')
                    if not company_tag:
                        company_tag = company_link
            if company_tag:
                job_data['company'] = company_tag.get_text(strip=True)
        
        # Location - specific ID with nested structure
        location_span = soup.find('span', {'id': 'job-location'})
        if location_span:
            # Try to get the nested p tag
            location_p = location_span.find('p', {'itemprop': 'jobLocation'})
            if location_p:
                location_text = location_p.get_text(strip=True)
                if location_text:
                    job_data['location'] = location_text
        
        # Salary - specific ID with nested structure
        salary_span = soup.find('span', {'id': 'job-salary'})
        if salary_span:
            salary_p = salary_span.find('p', {'itemprop': 'estimatedSalary'})
            if salary_p:
                salary_text = salary_p.get_text(strip=True)
                if salary_text and salary_text.lower() != 'not disclosed':
                    job_data['salary'] = salary_text
        
        # Experience - specific ID with nested structure
        exp_span = soup.find('span', {'id': 'job-experience'})
        if exp_span:
            exp_p = exp_span.find('p', {'itemprop': 'experienceRequirements'})
            if exp_p:
                job_data['experience'] = exp_p.get_text(strip=True)
        
        # Job type - specific ID with nested structure
        if not job_data['jobType']:
            jobtype_span = soup.find('span', {'id': 'job-type'})
            if jobtype_span:
                jobtype_p = jobtype_span.find('p', {'itemprop': 'employmentType'})
                if jobtype_p:
                    job_data['jobType'] = jobtype_p.get_text(strip=True)
        
        # Skills - job-keyword spans
        skill_tags = soup.find_all('span', {'class': 'job-keyword'})
        if skill_tags:
            skills = [tag.get_text(strip=True) for tag in skill_tags]
            job_data['skills'] = ', '.join(skills)
        
        # Posted date - look for "Posted on" text
        if not job_data['postedDate']:
            # Find text containing "Posted on"
            for elem in soup.find_all(string=re.compile(r'Posted on', re.I)):
                parent = elem.parent
                if parent:
                    # Get the highlight span next to it
                    highlight = parent.find('span', {'class': 'highlight'})
                    if highlight:
                        job_data['postedDate'] = highlight.get_text(strip=True)
                        break
        
        # Description - from job-details-content
        if not job_data['description'] or len(job_data['description']) < 100:
            desc_tag = soup.find('div', {'id': 'job-details-content'})
            if desc_tag:
                # Get text from description
                desc_text = desc_tag.get_text('\n', strip=True)
                job_data['description'] = desc_text[:2000]  # Limit length
        
    except Exception as e:
        print(f'Error parsing job data: {e}')
    
    return job_data


def parse_job_links(html):
    """Extract job listing URLs from a search/listing page."""
    soup = BeautifulSoup(html, 'lxml')
    links = []
    
    # UPDATED: More comprehensive link patterns for jobringer.com
    # Based on actual site structure analysis
    job_link_patterns = [
        re.compile(r'/job[s]?/[\w-]+', re.I),
        re.compile(r'/vacancy/[\w-]+', re.I),
        re.compile(r'/position/[\w-]+', re.I),
        re.compile(r'job-\d+', re.I),
        re.compile(r'/[\w-]+-job-in-', re.I),
        re.compile(r'/job-detail', re.I),
        re.compile(r'/jobdetails', re.I),
        re.compile(r'view.*job', re.I),
    ]
    
    # Also look for data attributes that might contain job IDs
    for element in soup.find_all(['div', 'a'], attrs={'data-job-id': True}):
        job_id = element.get('data-job-id')
        if job_id:
            full_url = f'https://jobringer.com/job/{job_id}'
            if full_url not in links:
                links.append(full_url)
    
    # Parse all links
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
    
    # If still no links found, try to find ANY links that might be jobs
    # by looking for links with text containing job-related keywords
    if len(links) == 0:
        for link_tag in soup.find_all('a', href=True):
            text = link_tag.get_text(strip=True).lower()
            href = link_tag.get('href', '')
            
            # Skip navigation and common non-job links
            if any(skip in href.lower() for skip in ['login', 'signup', 'register', 'pricing', 'about', 'contact', 'faq', 'terms', 'privacy']):
                continue
            
            # Look for job-related text
            if any(keyword in text for keyword in ['apply', 'view job', 'details', 'opening']) and href:
                if href.startswith('http'):
                    full_url = href
                elif href.startswith('/'):
                    full_url = f'https://jobringer.com{href}'
                else:
                    continue
                
                if 'jobringer.com' in full_url and full_url not in links:
                    links.append(full_url)
    
    return links

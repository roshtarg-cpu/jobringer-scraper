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
            title_tag = soup.find('h1', {'id': 'job-title'}) or soup.find('h1')
            if title_tag:
                job_data['jobTitle'] = title_tag.get_text(strip=True)
        
        # Company - specific ID
        if not job_data['company']:
            company_tag = soup.find('p', {'id': 'job-company'})
            if not company_tag:
                company_link = soup.find('a', href=re.compile(r'company-details'))
                if company_link:
                    company_tag = company_link.find('p') or company_link
            if company_tag:
                job_data['company'] = company_tag.get_text(strip=True)
        
        # Location
        location_span = soup.find('span', {'id': 'job-location'})
        if location_span:
            location_p = location_span.find('p', {'itemprop': 'jobLocation'})
            if location_p:
                job_data['location'] = location_p.get_text(strip=True)
        
        # Salary
        salary_span = soup.find('span', {'id': 'job-salary'})
        if salary_span:
            salary_p = salary_span.find('p', {'itemprop': 'estimatedSalary'})
            if salary_p:
                salary_text = salary_p.get_text(strip=True)
                if salary_text and salary_text.lower() != 'not disclosed':
                    job_data['salary'] = salary_text
        
        # Experience
        exp_span = soup.find('span', {'id': 'job-experience'})
        if exp_span:
            exp_p = exp_span.find('p', {'itemprop': 'experienceRequirements'})
            if exp_p:
                job_data['experience'] = exp_p.get_text(strip=True)
        
        # Job type
        if not job_data['jobType']:
            jobtype_span = soup.find('span', {'id': 'job-type'})
            if jobtype_span:
                jobtype_p = jobtype_span.find('p', {'itemprop': 'employmentType'})
                if jobtype_p:
                    job_data['jobType'] = jobtype_p.get_text(strip=True)
        
        # Skills
        skill_tags = soup.find_all('span', {'class': 'job-keyword'})
        if skill_tags:
            skills = [tag.get_text(strip=True) for tag in skill_tags]
            job_data['skills'] = ', '.join(skills)
        
        # Posted date
        if not job_data['postedDate']:
            for elem in soup.find_all(string=re.compile(r'Posted on', re.I)):
                parent = elem.parent
                if parent:
                    highlight = parent.find('span', {'class': 'highlight'})
                    if highlight:
                        job_data['postedDate'] = highlight.get_text(strip=True)
                        break
        
        # Description
        if not job_data['description'] or len(job_data['description']) < 100:
            desc_tag = soup.find('div', {'id': 'job-details-content'})
            if desc_tag:
                desc_text = desc_tag.get_text('\n', strip=True)
                job_data['description'] = desc_text[:2000]
        
    except Exception as e:
        print(f'Error parsing job data: {e}')
    
    return job_data


def parse_job_links(html):
    """Extract job listing URLs from a search/listing page.
    
    Based on live site analysis (Aug 2026):
    - Job cards have class .job-card
    - Job links follow pattern: /job/{slug}/{8-hex-id}
    - Example: /job/software-developer/96018b76
    """
    soup = BeautifulSoup(html, 'lxml')
    links = []
    
    # Strategy 1: Look for .job-card containers
    job_cards = soup.select('.job-card')
    if job_cards:
        for card in job_cards:
            # Find link starting with /job/ or job/
            job_link = card.select_one('a[href^="/job/"]') or card.select_one('a[href^="job/"]')
            if job_link:
                href = job_link.get('href', '')
                # Validate pattern: /job/{slug}/{8-hex-id}
                if re.match(r'/job/[\w-]+/[0-9a-f]{8}$', href):
                    full_url = f'https://jobringer.com{href}' if href.startswith('/') else f'https://jobringer.com/{href}'
                    if full_url not in links:
                        links.append(full_url)
    
    # Strategy 2: Look in #jobs-container
    if not links:
        jobs_container = soup.select_one('#jobs-container')
        if jobs_container:
            for link_tag in jobs_container.find_all('a', href=True):
                href = link_tag.get('href', '')
                if re.match(r'/job/[\w-]+/[0-9a-f]{8}$', href):
                    full_url = f'https://jobringer.com{href}' if href.startswith('/') else f'https://jobringer.com/{href}'
                    if full_url not in links:
                        links.append(full_url)
    
    # Strategy 3: Scan all links for correct pattern
    if not links:
        for link_tag in soup.find_all('a', href=True):
            href = link_tag.get('href', '')
            # Match ONLY /job/{slug}/{8-hex-id}
            # SKIP /jobs, /applyCredits, /job-listing.php, company-details
            if re.match(r'/job/[\w-]+/[0-9a-f]{8}$', href):
                if href in ['/jobs', '/applyCredits']:
                    continue
                if 'company-details' in href or 'job-listing.php' in href:
                    continue
                full_url = f'https://jobringer.com{href}' if href.startswith('/') else f'https://jobringer.com/{href}'
                if full_url not in links:
                    links.append(full_url)
    
    return links

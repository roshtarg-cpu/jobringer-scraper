"""Main actor logic for jobringer scraper."""
import asyncio
from apify import Actor
from .utils import _fetch
from .parser import parse_job_listing, parse_job_links


async def main():
    """Main actor entry point."""
    async with Actor:
        # Get input
        actor_input = await Actor.get_input() or {}
        
        search_query = actor_input.get('searchQuery', '')
        location = actor_input.get('location', '')
        job_type = actor_input.get('jobType', 'Any')
        experience_level = actor_input.get('experienceLevel', 'Any')
        salary_min = actor_input.get('salaryMin', 0)
        include_description = actor_input.get('includeDescription', True)
        max_results = actor_input.get('maxResults', 50)
        proxy_config = actor_input.get('proxyConfiguration')
        
        Actor.log.info(f'Starting jobringer scraper: query={search_query}, location={location}, max={max_results}')
        
        # Create proxy URL if configured
        proxy_url = None
        if proxy_config and proxy_config.get('useApifyProxy'):
            proxy_password = Actor.get_env().get('APIFY_PROXY_PASSWORD')
            if proxy_password:
                groups = proxy_config.get('apifyProxyGroups', ['RESIDENTIAL'])
                group = groups[0] if groups else 'RESIDENTIAL'
                proxy_url = f'http://auto:{proxy_password}@proxy.apify.com:8000'
                Actor.log.info(f'Using Apify proxy: {group}')
        
        # Build search URL
        base_url = 'https://jobringer.com'
        
        # Construct search URL based on inputs
        if search_query or location:
            search_parts = []
            if search_query:
                search_parts.append(f'jobs-in-{search_query.lower().replace(" ", "-")}')
            if location:
                search_parts.append(f'{location.lower().replace(" ", "-")}')
            search_url = f'{base_url}/{"-".join(search_parts)}'
        else:
            search_url = f'{base_url}/jobs'
        
        Actor.log.info(f'Search URL: {search_url}')
        
        # Track stats
        item_count = 0
        request_count = 0
        error_count = 0
        processed_urls = set()
        
        # Fetch search results with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                Actor.log.info(f'Fetching search page (attempt {attempt + 1}/{max_retries})')
                request_count += 1
                
                search_html = await _fetch(search_url, proxy_url)
                
                if not search_html:
                    raise Exception('No content returned from search page')
                
                # Parse job links
                job_links = parse_job_links(search_html)
                Actor.log.info(f'Found {len(job_links)} job links')
                
                if not job_links:
                    Actor.log.warning('No job links found on search page')
                    # Try alternative search URL
                    if attempt < max_retries - 1:
                        search_url = f'{base_url}/jobs'
                        await asyncio.sleep(5)
                        continue
                
                # Limit to max_results
                job_links = job_links[:max_results]
                
                # Process each job
                for idx, job_url in enumerate(job_links):
                    if item_count >= max_results:
                        break
                    
                    if job_url in processed_urls:
                        continue
                    
                    processed_urls.add(job_url)
                    
                    try:
                        Actor.log.info(f'Processing job {idx + 1}/{len(job_links)}: {job_url}')
                        request_count += 1
                        
                        # Fetch job detail page
                        job_html = await _fetch(job_url, proxy_url)
                        
                        if not job_html:
                            Actor.log.warning(f'No content for {job_url}')
                            error_count += 1
                            continue
                        
                        # Parse job data
                        job_data = parse_job_listing(job_html, job_url)
                        
                        # Skip if no title (invalid job)
                        if not job_data.get('jobTitle'):
                            Actor.log.warning(f'No job title found for {job_url}')
                            error_count += 1
                            continue
                        
                        # If includeDescription is False, remove description to save space
                        if not include_description:
                            job_data['description'] = None
                        
                        # Push to dataset
                        await Actor.push_data(job_data)
                        item_count += 1
                        
                        if item_count % 10 == 0:
                            Actor.log.info(f'Progress: {item_count} jobs scraped')
                        
                        # Rate limiting
                        await asyncio.sleep(2)
                        
                    except Exception as e:
                        Actor.log.error(f'Error processing {job_url}: {e}')
                        error_count += 1
                        await asyncio.sleep(5)
                
                # Success - break retry loop
                break
                
            except Exception as e:
                Actor.log.error(f'Search attempt {attempt + 1} failed: {e}')
                error_count += 1
                
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 10
                    Actor.log.info(f'Retrying in {wait_time} seconds...')
                    await asyncio.sleep(wait_time)
                else:
                    Actor.log.error('All retry attempts exhausted')
        
        # Save task context
        await Actor.set_value('SAVED-TASK', {
            'actorId': Actor.get_env().get('actor_id'),
            'actorRunId': Actor.get_env().get('actor_run_id'),
            'defaultDatasetId': Actor.get_env().get('default_dataset_id'),
            'startedAt': Actor.get_env().get('started_at'),
            'input': actor_input,
            'stats': {
                'itemsScraped': item_count,
                'requestsMade': request_count,
                'errors': error_count
            }
        })
        
        Actor.log.info(f'Scraping complete: {item_count} jobs, {request_count} requests, {error_count} errors')

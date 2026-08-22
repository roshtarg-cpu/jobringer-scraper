# 🎯 JobRinger Jobs Scraper — AI-Ready Data Extraction

[![Apify Actor](https://img.shields.io/badge/Apify-Actor-00D4FF?logo=apify)](https://apify.com/fervent_bus/jobringer-scraper)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python)](https://www.python.org/)
[![AI Agents](https://img.shields.io/badge/AI-Ready-00A67E?logo=openai)](https://apify.com)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-7C3AED)](https://modelcontextprotocol.io)

Extract structured job listings from **JobRinger.com** — India's growing job portal with 196K+ monthly visitors. Perfect for **Claude AI**, **ChatGPT**, and **AI agent** automation via **Apify MCP integration**.

---

## 🎯 Features

✅ **Zero Competition** — First JobRinger scraper on Apify Store  
✅ **AI-First Design** — Structured output for Claude, ChatGPT, LangChain  
✅ **Comprehensive Filters** — Search by keyword, location, job type, experience, salary  
✅ **Rich Data Extraction** — Title, company, location, salary, skills, full descriptions  
✅ **MCP Integration** — Works seamlessly with Apify Model Context Protocol  
✅ **Reliable Scraping** — Residential proxies + browser automation bypass protection  
✅ **Pay Per Result** — Only pay for jobs extracted ($0.005/job + $0.05 start fee)

---

## 📊 Output Data Schema

Each job listing includes:

| Field | Type | Description |
|-------|------|-------------|
| **jobTitle** | string | Position title (e.g., "Senior Software Engineer") |
| **company** | string | Hiring organization name |
| **location** | string | Job location (city, state) |
| **salary** | string | Salary range or package (e.g., "₹8-12 LPA") |
| **experience** | string | Required experience (e.g., "3-5 years") |
| **jobType** | string | Employment type (Full-time, Remote, etc.) |
| **skills** | string | Required skills and qualifications |
| **postedDate** | string | When the job was posted |
| **description** | string | Full job description |
| **url** | string | Direct link to job posting |
| **scrapedAt** | datetime | Extraction timestamp (ISO 8601) |

---

## 🚀 Quick Start

### 1️⃣ Run on Apify Console

```json
{
  "searchQuery": "python developer",
  "location": "Bangalore",
  "jobType": "Full-time",
  "experienceLevel": "3-5 years",
  "salaryMin": 800000,
  "includeDescription": true,
  "maxResults": 50
}
```

### 2️⃣ Use with Apify API

```bash
curl -X POST https://api.apify.com/v2/acts/fervent_bus~jobringer-scraper/runs \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_APIFY_TOKEN" \
  -d '{
    "searchQuery": "data scientist",
    "location": "Mumbai",
    "maxResults": 100
  }'
```

### 3️⃣ Python SDK

```python
from apify_client import ApifyClient

client = ApifyClient('YOUR_APIFY_TOKEN')
run = client.actor('fervent_bus/jobringer-scraper').call(
    run_input={
        'searchQuery': 'machine learning',
        'location': 'Hyderabad',
        'maxResults': 200
    }
)

for item in client.dataset(run['defaultDatasetId']).iterate_items():
    print(f"{item['jobTitle']} at {item['company']} - {item['salary']}")
```

---

## 🤖 AI Agent Integration

### Use with Claude via Apify MCP

```typescript
// Claude Desktop config.json
{
  "mcpServers": {
    "apify": {
      "command": "npx",
      "args": ["-y", "@apify/mcp-server-apify"]
    }
  }
}
```

**Example Claude prompt:**
> "Use the JobRinger scraper to find all remote Python developer jobs in India with 5+ years experience and salary above ₹15 LPA. Export results as CSV."

### ChatGPT Integration

Use Apify's GPT action to let ChatGPT scrape JobRinger:

```yaml
# Custom GPT Action
POST https://api.apify.com/v2/acts/fervent_bus~jobringer-scraper/runs
Authorization: Bearer {APIFY_TOKEN}
Body: {
  "searchQuery": "{user_query}",
  "maxResults": 100
}
```

### LangChain / AutoGPT

```python
from langchain.tools import Tool
from apify_client import ApifyClient

def scrape_jobringer(query: str, location: str = "India"):
    client = ApifyClient('YOUR_TOKEN')
    run = client.actor('fervent_bus/jobringer-scraper').call(
        run_input={'searchQuery': query, 'location': location}
    )
    return list(client.dataset(run['defaultDatasetId']).iterate_items())

jobringer_tool = Tool(
    name="JobRinger Scraper",
    func=lambda q: scrape_jobringer(q),
    description="Search Indian job market via JobRinger.com"
)
```

---

## 💡 Use Cases

🔹 **Recruitment Automation** — Auto-source candidates matching JD criteria  
🔹 **Salary Benchmarking** — Analyze compensation trends by role/location  
🔹 **Market Intelligence** — Track hiring patterns, skill demand, company growth  
🔹 **Job Aggregation** — Build custom job boards for niche industries  
🔹 **AI-Powered Matching** — Feed data to LLMs for candidate-job matching  
🔹 **Competitive Analysis** — Monitor competitor hiring strategies

---

## 📋 Input Configuration

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| **searchQuery** | string | No | `""` | Job title or keywords (e.g., "software engineer") |
| **location** | string | No | `""` | City, state, or region (e.g., "Mumbai") |
| **jobType** | enum | No | `"Any"` | Full-time, Part-time, Contract, Remote, Work from Home |
| **experienceLevel** | enum | No | `"Any"` | Fresher, 0-1 years, 1-3 years, 3-5 years, 5-10 years, 10+ |
| **salaryMin** | integer | No | `0` | Minimum annual salary in INR (e.g., `500000`) |
| **includeDescription** | boolean | No | `true` | Extract full job descriptions (slower but detailed) |
| **maxResults** | integer | Yes | `50` | Maximum jobs to scrape (1-500) |
| **proxyConfiguration** | object | No | Residential | Apify proxy settings (recommended: RESIDENTIAL) |

---

## 🏆 Why This Scraper?

### ✅ Competitive Advantages

1. **First to Market** — No existing JobRinger scrapers on Apify Store
2. **AI-Native** — Designed for Claude, ChatGPT, MCP from day one
3. **Comprehensive Inputs** — 8 filter options vs competitors' 2-3
4. **Structured Output** — 11 fields including salary, skills, experience
5. **Reliable Extraction** — Camoufox browser + residential proxies bypass protection
6. **Cost-Effective** — Pay only for results, not runtime

### 📈 Target Market

- **India Job Market** — 196K monthly visitors, 3 competitors on Apify
- **Underserved Region** — Indian job portals less saturated than US/UK
- **Growing Demand** — AI recruitment tools gaining traction in India

---

## 🛠️ Technical Details

- **Language:** Python 3.11
- **Browser:** Camoufox (fingerprint-resistant Firefox)
- **Parsing:** BeautifulSoup4 + regex for data extraction
- **Proxies:** Apify Residential (recommended for reliability)
- **Rate Limiting:** 2-second delays between requests
- **Error Handling:** 3 retry attempts with exponential backoff

---

## 📚 Resources

- 📖 [Apify Documentation](https://docs.apify.com)
- 🤖 [MCP Integration Guide](https://docs.apify.com/platform/integrations/model-context-protocol)
- 💬 [Support Forum](https://community.apify.com)
- 🐛 [Report Issues](https://github.com/roshtarg-cpu/jobringer-scraper/issues)

---

## 📝 Example Output

```json
{
  "jobTitle": "Senior Python Developer",
  "company": "Tech Innovations Pvt Ltd",
  "location": "Bangalore, Karnataka",
  "salary": "₹10-15 LPA",
  "experience": "3-5 years",
  "jobType": "Full-time",
  "skills": "Python, Django, REST APIs, PostgreSQL, AWS",
  "postedDate": "2 days ago",
  "description": "We are seeking an experienced Python developer...",
  "url": "https://jobringer.com/jobs/senior-python-developer-bangalore-12345",
  "scrapedAt": "2026-08-22T00:45:00.000Z"
}
```

---

## 🏷️ Tags

`jobs` · `recruitment` · `india` · `jobringer` · `ai-agents` · `claude` · `chatgpt` · `mcp` · `automation` · `lead-generation`

---

## 📜 License

This actor is published under the [Apache 2.0 License](https://www.apache.org/licenses/LICENSE-2.0).

---

## 🌟 Support

⭐ **Star this actor** if it helps your workflow!  
💬 Questions? Open an issue or contact via Apify support.

**Compatible with:** Claude AI · ChatGPT · LangChain · AutoGPT · Model Context Protocol (MCP)

import json
import requests
from bs4 import BeautifulSoup
from typing import List, Dict
import os


class SHLScraper:
    """Scrapes SHL Individual Test Solutions catalog."""
    
    def __init__(self, output_path: str = "data/shl_catalog.json"):
        self.output_path = output_path
        self.catalog = []
    
    def scrape(self) -> List[Dict]:
        """
        Scrape SHL catalog from their product catalog with pagination support.
        
        Uses real HTML structure:
        - <tr data-entity-id="...">
        - <td class="custom__table-heading__title"><a href="...">Name</a></td>
        - <span class="product-catalogue__key">K</span>
        """
        try:
            base_url = "https://www.shl.com/products/product-catalog/"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
            }
            
            print("🔍 Starting SHL catalog scraping...")
            print(f"📍 Base URL: {base_url}\n")
            
            page_num = 0
            start = 0
            has_more = True
            
            # Pagination loop: start=0,12,24,36...
            while has_more:
                page_num += 1
                pagination_url = f"{base_url}?start={start}&type=1"
                
                print(f"📄 Page {page_num} | start={start}")
                
                try:
                    response = requests.get(pagination_url, headers=headers, timeout=10)
                    response.raise_for_status()
                    
                    soup = BeautifulSoup(response.content, 'html.parser')
                    
                    # Find all assessment rows in product table
                    assessment_rows = soup.find_all('tr', attrs={'data-entity-id': True})
                    
                    if not assessment_rows:
                        print(f"   ℹ️  No more assessments found. Stopping pagination.\n")
                        has_more = False
                        break
                    
                    page_count = 0
                    
                    # Parse each row
                    for row in assessment_rows:
                        try:
                            item = self._parse_assessment(row)
                            if item:
                                self.catalog.append(item)
                                page_count += 1
                        except Exception as e:
                            print(f"   ⚠️  Parse error: {e}")
                            continue
                    
                    print(f"   ✅ Found {page_count} assessments on this page")
                    print(f"   📊 Total so far: {len(self.catalog)}\n")
                    
                    if page_count == 0:
                        has_more = False
                    else:
                        start += 12  # Pagination increment
                    
                except requests.exceptions.RequestException as e:
                    print(f"   ❌ Request error: {e}")
                    has_more = False
                    break
            
            if self.catalog:
                print(f"✅ Scraping complete: {len(self.catalog)} assessments\n")
                return self.catalog
            else:
                print("❌ No assessments found. Using fallback catalog.\n")
                self.catalog = self._get_fallback_catalog()
                return self.catalog
                
        except Exception as e:
            print(f"❌ Scraping failed: {e}")
            print("📌 Using fallback catalog.\n")
            self.catalog = self._get_fallback_catalog()
            return self.catalog
    
    def _parse_assessment(self, row_element) -> Dict:
        """
        Parse individual assessment from table row.
        
        HTML structure:
        <tr data-entity-id="...">
            <td class="custom__table-heading__title">
                <a href="/products/product-catalog/view/.../">Assessment Name</a>
            </td>
            <span class="product-catalogue__key">K</span>
            ...
        </tr>
        """
        try:
            # Extract name and URL
            title_cell = row_element.find('td', class_='custom__table-heading__title')
            
            if not title_cell:
                return None
            
            link = title_cell.find('a')
            if not link:
                return None
            
            name = link.text.strip()
            relative_url = link.get('href', '')
            full_url = f"https://www.shl.com{relative_url}" if relative_url else ""
            
            if not name or not full_url:
                return None
            
            # Extract test type keys
            key_spans = row_element.find_all('span', class_='product-catalogue__key')
            test_types = [k.text.strip() for k in key_spans if k.text.strip()]
            
            # Join multiple test types or use first one
            test_type = test_types[0] if test_types else "O"
            
            return {
                "name": name,
                "url": full_url,
                "description": name,
                "test_type": test_type,
                "skills": [],
                "duration": None,
                "level": None,
                "remote_support": True
            }
            
        except Exception as e:
            print(f"   Parse error: {e}")
            return None
    
    def save_catalog(self) -> None:
        """Save catalog to JSON file with UTF-8 encoding."""
        os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
        
        try:
            with open(self.output_path, 'w', encoding='utf-8') as f:
                json.dump(self.catalog, f, indent=2, ensure_ascii=False)
            
            print(f"✅ Catalog saved to {self.output_path}")
            print(f"📊 Total assessments: {len(self.catalog)}\n")
            
        except Exception as e:
            print(f"❌ Error saving catalog: {e}\n")
    
    def _get_fallback_catalog(self) -> List[Dict]:
        """Return fallback catalog with SHL assessments."""
        return [
            {
                "name": "OPQ32r",
                "description": "Personality assessment measuring 32 personality dimensions",
                "url": "https://www.shl.com/en/products/individual-test-solutions/opq32r/",
                "test_type": "P",
                "skills": ["personality", "leadership", "interpersonal"],
                "duration": 25,
                "level": "All",
                "remote_support": True
            },
            {
                "name": "Verify Critical Reasoning",
                "description": "Tests critical reasoning and logical thinking",
                "url": "https://www.shl.com/en/products/individual-test-solutions/verify-critical-reasoning/",
                "test_type": "A",
                "skills": ["reasoning", "logical thinking", "problem solving"],
                "duration": 30,
                "level": "Graduate+",
                "remote_support": True
            },
            {
                "name": "Verify Situational Judgment",
                "description": "Assesses judgment in workplace scenarios",
                "url": "https://www.shl.com/en/products/individual-test-solutions/verify-situational-judgment/",
                "test_type": "S",
                "skills": ["decision making", "workplace judgment", "professionalism"],
                "duration": 20,
                "level": "Mid-level+",
                "remote_support": True
            },
            {
                "name": "Verify Verbal Reasoning",
                "description": "Evaluates verbal reasoning abilities",
                "url": "https://www.shl.com/en/products/individual-test-solutions/verify-verbal-reasoning/",
                "test_type": "A",
                "skills": ["verbal reasoning", "comprehension", "communication"],
                "duration": 17,
                "level": "Graduate+",
                "remote_support": True
            },
            {
                "name": "Verify Numerical Reasoning",
                "description": "Tests numerical reasoning and quantitative skills",
                "url": "https://www.shl.com/en/products/individual-test-solutions/verify-numerical-reasoning/",
                "test_type": "A",
                "skills": ["numerical reasoning", "quantitative", "data analysis"],
                "duration": 18,
                "level": "Graduate+",
                "remote_support": True
            },
            {
                "name": "Verify Inductive Reasoning",
                "description": "Assesses pattern recognition and inductive logic",
                "url": "https://www.shl.com/en/products/individual-test-solutions/verify-inductive-reasoning/",
                "test_type": "A",
                "skills": ["pattern recognition", "inductive reasoning", "analysis"],
                "duration": 20,
                "level": "Graduate+",
                "remote_support": True
            },
            {
                "name": "Java 8 (New)",
                "description": "Knowledge test for Java 8 programming",
                "url": "https://www.shl.com/en/products/individual-test-solutions/java-8/",
                "test_type": "K",
                "skills": ["Java", "Java 8", "programming"],
                "duration": 25,
                "level": "All",
                "remote_support": True
            },
            {
                "name": "Spring Framework",
                "description": "Knowledge test for Spring Framework skills",
                "url": "https://www.shl.com/en/products/individual-test-solutions/spring-framework/",
                "test_type": "K",
                "skills": ["Spring", "Spring Boot", "Java", "web development"],
                "duration": 30,
                "level": "Mid-level+",
                "remote_support": True
            },
            {
                "name": "Python Programming",
                "description": "Knowledge test for Python programming",
                "url": "https://www.shl.com/en/products/individual-test-solutions/python/",
                "test_type": "K",
                "skills": ["Python", "programming", "software development"],
                "duration": 28,
                "level": "All",
                "remote_support": True
            },
            {
                "name": "SQL (Advanced)",
                "description": "Advanced SQL knowledge assessment",
                "url": "https://www.shl.com/en/products/individual-test-solutions/sql-advanced/",
                "test_type": "K",
                "skills": ["SQL", "database", "advanced queries"],
                "duration": 32,
                "level": "Mid-level+",
                "remote_support": True
            },
            {
                "name": "Angular Knowledge",
                "description": "Frontend framework knowledge test",
                "url": "https://www.shl.com/en/products/individual-test-solutions/angular/",
                "test_type": "K",
                "skills": ["Angular", "TypeScript", "frontend", "web development"],
                "duration": 30,
                "level": "Mid-level+",
                "remote_support": True
            },
            {
                "name": "React Knowledge",
                "description": "React and JavaScript knowledge assessment",
                "url": "https://www.shl.com/en/products/individual-test-solutions/react/",
                "test_type": "K",
                "skills": ["React", "JavaScript", "frontend", "web development"],
                "duration": 25,
                "level": "Mid-level+",
                "remote_support": True
            },
            {
                "name": "AWS Solutions Architect",
                "description": "Cloud infrastructure and AWS knowledge",
                "url": "https://www.shl.com/en/products/individual-test-solutions/aws-solutions-architect/",
                "test_type": "K",
                "skills": ["AWS", "cloud", "infrastructure", "architecture"],
                "duration": 40,
                "level": "Senior",
                "remote_support": True
            },
            {
                "name": "Project Management Fundamentals",
                "description": "Core project management knowledge",
                "url": "https://www.shl.com/en/products/individual-test-solutions/pm-fundamentals/",
                "test_type": "K",
                "skills": ["project management", "planning", "stakeholder management"],
                "duration": 35,
                "level": "All",
                "remote_support": True
            },
            {
                "name": "Leadership & Management",
                "description": "Assessment of leadership and management capabilities",
                "url": "https://www.shl.com/en/products/individual-test-solutions/leadership-management/",
                "test_type": "S",
                "skills": ["leadership", "team management", "decision making", "strategic thinking"],
                "duration": 25,
                "level": "Manager+",
                "remote_support": True
            },
        ]
    

if __name__ == "__main__":
    scraper = SHLScraper()
    catalog = scraper.scrape()
    scraper.save_catalog()
    print(f"\n🎉 Scraping complete: {len(catalog)} assessments")


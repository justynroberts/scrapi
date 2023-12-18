
# Flask Web Scraper

A versatile web scraper built with Flask, BeautifulSoup, and SQLite. This tool allows users to define scraping tasks, which can be stored in a database and executed via a simple API. It also includes functionality for one-time scraping tasks and JSON data filtering using JMESPath.

## Features

-   **CRUD Operations:** Create, read, update, and delete scraping definitions in a SQLite database.
-   **Dynamic Scraping:** Execute scraping tasks based on stored definitions.
-   **JSON Data Filtering:** Use JMESPath queries to filter and transform scraped data.
-   **One-time Execution:** Test scraping tasks without saving definitions.
-   **Insert and Execute:** Add a new scraping definition and execute it in a single step.

## Setup

1.  **Clone the Repository:**
    
    bashCopy code
    
    `git clone [repository-url]` 
    
2.  **Install Dependencies:**
    
    bashCopy code
    
    `pip install flask beautifulsoup4 requests sqlite3 jmespath` 
    
3.  **Run the Application:**
    
    bashCopy code
    
    `python app.py` 
    

## Usage

### CRUD Operations

1.  **Create a New Scraping Definition:**
    
    -   Endpoint: `/definition`
    -   Method: `POST`
    -   Payload:
        
        jsonCopy code
        
        `{
          "endpoint": "example_scrape",
          "url": "https://example.com",
          "element_selector": ".example-class",
          "config": {
            "method": "GET",
            "headers": {
              "User-Agent": "Mozilla/5.0"
            }
          },
          "filter_expression": "expression"  // Optional JMESPath expression
        }` 
        
2.  **Update an Existing Definition:**
    
    -   Endpoint: `/definition/[id]`
    -   Method: `PUT`
3.  **Delete a Definition:**
    
    -   Endpoint: `/definition/[id]`
    -   Method: `DELETE`
4.  **Retrieve All Definitions:**
    
    -   Endpoint: `/getdefs`
    -   Method: `GET`

### Scraping Execution

-   **Execute a Defined Scraping Task:**
    
    -   Endpoint: `/scrape/[endpoint]`
    -   Method: `GET`
-   **One-time Execution:**
    
    -   Endpoint: `/test`
    -   Method: `POST`
    -   Payload: Same as the create operation, but not stored in the database.
-   **Insert and Execute:**
    
    -   Endpoint: `/insertexecute`
    -   Method: `POST`
    -   Payload: Same as the create operation, but executes immediately after insertion.

## Examples

1.  **Creating a Scraping Task:**
    
    bashCopy code
    
    `curl -X POST http://localhost:5000/definition -d '{
      "endpoint": "wiki_scrape",
      "url": "https://en.wikipedia.org/wiki/Main_Page",
      "element_selector": "#mp-upper .mp-h2",
      "config": {
        "method": "GET",
        "headers": {
          "User-Agent": "Mozilla/5.0"
        }
      }
    }'` 
    
2.  **Executing a Scraping Task:**
    
    bashCopy code
    
    `curl http://localhost:5000/scrape/wiki_scrape` 
    
3.  **One-time Scraping Execution:**
    
    bashCopy code
    
    `curl -X POST http://localhost:5000/test -d '{
      "url": "https://example.com",
      "element_selector": ".example-class",
      "config": {
        "method": "GET"
      }
    }'` 
    

## Filtering with JMESPath

JMESPath expressions can be used to filter and transform the JSON data returned by a scrape. For more information on JMESPath syntax, visit [JMESPath Tutorial](http://jmespath.org/tutorial.html).

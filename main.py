import sqlite3
from flask import Flask, request, jsonify
import requests
from bs4 import BeautifulSoup
import json
import jmespath  # Assuming you're using jmespath for filtering

# Setup and initialize the SQLite database
def setup_database():
    with sqlite3.connect('scraping.db') as conn:
        c = conn.cursor()
        c.execute('''
            CREATE TABLE IF NOT EXISTS scraping_definitions (
                id INTEGER PRIMARY KEY,
                endpoint TEXT NOT NULL,
                url TEXT NOT NULL,
                element_selector TEXT NOT NULL,
                config TEXT,
                filter_expression TEXT  -- New column for filter expression
            )
        ''')
        conn.commit()

setup_database()

# Initialize Flask app
app = Flask(__name__)

# Database operation functions
def execute_query(query, args=(), fetch_one=False, fetch_all=False):
    with sqlite3.connect('scraping.db') as conn:
        c = conn.cursor()
        c.execute(query, args)
        if fetch_one or fetch_all:
            result = c.fetchone() if fetch_one else c.fetchall()
        conn.commit()
        return result if fetch_one or fetch_all else None

# Generalized scraping function
def scrape(url, selector, config):
    headers = config.get('headers', {})
    method = config.get('method', 'GET')

    if method.upper() == 'GET':
        response = requests.get(url, headers=headers)
    elif method.upper() == 'POST':
        response = requests.post(url, headers=headers, data=config.get('data', {}))

    soup = BeautifulSoup(response.content, 'html.parser')
    items = soup.select(selector)
    return [item.get_text().strip() for item in items]

# Function to filter JSON data
def filter_json_data(data, query):
    try:
        return jmespath.search(query, data)
    except jmespath.exceptions.JMESPathError as e:
        return {"error": str(e)}

# CRUD operations with filter expression
@app.route('/definition', methods=['POST'])
def create_definition():
    data = request.json
    execute_query('''
        INSERT INTO scraping_definitions (endpoint, url, element_selector, config, filter_expression) 
        VALUES (?, ?, ?, ?, ?)
    ''', (data['endpoint'], data['url'], data['element_selector'], json.dumps(data.get('config', {})), data.get('filter_expression')))
    return jsonify({"status": "success"}), 201

@app.route('/definition/<int:def_id>', methods=['PUT'])
def update_definition(def_id):
    data = request.json
    execute_query('''
        UPDATE scraping_definitions SET endpoint = ?, url = ?, element_selector = ?, config = ?, filter_expression = ? WHERE id = ?
    ''', (data['endpoint'], data['url'], data['element_selector'], json.dumps(data.get('config', {})), data.get('filter_expression'), def_id))
    return jsonify({"status": "updated"}), 200

@app.route('/definition/<int:def_id>', methods=['DELETE'])
def delete_definition(def_id):
    execute_query('DELETE FROM scraping_definitions WHERE id = ?', (def_id,))
    return jsonify({"status": "deleted"}), 200

# Dynamic route for scraping with filter application
@app.route('/scrape/<endpoint>', methods=['GET'])
def dynamic_route(endpoint):
    definitions = execute_query('SELECT * FROM scraping_definitions WHERE endpoint = ?', (endpoint,), fetch_one=True)

    if definitions:
        config = json.loads(definitions[4]) if definitions[4] else {}
        filter_expression = definitions[5]
        data = scrape(definitions[2], definitions[3], config)

        if filter_expression:
            data = filter_json_data(data, filter_expression)
        return jsonify(data)

    return jsonify({"error": "Endpoint not found"}), 404

# Endpoint to get all definitions
@app.route('/getdefs', methods=['GET'])
def get_definitions():
    definitions = execute_query('SELECT * FROM scraping_definitions', fetch_all=True)
    return jsonify([{'id': defn[0], 'endpoint': defn[1], 'url': defn[2], 'element_selector': defn[3], 'config': json.loads(defn[4]) if defn[4] else {}, 'filter_expression': defn[5]} for defn in definitions])

# New endpoint to insert and execute in one command
@app.route('/insertexecute', methods=['POST'])
def insert_and_execute():
    data = request.json
    if not all(key in data for key in ['endpoint', 'url', 'element_selector']):
        return jsonify({"error": "Missing required fields"}), 400

    execute_query('''
        INSERT INTO scraping_definitions (endpoint, url, element_selector, config, filter_expression) 
        VALUES (?, ?, ?, ?, ?)
    ''', (data['endpoint'], data['url'], data['element_selector'], json.dumps(data.get('config', {})), data.get('filter_expression')))

    scraped_data = scrape(data['url'], data['element_selector'], data.get('config', {}))
    if data.get('filter_expression'):
        scraped_data = filter_json_data(scraped_data, data['filter_expression'])
    return jsonify(scraped_data)

# Endpoint for one-time execution without saving the definition
@app.route('/test', methods=['POST'])
def execute_once():
    try:
        data = request.json
        url = data['url']
        selector = data['element_selector']
        config = data.get('config', {})
        filter_expression = data.get('filter_expression')

        scraped_data = scrape(url, selector, config)
        if filter_expression:
            scraped_data = filter_json_data(scraped_data, filter_expression)
        return jsonify(scraped_data)

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(debug=True)

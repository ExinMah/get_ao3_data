import json
import AO3
from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/get_work_data', methods=['POST'])
def get_work_data():
    url = ''
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        data = json.loads(request.data)
        url = data['url']
    
    try:
        # Work ID used for getting the rest of the data
        workid = AO3.utils.workid_from_url(url)
        work = AO3.Work(workid)
        
        # Extract author usernames
        authors = [author.username for author in work.authors]
        print(work.authors)
        # Debug prints
        print("Authors:", authors)
        print("Date:", work.date_updated)
        
        # Assemble data
        work_data = {
            'title': work.title,
            'author': authors,
            'fandoms': work.fandoms,
            'chapters': work.nchapters,
            'ratings': work.rating,
            'warnings': work.warnings,
            'categories': work.categories,
            'tags': work.tags,
            'characters': work.characters,
            'relationships': work.relationships,
            'completed': work.complete,
            'date_updated': work.date_updated.strftime("%Y-%m-%d %H:%M:%S"),
            'date_published': work.date_published.strftime("%Y-%m-%d %H:%M:%S"),
            'words': work.words,
            'summary': work.summary,
        }
        
        # Print the assembled JSON for inspection
        #print("Work Data JSON:", json.dumps(work_data, indent=4))
        
        # Return the JSON as a response
        return json.dumps(work_data)
    
    except Exception as e:
        print("Error:", str(e))
        return json.dumps({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=False)

import json
import AO3
from threading import Thread
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

@app.route('/get_batch_work_data', methods=['POST'])
def get_batch_work_data():
    content_type = request.headers.get('Content-Type')
    if content_type == 'application/json':
        data = json.loads(request.data)
        urls = data.get('urls', [])  # Get the list of URLs from the request body

        # Validate input
        if not isinstance(urls, list) or not urls:
            return jsonify({'error': 'Invalid input. "urls" must be a non-empty list.'}), 400

        results = []  # To store the results for each URL
        errors = []   # To store errors for problematic URLs
        threads = []  # To store threads for parallel processing

        # Function to process a single URL
        def process_url(url):
            try:
                # Extract work ID from the URL
                workid = AO3.utils.workid_from_url(url)
                work = AO3.Work(workid, load=False)  # Initialize with load=False
                thread = work.reload(threaded=True)  # Reload metadata in a thread
                thread.join()  # Wait for the thread to finish

                # Check if work is available (e.g., for registered users only)
                if work.title is None:  # If title is None, it's likely a restricted work
                    raise ValueError("This work is only available to registered users of the Archive")

                # Extract author usernames
                authors = [author.username for author in work.authors]

                # Assemble data for this work
                work_data = {
                    'url': url,
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

                results.append(work_data)

            except ValueError as e:
                # Handle the specific case for registered users only
                error_message = str(e)
                errors.append({'url': url, 'error': error_message})

            except Exception as e:
                # Log other errors and add to the errors list
                error_message = f"Error processing URL {url}: {str(e)}"
                print(error_message)
                errors.append({'url': url, 'error': str(e)})

        # Start a thread for each URL
        for url in urls:
            thread = Thread(target=process_url, args=(url,))
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Build the response
        response = {
            'results': results,
            'errors': errors,
        }

        return jsonify(response)
    
    else:
        return jsonify({'error': 'Unsupported content type. Expecting application/json.'}), 400

if __name__ == '__main__':
    app.run(debug=False)

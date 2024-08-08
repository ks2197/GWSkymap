from flask import Flask, render_template
import json
import requests

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        file_path = r'C:\Users\Shubhankar Kulkarni\Downloads\local_superevents (1).json'  # replace with latest Local JSON Superevents File.

        with open(file_path, 'r') as file:
            data = json.load(file)

        events_data = data.get("superevents", [])  # Get all super events
        events_info = []

        for superevent in events_data:
            event_info = {}
            event_info['event_id'] = superevent.get("superevent_id", "")
            event_info['event_start_time'] = superevent.get("t_start", "")
            event_info['time_created'] = superevent.get("created", "")
            event_info['flat_resolution_sky_maps'] = []
            event_info['multi_resolution_sky_maps'] = []

            files_url = superevent.get("links", {}).get("files", "")
            if files_url:
                files_response = requests.get(files_url)
                files_data = files_response.json()

                for key, value in files_data.items():
                    if "bayestar.fits.gz" in key:
                        event_info['flat_resolution_sky_maps'].append(value)
                    elif "bayestar.multiorder.fits" in key:
                        event_info['multi_resolution_sky_maps'].append(value)

            events_info.append(event_info)

        return render_template('index.html', events_info=events_info)
    except FileNotFoundError:
        return "File not found!"
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == '__main__':
    app.run(debug=True)

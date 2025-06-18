from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify
from ice_breaker import ice_break_with

load_dotenv()

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.get_json()
        name = data.get('name')
        mock = data.get('mock', False)
        
        if not name:
            return jsonify({'error': 'Name is required'}), 400
        
        # Call your ice_break_with function
        summary, profile_picture_url, banner_url = ice_break_with(name, mock=mock)
        
        return jsonify({
            'summary': summary.to_dict(),
            'profile_picture_url': profile_picture_url,
            'banner_url': banner_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
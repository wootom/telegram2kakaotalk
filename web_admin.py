from flask import Flask, render_template_string, request, redirect, url_for, jsonify
import json
import os
import threading

app = Flask(__name__)
SETTINGS_FILE = 'settings.json'

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"mappings": [], "recent_sources": []}
    with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

@app.route('/')
def index():
    settings = load_settings()
    mappings = settings.get('mappings', [])
    recent_sources = settings.get('recent_sources', [])
    
    # Simple HTML Template
    template = """
    <!DOCTYPE html>
    <html lang="ko">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>텔레그램-카카오톡 포워더</title>
        <style>
            body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #f5f5f7; }
            h1 { color: #1d1d1f; }
            .card { background: white; padding: 20px; border-radius: 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; }
            table { width: 100%; border-collapse: collapse; margin-top: 10px; }
            th, td { padding: 12px; text-align: left; border-bottom: 1px solid #e5e5e5; }
            th { color: #86868b; font-weight: 600; }
            input, select, button { padding: 10px; border-radius: 8px; border: 1px solid #d2d2d7; font-size: 14px; }
            button { background-color: #0071e3; color: white; border: none; cursor: pointer; font-weight: 500; }
            button:hover { background-color: #0077ed; }
            button.delete { background-color: #ff3b30; }
            button.delete:hover { background-color: #ff453a; }
            .form-group { margin-bottom: 10px; display: flex; gap: 10px; align-items: center; }
            .tag { background: #e5e5ea; padding: 4px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; cursor: pointer; }
            .tag:hover { background: #d2d2d7; }
        </style>
        <script>
            function setSource(name) {
                document.getElementById('source').value = name;
            }
        </script>
    </head>
    <body>
        <h1>텔레그램-카카오톡 포워더</h1>
        
        <div class="card">
            <h2>📢 최근 감지된 소스 (클릭하여 추가)</h2>
            <div id="recents">
                {% for source in recent_sources %}
                    <span class="tag" onclick="setSource('{{ source }}')">{{ source }}</span>
                {% endfor %}
            </div>
        </div>

        <div class="card">
            <h2>➕ 새 연결 추가</h2>
            <form action="/add" method="post" class="form-group">
                <input type="text" id="source" name="source" placeholder="텔레그램 소스 이름 (예: 포비아)" required style="flex: 2;">
                <input type="text" name="target" placeholder="카카오톡 채팅방 (예: VAAX)" required style="flex: 1;">
                <button type="submit">추가</button>
            </form>
        </div>

        <div class="card">
            <h2>🔗 현재 연결 설정</h2>
            <table>
                <thead>
                    <tr>
                        <th>텔레그램 소스</th>
                        <th>➡</th>
                        <th>카카오톡 타겟</th>
                        <th>작업</th>
                    </tr>
                </thead>
                <tbody>
                    {% for mapping in mappings %}
                    <tr>
                        <td>{{ mapping.source }}</td>
                        <td>➡</td>
                        <td>{{ mapping.target }}</td>
                        <td>
                            <form action="/delete" method="post" style="margin:0;">
                                <input type="hidden" name="source" value="{{ mapping.source }}">
                                <input type="hidden" name="target" value="{{ mapping.target }}">
                                <button type="submit" class="delete">삭제</button>
                            </form>
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(template, mappings=mappings, recent_sources=recent_sources)

@app.route('/add', methods=['POST'])
def add_mapping():
    source = request.form['source']
    target = request.form['target']
    settings = load_settings()
    
    # Allow multiple targets for same source (Do not remove existing)
    # Check if this exact pair already exists to avoid duplicates
    exists = any(m['source'] == source and m['target'] == target for m in settings['mappings'])
    if not exists:
        settings['mappings'].append({'source': source, 'target': target})
    
    save_settings(settings)
    return redirect(url_for('index'))

@app.route('/delete', methods=['POST'])
def delete_mapping():
    source = request.form['source']
    target = request.form.get('target') # Get target from form to identify specific rule
    settings = load_settings()
    
    # Remove only the specific source-target pair
    if target:
        settings['mappings'] = [m for m in settings['mappings'] if not (m['source'] == source and m['target'] == target)]
    else:
        # Fallback: legacy delete (remove all by source if target not provided)
        settings['mappings'] = [m for m in settings['mappings'] if m['source'] != source]
        
    save_settings(settings)
    return redirect(url_for('index'))

def run_admin_server():
    app.run(host='127.0.0.1', port=5001)

if __name__ == '__main__':
    run_admin_server()

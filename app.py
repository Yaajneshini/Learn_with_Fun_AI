from flask import Flask, render_template_string, request, redirect, jsonify
import sqlite3
import random

app = Flask(__name__)

# ------------------------------
# Database setup
# ------------------------------
def init_db():
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS responses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            roll TEXT,
            response TEXT
        )
    """)
    conn.commit()
    conn.close()

def insert_response(roll, response):
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("INSERT INTO responses (roll, response) VALUES (?, ?)", (roll, response))
    conn.commit()
    conn.close()

def get_all_responses():
    conn = sqlite3.connect("responses.db")
    c = conn.cursor()
    c.execute("SELECT response FROM responses")
    data = c.fetchall()
    conn.close()
    return [d[0] for d in data]

init_db()

# ------------------------------
# HTML Template
# ------------------------------
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Learn with Fun</title>
    <style>
        body { 
            font-family: Arial, sans-serif; 
            background: #f7f9fc; 
            padding: 20px; 
            margin: 0;
        }
        h1 { 
            text-align: center; 
            color: #333; 
            margin-bottom: 20px; 
        }

        /* --- Tabs --- */
        .tabs {
            display: flex;
            justify-content: center;
            border-bottom: 2px solid #ddd;
            margin-bottom: 20px;
        }
        .tab {
            cursor: pointer;
            padding: 12px 25px;
            background: #eee;
            margin: 0 2px;
            border-radius: 8px 8px 0 0;
            font-weight: bold;
            color: #444;
            transition: all 0.3s ease;
        }
        .tab:hover {
            background: #ddd;
        }
        .tab.active {
            background: #fff;
            border: 2px solid #ddd;
            border-bottom: none;
            color: #222;
            box-shadow: 0 -2px 5px rgba(0,0,0,0.1);
        }

        /* --- Tab content --- */
        .tab-content {
            display: none;
            padding: 20px;
            background: #fff;
            border: 2px solid #ddd;
            border-radius: 0 8px 8px 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            max-width: 700px;
            margin: 0 auto;
        }
        .tab-content.active {
            display: block;
            animation: fadeIn 0.3s ease-in-out;
        }
        @keyframes fadeIn {
            from {opacity: 0;}
            to {opacity: 1;}
        }

        /* --- Attractive Input Form --- */
        .input-card {
            background: linear-gradient(135deg, #a0e7e5, #b4f8c8);
            padding: 25px;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            text-align: center;
        }
        .input-card h2 {
            margin-bottom: 15px;
            color: #222;
        }
        .input-card select, 
        .input-card input {
            width: 80%;
            padding: 12px;
            margin: 10px 0;
            border-radius: 8px;
            border: 1px solid #ccc;
            font-size: 16px;
            box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
        }
        .input-card button {
            background: #ff9aa2;
            color: white;
            border: none;
            padding: 12px 25px;
            border-radius: 8px;
            font-size: 16px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s ease;
        }
        .input-card button:hover {
            background: #ff6f7c;
        }

        /* --- Sticky Notes --- */
        .notes-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
        }
        .note { 
            display: inline-block; 
            padding: 15px 20px; 
            margin: 10px; 
            font-size: 18px; 
            font-weight: bold;
            color: #333; 
            border-radius: 8px; 
            box-shadow: 2px 2px 8px rgba(0,0,0,0.2);
            word-wrap: break-word; 
            max-width: 140px; 
            text-align: center; 
            transform-origin: center; 
            transition: transform 0.2s;
        }
        .note:hover { 
            transform: scale(1.1) rotate(2deg); 
        }

        .footer { 
            margin-top: 30px; 
            font-size: 14px; 
            font-style: italic; 
            color: #666; 
            text-align: center; 
        }
    </style>
    <script>
        function showTab(tabId) {
            document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));
            document.getElementById(tabId+'-tab').classList.add('active');
            document.getElementById(tabId+'-content').classList.add('active');
            localStorage.setItem("activeTab", tabId); // remember last tab
        }

        // Restore last active tab
        window.onload = function() {
            let lastTab = localStorage.getItem("activeTab") || "input";
            showTab(lastTab);

            // Start auto-refresh for Sticky Notes
            if(lastTab === "sticky"){
                startAutoRefresh();
            }
        }

        function startAutoRefresh(){
            setInterval(function(){
                let active = localStorage.getItem("activeTab");
                if(active === "sticky"){
                    fetch("/api/responses")
                        .then(res => res.json())
                        .then(data => {
                            let container = document.getElementById("notes-box");
                            container.innerHTML = "";
                            data.forEach(r => {
                                let div = document.createElement("div");
                                div.className = "note";
                                div.style.background = r.color;
                                div.style.transform = "rotate(" + r.rotate + "deg)";
                                div.innerText = r.text;
                                container.appendChild(div);
                            });
                        });
                }
            }, 3000);
        }
    </script>
</head>
<body>
    <h1>Learn with Fun</h1>
    <div style="text-align:center;">
        <h4>Developed by Yaajneshini</h4>
        <h4>Contemporary Avenues for Literary Research</h4>
        <b>Literature and AI</b>
        <br><br>
    </div>

    <div class="tabs">
        <div id="input-tab" class="tab active" onclick="showTab('input')">✍️ Input</div>
        <div id="sticky-tab" class="tab" onclick="showTab('sticky'); startAutoRefresh()">📝 Sticky Notes</div>
    </div>

    <div id="input-content" class="tab-content active">
        <div class="input-card">
            <h2>Student / Teacher Input Form</h2>
            <form method="POST">
                <label>Select your Roll Number:</label><br>
                <select name="roll" required>
                    {% for r in rolls %}
                    <option value="{{r}}">{{r}}</option>
                    {% endfor %}
                </select><br>

                <label>Your response about AI (one or two words):</label><br>
                <input type="text" name="response" required><br>

                <button type="submit">Submit Response</button>
            </form>
        </div>
    </div>

    <div id="sticky-content" class="tab-content">
        <h2 style="text-align:center;">Sticky Notes</h2>
        <div id="notes-box" class="notes-container">
            {% if responses %}
                {% for r in responses %}
                    <div class="note" style="background:{{random.choice(colors)}}; transform: rotate({{random.randint(-15,15)}}deg);">
                        {{r}}
                    </div>
                {% endfor %}
            {% else %}
                <p>No responses yet. Start submitting in the Input tab! ✅</p>
            {% endif %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def index():
    rolls = ["Teacher"] + [f"24AMEN{str(i).zfill(3)}" for i in range(1, 49)]
    colors = ["#FFD966", "#FFB6B9", "#A0E7E5", "#B4F8C8", "#FBE7C6", "#C3B1E1",
              "#FF9AA2", "#FFDAC1", "#E2F0CB", "#B5EAEA", "#FFCCF9", "#F6F5AE",
              "#D0CFFF", "#F7C6C7", "#C1FFD7"]

    if request.method == "POST":
        roll = request.form.get("roll")
        response = request.form.get("response")
        if response.strip():
            insert_response(roll, response.strip())
        return redirect("/")

    responses = get_all_responses()
    random.shuffle(responses)  # shuffle before sending
    return render_template_string(HTML_TEMPLATE, rolls=rolls, responses=responses, colors=colors, random=random)

# API endpoint for AJAX refresh
@app.route("/api/responses")
def api_responses():
    colors = ["#FFD966", "#FFB6B9", "#A0E7E5", "#B4F8C8", "#FBE7C6", "#C3B1E1",
              "#FF9AA2", "#FFDAC1", "#E2F0CB", "#B5EAEA", "#FFCCF9", "#F6F5AE",
              "#D0CFFF", "#F7C6C7", "#C1FFD7"]
    responses = get_all_responses()
    random.shuffle(responses)
    result = []
    for r in responses:
        result.append({
            "text": r,
            "color": random.choice(colors),
            "rotate": random.randint(-15, 15)
        })
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)

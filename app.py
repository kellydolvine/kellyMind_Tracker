import sqlite3
import os
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kelly_mind_ai_2026"

# Initialisation de la base de données
def init_db():
    conn = sqlite3.connect('bienetre.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            humeur TEXT,
            sommeil INTEGER,
            stress INTEGER,
            activite TEXT,
            indice_serenite INTEGER,
            analyse_ia TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Logique de l'IA KellyMind
def moteur_ia(humeur, sommeil, stress, activite):
    score = 50 + (sommeil * 5) - (stress * 4)
    if activite in ["sport", "lecture", "méditation"]: score += 15
    score = max(0, min(100, score))

    if score > 80:
        msg = f"Analyse IA : État optimal. Ton activité ({activite}) booste ton bien-être. Continue !"
    elif score > 50:
        msg = f"Analyse IA : Équilibre correct, mais surveille ton niveau de stress ({stress}/10)."
    else:
        msg = "Analyse IA : Alerte fatigue. Ton système nerveux a besoin de repos immédiat."
    
    return score, msg

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/enregistrer', methods=['POST'])
def enregistrer():
    humeur = request.form.get('humeur')
    sommeil = int(request.form.get('sommeil'))
    stress = int(request.form.get('stress'))
    activite = request.form.get('activite')

    score, analyse = moteur_ia(humeur, sommeil, stress, activite)

    conn = sqlite3.connect('bienetre.db')
    cursor = conn.cursor()
    cursor.execute('''INSERT INTO journal (humeur, sommeil, stress, activite, indice_serenite, analyse_ia) 
                      VALUES (?, ?, ?, ?, ?, ?)''', (humeur, sommeil, stress, activite, score, analyse))
    conn.commit()
    conn.close()
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    conn = sqlite3.connect('bienetre.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM journal ORDER BY id DESC')
    logs = cursor.fetchall()
    conn.close()
    return render_template('dashboard.html', logs=logs)

if __name__ == '__main__':
    # TRÈS IMPORTANT POUR RENDER :
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
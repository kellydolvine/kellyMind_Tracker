import sqlite3
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)
app.secret_key = "kelly_mind_ai_2026"

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

def moteur_ia(humeur, sommeil, stress, activite):
    # Calcul du score
    score = 50 + (sommeil * 5) - (stress * 4)
    if activite in ["sport", "lecture"]: score += 15
    score = max(0, min(100, score))

    # Génération de l'analyse IA
    if score > 80:
        msg = f"Analyse IA : État optimal détecté. Ton activité ({activite}) booste ta sérotonine. Continue ainsi !"
    elif score > 50:
        msg = f"Analyse IA : Équilibre fragile. Le sommeil ({sommeil}h) est correct, mais attention au pic de stress."
    else:
        msg = "Analyse IA : Alerte fatigue. Ton système nerveux demande une pause immédiate. Priorise le repos."
    
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
    app.run(debug=True)
import streamlit as st
import google.generativeai as genai
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- DATABÁZE POPISKŮ FONDŮ ---
POPISKY_FONDU = {
    "Conseq realitní": "Realitní fond zaměřený na komerční nemovitosti v ČR a Polsku. Nízké zadlužení (LTV 16 %), yield 7,6 %. Ideální jako konzervativní složka portfolia.",
    "Future X1": "Fond zaměřený na rezidenční novostavby a development.",
    "Conseq Invest Konzervativní": "Dluhopisový fond zaměřený na státní dluhopisy ČR, velmi nízké riziko.",
    "Conseq korporátních dluhopisů": "Fond investující do kvalitních firemních dluhopisů s vyšším výnosem.",
    "FF - World Fund": "Široce diverzifikovaný akciový fond investující do největších světových společností.",
    "BNP US Value Multi-Factor Equity": "Fond zaměřený na americké (USA) akcie s využitím hodnotových faktorů.",
    "Amundi Pioneer Global Equity": "Globální akciový fond zaměřený na růstové příležitosti po celém světě.",
    "J&T BOND": "Dluhopisový fond zaměřený na high-yield dluhopisy.",
    "FF - Global Dividend Fund": "Akciový fond zaměřený na dividendové společnosti.",
    "BNP Paribas Disruptive Technology": "Akciový fond zaměřený na technologie a inovace.",
    "Conseq Invest Akcie Nové Evropy A": "Fond zaměřený na trhy východní Evropy."
}

# --- SYSTÉMOVÝ PROMPT PRO AI ---
SYSTEM_PROMPT = """
Jsi expertní finanční poradce. Navrhni portfolio na platformě Conseq. 
Pokud klient chce ČISTĚ AKCIOVÉ portfolio, NEZAŘAZUJ reality ani dluhopisy.
Pokud klient chce nadvážit USA, přidej "BNP US Value Multi-Factor Equity".
Pokud klient chce pravidelnou investici, navrhni portfolio vhodné pro dlouhodobé spoření.
Vrať výsledek STRIKTNĚ jako JSON:
{
    "analyza": "Stručné zdůvodnění portfolia...",
    "jednorazova_investice": [{"fond": "Název", "vaha": "X %"}],
    "pravidelna_investice": [{"fond": "Název", "vaha": "X %"}]
}
"""

def generuj_pdf(jmeno_poradce, text_situace, analyza, jednorazove, pravidelne):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    
    story.append(Paragraph("Klientský investiční návrh", styles['Title']))
    story.append(Paragraph(f"Zpracoval: {jmeno_poradce}", styles['Normal']))
    story.append(Spacer(1, 12))
    story.append(Paragraph("Analýza", styles['Heading2']))
    story.append(Paragraph(analyza, styles['Normal']))
    
    def pridej_portfolio(data, nadpis):
        if data:
            story.append(Paragraph(nadpis, styles['Heading2']))
            t_data = [["Fond", "Váha"]] + [[r["fond"], r["vaha"]] for r in data]
            t = Table(t_data)
            story.append(t)
            for r in data:
                story.append(Paragraph(f"<b>{r['fond']}:</b> {POPISKY_FONDU.get(r['fond'], 'Popis není dostupný.')}", styles['Normal']))
    
    pridej_portfolio(jednorazove, "Jednorázová investice")
    pridej_portfolio(pravidelne, "Pravidelná investice")
    
    doc.build(story)
    buffer.seek(0)
    return buffer

# --- UI ---
st.title("🧠 AI Poradce (Gemini)")
api_key = st.sidebar.text_input("Vlož Gemini API klíč", type="password")
jmeno = st.text_input("Jméno poradce")
zadání = st.text_area("Situace klienta")

if st.button("Generovat"):
    if api_key:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        odpoved = model.generate_content(f"{SYSTEM_PROMPT}\nZadání: {zadání}")
        
        # Očištění výstupu od ```json značek
        text = odpoved.text.replace("```json", "").replace("```", "")
        data = json.loads(text)
        
        st.write(data["analyza"])
        st.table(data["jednorazova_investice"])
        
        pdf = generuj_pdf(jmeno, zadání, data["analyza"], data["jednorazova_investice"], data["pravidelna_investice"])
        st.download_button("Stáhnout PDF", pdf, "navrh.pdf", "application/pdf")

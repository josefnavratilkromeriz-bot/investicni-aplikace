import streamlit as st
import google.generativeai as genai
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet

# Databáze popisků
POPISKY_FONDU = {
    "Conseq realitní": "Realitní fond zaměřený na komerční nemovitosti (kanceláře, logistika). Nízké zadlužení (LTV 16 %), výnos 7,6 % p.a. Konzervativní realitní produkt.",
    "Future X1": "Fond zaměřený na rezidenční novostavby a development.",
    "Conseq Invest Konzervativní": "Dluhopisový fond, převážně státní dluhopisy ČR. Velmi nízké riziko.",
    "Conseq korporátních dluhopisů": "Fond investující do kvalitních firemních dluhopisů s vyšším výnosem.",
    "FF - World Fund": "Široce diverzifikovaný akciový fond na rozvinuté trhy.",
    "BNP US Value Multi-Factor Equity": "Fond zaměřený na americké (USA) akcie s využitím hodnotových faktorů.",
    "Amundi Pioneer Global Equity": "Globální akciový fond zaměřený na růstové příležitosti.",
    "J&T BOND": "Fond zaměřený na high-yield dluhopisy."
}

SYSTEM_PROMPT = """
Jsi expertní finanční poradce. Navrhni portfolio na platformě Conseq.
Pravidla: 
1. Pokud chce klient čistě akcie, nedávej tam reality/dluhopisy. 
2. Pokud chce USA, přidej "BNP US Value Multi-Factor Equity".
3. Vrať STRIKTNĚ tento JSON formát:
{
    "analyza": "Textové zdůvodnění...",
    "jednorazova_investice": [{"fond": "Název", "vaha": "X %"}],
    "pravidelna_investice": [{"fond": "Název", "vaha": "X %"}]
}
"""

def generuj_pdf(jmeno, situace, analyza, jednorazove, pravidelne):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    styles = getSampleStyleSheet()
    story.append(Paragraph("Klientský investiční návrh", styles['Title']))
    story.append(Paragraph(f"Zpracoval: {jmeno}", styles['Normal']))
    story.append(Paragraph("Analýza", styles['Heading2']))
    story.append(Paragraph(analyza, styles['Normal']))
    
    for data, nadpis in [(jednorazove, "Jednorázová investice"), (pravidelne, "Pravidelná investice")]:
        if data:
            story.append(Paragraph(nadpis, styles['Heading2']))
            t_data = [["Fond", "Váha"]] + [[r["fond"], r["vaha"]] for r in data]
            story.append(Table(t_data))
            for r in data:
                story.append(Paragraph(f"<b>{r['fond']}:</b> {POPISKY_FONDU.get(r['fond'], 'Popis není dostupný.')}", styles['Normal']))
    
    doc.build(story)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="AI Poradce", page_icon="🧠")
st.title("🧠 AI Poradce pro Conseq")
st.markdown("Aplikace automaticky analyzuje situaci klienta a navrhuje řešení na míru.")

# BEZPEČNÉ NAČTENÍ KLÍČE (aby aplikace nespadla, pokud klíč chybí)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    api_key = None

jmeno = st.text_input("Jméno poradce")
zadání = st.text_area("Situace klienta", height=150)

if st.button("Generovat návrh", type="primary"):
    if not api_key:
        st.error("Chyba: Nepodařilo se najít API klíč. Zkontrolujte prosím sekci 'Secrets' v nastavení Streamlitu.")
    elif not zadání.strip():
        st.warning("Prosím, vyplňte situaci klienta.")
    else:
        with st.spinner("AI analyzuje zadání..."):
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-1.5-flash')
                odpoved = model.generate_content(f"{SYSTEM_PROMPT}\nZadání: {zadání}")
                
                text = odpoved.text.replace("```json", "").replace("```", "").strip()
                data = json.loads(text)
                
                st.success("Analýza hotova!")
                st.write("### Zdůvodnění")
                st.write(data.get("analyza", ""))
                
                if data.get("jednorazova_investice"):
                    st.write("### Jednorázová investice")
                    st.table(data["jednorazova_investice"])
                if data.get("pravidelna_investice"):
                    st.write("### Pravidelná investice")
                    st.table(data["pravidelna_investice"])
                    
                pdf = generuj_pdf(jmeno, zadání, data.get("analyza", ""), data.get("jednorazova_investice", []), data.get("pravidelna_investice", []))
                st.download_button("📥 Stáhnout PDF report pro klienta", pdf, "navrh_ai.pdf", "application/pdf")
                
            except json.JSONDecodeError:
                st.error("AI vrátila data ve špatném formátu. Zkuste to prosím znovu (klikněte ještě jednou na Generovat).")
            except Exception as e:
                st.error(f"Došlo k chybě: {e}")

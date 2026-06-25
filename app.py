import streamlit as st
import io
import re
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Nastavení stránky Streamlitu
st.set_page_config(page_title="Investiční Asistent Poradce", layout="wide", page_icon="💼")

# --- ÚVODNÍ DATA: REÁLNÁ MODELOVÁ PORTFOLIA (CONSEQ) ---
MODEL_PORTFOLIA = {
    "do 3 let": {
        "Opatrný": [
            {"fond": "Conseq Invest Konzervativní", "vaha": "50%"},
            {"fond": "Conseq Invest Dluhopisový", "vaha": "50%"}
        ],
        "Vyvážený": [
            {"fond": "Conseq Invest Konzervativní", "vaha": "70%"},
            {"fond": "Future X1", "vaha": "15%"},
            {"fond": "Conseq realitní", "vaha": "15%"}
        ],
        "Dynamický": [
            {"fond": "Conseq Invest Konzervativní", "vaha": "20%"},
            {"fond": "Conseq korporátních dluhopisů", "vaha": "30%"},
            {"fond": "BNP Paribas Global Absolute Return Bond", "vaha": "20%"},
            {"fond": "Future X1", "vaha": "15%"},
            {"fond": "Conseq realitní", "vaha": "15%"}
        ]
    },
    "4 až 6 let": {
        "Opatrný": [
            {"fond": "BNP Paribas Global Absolute Return Bond", "vaha": "30%"},
            {"fond": "Conseq korporátních dluhopisů", "vaha": "35%"},
            {"fond": "Future X1", "vaha": "17.5%"},
            {"fond": "Conseq realitní", "vaha": "17.5%"}
        ],
        "Vyvážený": [
            {"fond": "Conseq korporátních dluhopisů", "vaha": "30%"},
            {"fond": "Conseq vys. úročených dluhopisů", "vaha": "20%"},
            {"fond": "Future X1", "vaha": "17.5%"},
            {"fond": "Conseq realitní", "vaha": "17.5%"},
            {"fond": "Amundi Pioneer Global Equity", "vaha": "15%"}
        ],
        "Dynamický": [
            {"fond": "J&T BOND", "vaha": "10%"},
            {"fond": "Conseq vys. úročených dluhopisů", "vaha": "25%"},
            {"fond": "Future X1", "vaha": "17.5%"},
            {"fond": "Conseq realitní", "vaha": "17.5%"},
            {"fond": "Amundi Pioneer Global Equity", "vaha": "15%"},
            {"fond": "FF - Global Dividend Fund", "vaha": "15%"}
        ]
    },
    "7 a více let": {
        "Opatrný": [
            {"fond": "J&T BOND", "vaha": "10%"},
            {"fond": "Conseq vys. úročených dluhopisů", "vaha": "10%"},
            {"fond": "Future X1", "vaha": "20%"},
            {"fond": "Conseq realitní", "vaha": "20%"},
            {"fond": "Amundi Pioneer Global Equity", "vaha": "20%"},
            {"fond": "FF - Global Dividend Fund", "vaha": "20%"}
        ],
        "Vyvážený": [
            {"fond": "Future X1", "vaha": "20%"},
            {"fond": "Conseq realitní", "vaha": "20%"},
            {"fond": "Amundi Pioneer Global Equity", "vaha": "30%"},
            {"fond": "FF - World Fund", "vaha": "30%"}
        ],
        "Dynamický": [
            {"fond": "Future X1", "vaha": "10%"},
            {"fond": "Conseq realitní", "vaha": "10%"},
            {"fond": "Amundi Pioneer Global Equity", "vaha": "20%"},
            {"fond": "FF - World Fund", "vaha": "20%"},
            {"fond": "BNP Paribas Disruptive Technology", "vaha": "10%"},
            {"fond": "BNP US Value Multi-Factor Equity", "vaha": "10%"},
            {"fond": "Conseq Invest Akcie Nové Evropy A", "vaha": "10%"}
        ]
    }
}

def analyzuj_text_a_doporuc(text):
    text_lower = text.lower()
    if "dynamick" in text_lower or "vysok" in text_lower or "akcie" in text_lower or "mlad" in text_lower:
        profil = "Dynamický"
    elif "opatr" in text_lower or "konzervat" in text_lower or "nízk" in text_lower or "strach" in text_lower or "bezpeč" in text_lower:
        profil = "Opatrný"
    else:
        profil = "Vyvážený"
        
    horizont = "7 a více let"
    cisla_v_textu = re.findall(r'(\d+)\s*(let|rok|roky)', text_lower)
    if cisla_v_textu:
        pocet_let = int(cisla_v_textu[0][0])
        if pocet_let <= 3:
            horizont = "do 3 let"
        elif 4 <= pocet_let <= 6:
            horizont = "4 až 6 let"
        else:
            horizont = "7 a více let"
    elif "krátkodob" in text_lower:
        horizont = "do 3 let"
    elif "střednědob" in text_lower:
        horizont = "4 až 6 let"
        
    return profil, horizont

def generuj_pdf(jmeno_poradce, text_situace, profil, horizont, portfolio_data):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('DocTitle', fontSize=22, leading=26, textColor=colors.HexColor("#1A365D"), spaceAfter=15)
    h2_style = ParagraphStyle('SectionHeader', fontSize=14, leading=18, textColor=colors.HexColor("#2C5282"), spaceBefore=15, spaceAfter=10)
    body_style = ParagraphStyle('BodyTextCustom', fontSize=10, leading=14, textColor=colors.HexColor("#2D3748"), spaceAfter=8)

    story.append(Paragraph("NAVRH INVESTICNIHO RESENI (Platforma CONSEQ)", title_style))
    story.append(Paragraph(f"<b>Zpracoval poradce:</b> {jmeno_poradce}", body_style))
    story.append(Spacer(1, 15))
    story.append(Paragraph("Analyza situace klienta", h2_style))
    story.append(Paragraph(text_situace, body_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph(f"Doporucene reseni", h2_style))
    story.append(Paragraph(f"Investicni horizont: <b>{horizont}</b> | Typ investora: <b>{profil}</b>.", body_style))
    story.append(Spacer(1, 10))
    
    data = [["Nazev fondu", "Doporucena vaha"]]
    for radek in portfolio_data:
        data.append([radek["fond"], radek["vaha"]])
        
    t = Table(data, colWidths=[350, 100])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1A365D")),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor("#F7FAFC")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#E2E8F0")),
    ]))
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

st.title("💼 Investiční Asistent pro Finanční Poradce")
st.markdown("Aplikace doporučuje portfolia Conseq na základě **profilu rizika a délky horizontu**.")

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Vstupní parametry")
    jmeno_poradce = st.text_input("Jméno poradce", value="Jan Novák")
    situace_klienta = st.text_area(
        "Zadání situace klienta (volný text)",
        height=250,
        placeholder="Např.: Klientovi je 35 let, peníze bude potřebovat za 5 let. Má opatrný přístup a bojí se ztrát.",
        value="Klient má peníze na účtu a chce je ochránit před inflací. Bojí se ztráty a peníze bude možná potřebovat už za 2 roky."
    )
    tlacitko_analyzovat = st.button("📊 Vyhodnotit a doporučit řešení", type="primary")

with col2:
    st.subheader("2. Výsledek analýzy a návrh")
    if tlacitko_analyzovat or situace_klienta:
        if not situace_klienta.strip():
            st.error("Prosím, popište situaci klienta.")
        else:
            doporuceny_profil, doporuceny_horizont = analyzuj_text_a_doporuc(situace_klienta)
            st.success(f"**Investiční horizont:** {doporuceny_horizont} | **Profil:** {doporuceny_profil}")
            fondy = MODEL_PORTFOLIA[doporuceny_horizont][doporuceny_profil]
            st.write("### 🏢 Navrhované portfolio (Conseq)")
            st.table(fondy)
            pdf_data = generuj_pdf(jmeno_poradce, situace_klienta, doporuceny_profil, doporuceny_horizont, fondy)
            st.download_button(
                label=f"📥 Stáhnout PDF návrh",
                data=pdf_data,
                file_name=f"navrh_conseq.pdf",
                mime="application/pdf"
            )
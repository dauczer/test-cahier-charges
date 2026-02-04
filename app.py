import streamlit as st
from jinja2 import Template
from weasyprint import HTML
import pandas as pd
from datetime import datetime
import io

# Configuration de la page
st.set_page_config(
    page_title="Générateur de Cahier des Charges",
    page_icon="📋",
    layout="wide"
)

# Configuration des use cases
USECASES = {
    "UC001": {
        "title": "Import des données clients",
        "description": """Lorem ipsum dolor sit amet, consectetur adipiscing elit. 
        Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. 
        Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi 
        ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit 
        in voluptate velit esse cillum dolore eu fugiat nulla pariatur.""",
        "columns": [
            {"name": "client_id", "type": "Integer", "mandatory": "Oui", "description": "Identifiant unique du client"},
            {"name": "nom", "type": "String(100)", "mandatory": "Oui", "description": "Nom complet du client"},
            {"name": "email", "type": "String(255)", "mandatory": "Oui", "description": "Adresse email valide"},
            {"name": "telephone", "type": "String(20)", "mandatory": "Non", "description": "Numéro de téléphone"},
            {"name": "date_creation", "type": "Date", "mandatory": "Oui", "description": "Date de création du compte"}
        ],
        "template_file": "template_clients.xlsx"
    },
    "UC002": {
        "title": "Export des commandes",
        "description": """Excepteur sint occaecat cupidatat non proident, sunt in culpa 
        qui officia deserunt mollit anim id est laborum. Sed ut perspiciatis unde omnis 
        iste natus error sit voluptatem accusantium doloremque laudantium, totam rem aperiam, 
        eaque ipsa quae ab illo inventore veritatis et quasi architecto beatae vitae dicta sunt explicabo.""",
        "columns": [
            {"name": "commande_id", "type": "Integer", "mandatory": "Oui", "description": "Identifiant unique de la commande"},
            {"name": "client_id", "type": "Integer", "mandatory": "Oui", "description": "Identifiant du client"},
            {"name": "montant_total", "type": "Decimal(10,2)", "mandatory": "Oui", "description": "Montant total TTC"},
            {"name": "statut", "type": "String(50)", "mandatory": "Oui", "description": "Statut de la commande"},
            {"name": "date_commande", "type": "DateTime", "mandatory": "Oui", "description": "Date et heure de la commande"}
        ],
        "template_file": "template_commandes.xlsx"
    },
    "UC003": {
        "title": "Synchronisation des produits",
        "description": """Nemo enim ipsam voluptatem quia voluptas sit aspernatur aut odit 
        aut fugit, sed quia consequuntur magni dolores eos qui ratione voluptatem sequi nesciunt. 
        Neque porro quisquam est, qui dolorem ipsum quia dolor sit amet, consectetur, adipisci velit, 
        sed quia non numquam eius modi tempora incidunt ut labore et dolore magnam aliquam quaerat voluptatem.""",
        "columns": [
            {"name": "produit_id", "type": "Integer", "mandatory": "Oui", "description": "Identifiant unique du produit"},
            {"name": "sku", "type": "String(50)", "mandatory": "Oui", "description": "Code produit (Stock Keeping Unit)"},
            {"name": "libelle", "type": "String(200)", "mandatory": "Oui", "description": "Nom commercial du produit"},
            {"name": "prix_ht", "type": "Decimal(10,2)", "mandatory": "Oui", "description": "Prix hors taxes"},
            {"name": "stock", "type": "Integer", "mandatory": "Non", "description": "Quantité disponible en stock"},
            {"name": "categorie", "type": "String(100)", "mandatory": "Non", "description": "Catégorie du produit"}
        ],
        "template_file": "template_produits.xlsx"
    },
    "UC004": {
        "title": "Import des transactions financières",
        "description": """At vero eos et accusamus et iusto odio dignissimos ducimus qui 
        blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas molestias 
        excepturi sint occaecati cupiditate non provident, similique sunt in culpa qui officia 
        deserunt mollitia animi, id est laborum et dolorum fuga.""",
        "columns": [
            {"name": "transaction_id", "type": "String(50)", "mandatory": "Oui", "description": "Identifiant unique de la transaction"},
            {"name": "montant", "type": "Decimal(15,2)", "mandatory": "Oui", "description": "Montant de la transaction"},
            {"name": "devise", "type": "String(3)", "mandatory": "Oui", "description": "Code devise ISO 4217 (EUR, USD, etc.)"},
            {"name": "type_transaction", "type": "String(20)", "mandatory": "Oui", "description": "Type de transaction (DEBIT, CREDIT)"},
            {"name": "date_valeur", "type": "Date", "mandatory": "Oui", "description": "Date de valeur de la transaction"}
        ],
        "template_file": "template_transactions.xlsx"
    },
    "UC005": {
        "title": "Export des rapports analytiques",
        "description": """Et harum quidem rerum facilis est et expedita distinctio. 
        Nam libero tempore, cum soluta nobis est eligendi optio cumque nihil impedit quo minus 
        id quod maxime placeat facere possimus, omnis voluptas assumenda est, omnis dolor repellendus. 
        Temporibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet.""",
        "columns": [
            {"name": "rapport_id", "type": "Integer", "mandatory": "Oui", "description": "Identifiant unique du rapport"},
            {"name": "periode", "type": "String(20)", "mandatory": "Oui", "description": "Période concernée (ex: 2024-Q1)"},
            {"name": "indicateur", "type": "String(100)", "mandatory": "Oui", "description": "Nom de l'indicateur mesuré"},
            {"name": "valeur", "type": "Decimal(12,2)", "mandatory": "Oui", "description": "Valeur numérique de l'indicateur"},
            {"name": "unite", "type": "String(20)", "mandatory": "Non", "description": "Unité de mesure (€, %, kg, etc.)"},
            {"name": "commentaire", "type": "Text", "mandatory": "Non", "description": "Observations et remarques"}
        ],
        "template_file": "template_rapports.xlsx"
    }
}

# Template HTML/CSS
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @page {
            size: A4;
            margin: 2.5cm 2cm;
            @top-center {
                content: "Cahier des Charges - Échanges de Fichiers";
                font-size: 10pt;
                color: #666;
                font-family: 'Arial', sans-serif;
            }
            @bottom-right {
                content: "Page " counter(page) " / " counter(pages);
                font-size: 9pt;
                color: #666;
            }
        }
        
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }
        
        h1 {
            color: #2c3e50;
            font-size: 28pt;
            margin-bottom: 10px;
            border-bottom: 4px solid #3498db;
            padding-bottom: 10px;
        }
        
        h2 {
            color: #2c3e50;
            font-size: 20pt;
            margin-top: 40px;
            margin-bottom: 15px;
            page-break-after: avoid;
        }
        
        h3 {
            color: #34495e;
            font-size: 14pt;
            margin-top: 25px;
            margin-bottom: 10px;
            page-break-after: avoid;
        }
        
        .usecase {
            page-break-before: always;
            margin-bottom: 30px;
        }
        
        .usecase:first-of-type {
            page-break-before: avoid;
        }
        
        .description {
            background-color: #f8f9fa;
            padding: 15px;
            border-left: 4px solid #3498db;
            margin: 20px 0;
            text-align: justify;
        }
        
        table {
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            page-break-inside: avoid;
            font-size: 10pt;
        }
        
        th {
            background-color: #3498db;
            color: white;
            padding: 12px 8px;
            text-align: left;
            font-weight: 600;
        }
        
        td {
            padding: 10px 8px;
            border-bottom: 1px solid #ddd;
        }
        
        tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        
        .mandatory-yes {
            color: #e74c3c;
            font-weight: 600;
        }
        
        .mandatory-no {
            color: #95a5a6;
        }
        
        .download-box {
            background-color: #ecf0f1;
            border: 2px dashed #3498db;
            padding: 15px;
            margin: 20px 0;
            text-align: center;
            border-radius: 5px;
        }
        
        .template-info {
            color: #34495e;
            font-size: 11pt;
            font-weight: 600;
        }
        
        .cover-page {
            text-align: center;
            padding-top: 200px;
            page-break-after: always;
        }
        
        .cover-title {
            font-size: 36pt;
            color: #2c3e50;
            margin-bottom: 20px;
        }
        
        .cover-subtitle {
            font-size: 18pt;
            color: #7f8c8d;
            margin-bottom: 50px;
        }
        
        .metadata {
            margin-top: 100px;
            font-size: 11pt;
            color: #7f8c8d;
        }
    </style>
</head>
<body>
    <div class="cover-page">
        <h1 class="cover-title">Cahier des Charges</h1>
        <p class="cover-subtitle">Spécifications des Échanges de Fichiers</p>
        <div class="metadata">
            <p>Date de génération : {{ date }}</p>
            <p>Nombre de use cases : {{ usecases|length }}</p>
        </div>
    </div>

    {% for uc_id, uc in usecases.items() %}
    <div class="usecase">
        <h2>{{ loop.index }}. {{ uc.title }}</h2>
        <p><strong>Référence :</strong> {{ uc_id }}</p>
        
        <h3>Description</h3>
        <div class="description">
            {{ uc.description }}
        </div>
        
        <h3>Format attendu</h3>
        <table>
            <thead>
                <tr>
                    <th style="width: 20%">Nom du champ</th>
                    <th style="width: 15%">Type</th>
                    <th style="width: 12%">Obligatoire</th>
                    <th style="width: 53%">Description</th>
                </tr>
            </thead>
            <tbody>
                {% for col in uc.columns %}
                <tr>
                    <td><strong>{{ col.name }}</strong></td>
                    <td><code>{{ col.type }}</code></td>
                    <td class="{% if col.mandatory == 'Oui' %}mandatory-yes{% else %}mandatory-no{% endif %}">
                        {{ col.mandatory }}
                    </td>
                    <td>{{ col.description }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <div class="download-box">
            <p class="template-info">📥 Template Excel : {{ uc.template_file }}</p>
            <p style="font-size: 9pt; color: #7f8c8d; margin-top: 10px;">
                Les templates Excel sont générés automatiquement avec les colonnes du tableau ci-dessus.<br>
                Téléchargez-les depuis l'interface de génération.
            </p>
        </div>
    </div>
    {% endfor %}
</body>
</html>
"""

def generate_excel_template(uc_data):
    """Génère un fichier Excel template à partir des colonnes d'un use case"""
    columns = [col['name'] for col in uc_data['columns']]
    
    # Créer un DataFrame vide avec les colonnes
    df = pd.DataFrame(columns=columns)
    
    # Créer un fichier Excel en mémoire
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Template')
        
        # Accéder au workbook et à la feuille pour formatter
        workbook = writer.book
        worksheet = writer.sheets['Template']
        
        # Formatter les en-têtes (en gras, fond bleu)
        from openpyxl.styles import Font, PatternFill, Alignment
        
        header_fill = PatternFill(start_color="3498DB", end_color="3498DB", fill_type="solid")
        header_font = Font(bold=True, color="FFFFFF")
        
        for cell in worksheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')
        
        # Ajuster la largeur des colonnes
        for column in worksheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(cell.value)
                except:
                    pass
            adjusted_width = min(max_length + 2, 50)
            worksheet.column_dimensions[column_letter].width = adjusted_width
    
    output.seek(0)
    return output

def generate_pdf(selected_usecases):
    """Génère le PDF du cahier des charges"""
    template_data = {
        'usecases': selected_usecases,
        'date': datetime.now().strftime('%d/%m/%Y')
    }
    
    template = Template(HTML_TEMPLATE)
    html_content = template.render(**template_data)
    
    pdf_bytes = HTML(string=html_content).write_pdf()
    return pdf_bytes

# Interface Streamlit
st.title("📋 Générateur de Cahier des Charges")
st.markdown("### Spécifications des Échanges de Fichiers")

st.markdown("---")

st.markdown("#### 🔍 Sélectionnez les use cases à inclure")

# Créer les checkboxes en 2 colonnes
col1, col2 = st.columns(2)

selected_usecases = {}

for idx, (uc_id, uc_data) in enumerate(USECASES.items()):
    with col1 if idx % 2 == 0 else col2:
        if st.checkbox(f"**{uc_id}** : {uc_data['title']}", key=uc_id):
            selected_usecases[uc_id] = uc_data

st.markdown("---")

# Zone de génération
if len(selected_usecases) > 0:
    st.success(f"✅ {len(selected_usecases)} use case(s) sélectionné(s)")
    
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 2])
    
    with col_btn1:
        if st.button("🚀 Générer le PDF", type="primary", use_container_width=True):
            with st.spinner("Génération du PDF en cours..."):
                pdf_bytes = generate_pdf(selected_usecases)
                
                st.download_button(
                    label="📥 Télécharger le PDF",
                    data=pdf_bytes,
                    file_name=f"cahier_des_charges_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
    
    st.markdown("#### 📊 Templates Excel")
    st.info("💡 Les templates Excel sont générés automatiquement avec les colonnes définies dans chaque use case.")
    
    # Générer les templates Excel
    excel_cols = st.columns(min(len(selected_usecases), 3))
    
    for idx, (uc_id, uc_data) in enumerate(selected_usecases.items()):
        with excel_cols[idx % 3]:
            excel_buffer = generate_excel_template(uc_data)
            
            st.download_button(
                label=f"📥 {uc_data['template_file']}",
                data=excel_buffer,
                file_name=uc_data['template_file'],
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key=f"excel_{uc_id}",
                use_container_width=True
            )
            st.caption(f"{uc_id}: {uc_data['title']}")

else:
    st.warning("⚠️ Veuillez sélectionner au moins un use case pour commencer")

st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #7f8c8d; font-size: 0.9em;'>
    Générateur de Cahier des Charges - Version 1.0<br>
    Génère automatiquement des PDFs professionnels et des templates Excel
    </div>
    """,
    unsafe_allow_html=True
)
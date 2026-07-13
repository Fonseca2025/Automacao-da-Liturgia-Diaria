import requests
from bs4 import BeautifulSoup
import os
from datetime import datetime
import pytz

def get_liturgia():
    # Define o fuso horário de Brasília para garantir a data correta
    timezone = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(timezone).strftime('%d-%m-%Y')
    
    # URL dos Dehonianos (muito estável)
    url = "https://dehonianos.org.br/liturgia/"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            return f"❌ Erro ao acessar site: Status {response.status_code}"

        soup = BeautifulSoup(response.text, 'html.parser')

        # No site dos Dehonianos, o conteúdo fica dentro da classe 'entry-content'
        corpo = soup.find("div", class_="entry-content")
        
        if not corpo:
            return "⚠️ Não foi possível encontrar o conteúdo da liturgia."

        # Montagem do texto em HTML
        texto_final = f"<b>📖 LITURGIA DIÁRIA ({hoje})</b>\n"
        texto_final += "━━━━━━━━━━━━━━━━━━\n\n"

        # Extraindo títulos e parágrafos
        # Eles usam <h4> ou <strong> para os títulos das leituras
        for elemento in corpo.find_all(['h4', 'p', 'strong']):
            txt = elemento.get_text(strip=True)
            
            if not txt or len(txt) < 2:
                continue
                
            # Identifica títulos (Leitura, Salmo, Evangelho)
            if elemento.name == 'h4' or "LEITURA" in txt.upper() or "EVANGELHO" in txt.upper() or "SALMO" in txt.upper():
                texto_final += f"\n<pre>📑 {txt.upper()}</pre>\n"
            else:
                # Se for a citação bíblica (ex: Jo 3, 16)
                if any(livro in txt for livro in ["Mt ", "Mc ", "Lc ", "Jo ", "At ", "Sl "]):
                    texto_final += f"<i>📍 {txt}</i>\n\n"
                else:
                    texto_final += f"{txt}\n\n"

        if len(texto_final) < 300:
             return "⚠️ O conteúdo parece incompleto. Tente o link oficial: " + url

        return texto_final

    except Exception as e:
        return f"❌ Erro crítico: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # O Telegram aceita 4096 caracteres. Se passar, dividimos.
    if len(text) > 4000:
        partes = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for parte in partes:
            requests.post(url, data={"chat_id": chat_id, "text": parte, "parse_mode": "HTML"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    resultado = get_liturgia()
    send_telegram(resultado)

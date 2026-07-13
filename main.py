import requests
from bs4 import BeautifulSoup
import os

def get_liturgia_completa():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Tentar pegar a data (Geralmente é o primeiro H2 ou está na classe header-liturgia)
        dia_tag = soup.find("h2")
        dia = dia_tag.get_text(strip=True) if dia_tag else "Liturgia de Hoje"

        # 2. Tentar pegar a cor (Procurar pelo ID específico ou texto que contenha "Cor:")
        cor = "Não informada"
        cor_div = soup.find("div", id="cor-liturgica-dia")
        if cor_div:
            cor = cor_div.get_text(strip=True)
        
        mensagem_final = f"📖 *LITURGIA DIÁRIA*\n📅 *{dia}*\n🎨 *Cor:* {cor}\n"
        mensagem_final += "━━━━━━━━━━━━━━━━━━\n\n"

        # 3. Pegar as leituras
        # No site da CNBB, cada leitura costuma estar dentro de uma div 'col-12' 
        # com um H3 para o título e uma div para o texto.
        leituras_encontradas = False
        
        # Vamos buscar todos os blocos que pareçam uma leitura
        blocos = soup.find_all("div", class_="col-12")
        
        for bloco in blocos:
            titulo_tag = bloco.find("h3")
            if titulo_tag:
                leituras_encontradas = True
                titulo = titulo_tag.get_text(strip=True)
                
                # Referência (ex: "Leitura do Livro de...")
                ref_tag = bloco.find("p", class_="referencia-leitura")
                ref = ref_tag.get_text(strip=True) if ref_tag else ""
                
                # Texto da leitura
                texto_tag = bloco.find("div", class_="texto-leitura")
                if not texto_tag:
                    # Tenta pegar o próximo div se não achar pela classe
                    texto_tag = titulo_tag.find_next_sibling("div")
                
                texto = texto_tag.get_text(separator='\n').strip() if texto_tag else ""
                
                if titulo:
                    mensagem_final += f"📑 *{titulo}*\n"
                if ref:
                    mensagem_final += f"📍 _{ref}_\n\n"
                if texto:
                    mensagem_final += texto + "\n\n"
                    mensagem_final += "━━━━━━━━━━━━━━━━━━\n\n"

        if not leituras_encontradas:
            return "⚠️ O site da CNBB mudou a estrutura. Não foi possível extrair as leituras hoje."

        return mensagem_final

    except Exception as e:
        return f"❌ Erro ao acessar o site: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Credenciais não configuradas.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Quebra o texto se for maior que o limite do Telegram (4096 caracteres)
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            part = text[i:i+4000]
            requests.post(url, data={"chat_id": chat_id, "text": part, "parse_mode": "Markdown"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    conteudo = get_liturgia_completa()
    send_telegram(conteudo)

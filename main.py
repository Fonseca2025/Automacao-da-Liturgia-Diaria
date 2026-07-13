import requests
from bs4 import BeautifulSoup
import os
import sys

def get_liturgia():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8' # Garante a acentuação correta
    soup = BeautifulSoup(response.text, 'html.parser')

    try:
        # Seletores atualizados baseados na estrutura real do site
        dia_elemento = soup.find("h2", class_="header-liturgia")
        dia = dia_elemento.text.strip() if dia_elemento else "Data não encontrada"

        cor_elemento = soup.find("div", id="cor-liturgica-dia")
        cor = cor_elemento.text.strip() if cor_elemento else "Cor não informada"
        
        # Pega as leituras (títulos)
        leituras_tags = soup.find_all("h3", class_="titulo-leitura")
        lista_leituras = [tag.text.strip() for tag in leituras_tags]

        # Monta a mensagem
        texto_final = f"📖 *LITURGIA DIÁRIA*\n"
        texto_final += f"📅 {dia}\n"
        texto_final += f"🎨 *Cor:* {cor}\n\n"
        
        if lista_leituras:
            texto_final += "📑 *Leituras de hoje:*\n"
            for leitura in lista_leituras:
                texto_final += f"• {leitura}\n"
        
        texto_final += f"\n🔗 [Leia a liturgia completa aqui]({url})"
        
        return texto_final

    except Exception as e:
        print(f"Erro ao processar o HTML: {e}")
        return None

def send_telegram(text):
    if not text:
        return

    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: TELEGRAM_TOKEN ou TELEGRAM_CHAT_ID não configurados nas Secrets.")
        sys.exit(1)

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    res = requests.post(url, data=payload)
    if res.status_code != 200:
        print(f"Erro ao enviar para o Telegram: {res.text}")

if __name__ == "__main__":
    mensagem = get_liturgia()
    if mensagem:
        send_telegram(mensagem)
        print("Processo concluído!")
    else:
        print("Não foi possível gerar a mensagem.")

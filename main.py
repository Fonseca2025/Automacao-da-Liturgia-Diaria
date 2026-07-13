import requests
from bs4 import BeautifulSoup
import os

def clean_text(soup_element):
    """Limpa o HTML e retorna apenas o texto formatado."""
    if not soup_element:
        return ""
    # Remove scripts e estilos
    for script in soup_element(["script", "style"]):
        script.decompose()
    return soup_element.get_text(separator='\n').strip()

def get_liturgia_completa():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. Pegar Cabeçalho (Data e Cor)
    dia = soup.find("h2", class_="header-liturgia").get_text(strip=True)
    cor = soup.find("div", id="cor-liturgica-dia").get_text(strip=True)
    
    mensagem_final = f"📖 *LITURGIA DIÁRIA*\n📅 *{dia}*\n🎨 *Cor:* {cor}\n\n"
    mensagem_final += "---" * 5 + "\n\n"

    # 2. Pegar todas as leituras
    # O site da CNBB organiza as leituras dentro de divs com a classe 'content' ou 'leituras'
    # Vamos buscar os blocos de leitura
    leituras = soup.find_all("div", class_="col-12")

    for item in leituras:
        titulo = item.find("h3", class_="titulo-leitura")
        referencia = item.find("p", class_="referencia-leitura")
        texto = item.find("div", class_="texto-leitura")

        if titulo:
            mensagem_final += f"📑 *{titulo.get_text(strip=True)}*\n"
        if referencia:
            mensagem_final += f"📍 _{referencia.get_text(strip=True)}_\n\n"
        if texto:
            mensagem_final += f"{texto.get_text(separator='\n').strip()}\n\n"
            mensagem_final += "---" * 5 + "\n\n"

    return mensagem_final

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Se o texto for muito grande, o Telegram rejeita. 
    # Vamos quebrar em partes de 4000 caracteres se necessário.
    if len(text) > 4096:
        for i in range(0, len(text), 4000):
            part = text[i:i+4000]
            payload = {
                "chat_id": chat_id,
                "text": part,
                "parse_mode": "Markdown"
            }
            requests.post(url, data=payload)
    else:
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "Markdown"
        }
        requests.post(url, data=payload)

if __name__ == "__main__":
    try:
        conteudo = get_liturgia_completa()
        send_telegram(conteudo)
        print("Liturgia completa enviada!")
    except Exception as e:
        print(f"Erro: {e}")

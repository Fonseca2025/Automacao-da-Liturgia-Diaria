import requests
from bs4 import BeautifulSoup
import os

def get_liturgia_completa():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'
    soup = BeautifulSoup(response.text, 'html.parser')

    # 1. Pegar Cabeçalho (Data e Cor)
    dia_tag = soup.find("h2", class_="header-liturgia")
    dia = dia_tag.get_text(strip=True) if dia_tag else "Data não encontrada"
    
    cor_tag = soup.find("div", id="cor-liturgica-dia")
    cor = cor_tag.get_text(strip=True) if cor_tag else "Cor não informada"
    
    mensagem_final = f"📖 *LITURGIA DIÁRIA*\n📅 *{dia}*\n🎨 *Cor:* {cor}\n\n"
    mensagem_final += "━━━━━━━━━━━━━━━━━━\n\n"

    # 2. Pegar todas as seções de leitura
    # O site geralmente divide em blocos. Vamos pegar os títulos e os textos.
    leituras = soup.find_all("div", class_="col-12")

    for item in leituras:
        titulo_tag = item.find("h3", class_="titulo-leitura")
        ref_tag = item.find("p", class_="referencia-leitura")
        texto_tag = item.find("div", class_="texto-leitura")

        if titulo_tag:
            titulo = titulo_tag.get_text(strip=True)
            mensagem_final += f"📑 *{titulo}*\n"
        
        if ref_tag:
            referencia = ref_tag.get_text(strip=True)
            mensagem_final += f"📍 _{referencia}_\n\n"
        
        if texto_tag:
            # Corrigido o erro da f-string separando o processamento do texto
            texto_puro = texto_tag.get_text(separator='\n').strip()
            mensagem_final += texto_puro + "\n\n"
            mensagem_final += "━━━━━━━━━━━━━━━━━━\n\n"

    return mensagem_final

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Token ou Chat ID não encontrados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # O Telegram tem limite de 4096 caracteres. Se passar, vamos dividir.
    if len(text) > 4000:
        partes = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for parte in partes:
            payload = {
                "chat_id": chat_id,
                "text": parte,
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
        print("Sucesso!")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")

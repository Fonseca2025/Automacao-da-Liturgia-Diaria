import requests
from bs4 import BeautifulSoup
import os

def get_liturgia_cnbb():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Pegar a data
        dia_tag = soup.find("h2", class_="header-liturgia")
        dia_info = dia_tag.get_text(strip=True) if dia_tag else "Liturgia Diária"

        # 2. Pegar a cor
        cor_tag = soup.find("div", id="cor-liturgica-dia")
        cor_info = cor_tag.get_text(strip=True) if cor_tag else "Não informada"

        mensagem = f"📖 *LITURGIA DIÁRIA*\n📅 {dia_info}\n🎨 *Cor:* {cor_info}\n"
        mensagem += "━━━━━━━━━━━━━━━━━━\n\n"

        # 3. Pegar as leituras de forma robusta
        leituras = soup.find_all("div", class_="col-12")
        conteudo_detectado = False

        for item in leituras:
            titulo_tag = item.find("h3", class_="titulo-leitura")
            ref_tag = item.find("p", class_="referencia-leitura")
            texto_tag = item.find("div", class_="texto-leitura")

            if titulo_tag:
                conteudo_detectado = True
                titulo = titulo_tag.get_text(strip=True).upper()
                mensagem += f"📑 *{titulo}*\n"
                
                if ref_tag:
                    ref = ref_tag.get_text(strip=True)
                    mensagem += f"📍 _{ref}_\n\n"
                
                if texto_tag:
                    # Correção do erro da barra invertida: processamos o texto fora da f-string
                    texto_puro = texto_tag.get_text(separator='\n').strip()
                    mensagem += texto_puro + "\n\n"
                    mensagem += "──────────────────\n\n"

        if not conteudo_detectado:
            # Fallback caso a estrutura mude muito
            corpo_site = soup.find("div", id="liturgia-diaria")
            if corpo_site:
                texto_fallback = corpo_site.get_text(separator='\n', strip=True)
                return "📖 *LITURGIA (Modo de Segurança)*\n\n" + texto_fallback
            return "⚠️ Não foi possível extrair os textos hoje. Verifique o site: " + url

        return mensagem

    except Exception as e:
        return f"❌ Erro ao acessar o site: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Chaves não configuradas no GitHub Secrets.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Se o texto for muito grande (limite do Telegram é 4096), divide em partes
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            part = text[i:i+4000]
            requests.post(url, data={"chat_id": chat_id, "text": part, "parse_mode": "Markdown"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    resultado = get_liturgia_cnbb()
    send_telegram(resultado)
    print("Processo finalizado.")

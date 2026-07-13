import requests
from bs4 import BeautifulSoup
import os

def get_liturgia_cnbb():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    
    # Headers mais completos para parecer um navegador real
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
        'Referer': 'https://www.google.com/'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Pegar Data (Tentativa mais flexível)
        dia_tag = soup.find("h2", class_="header-liturgia") or soup.find("h2")
        dia = dia_tag.get_text(strip=True) if dia_tag else "Data não encontrada"

        # 2. Pegar Cor
        cor_tag = soup.find("div", id="cor-liturgica-dia")
        cor = cor_tag.get_text(strip=True) if cor_tag else "Cor não informada"

        mensagem = f"📖 *LITURGIA DIÁRIA*\n📅 {dia}\n🎨 *Cor:* {cor}\n"
        mensagem += "━━━━━━━━━━━━━━━━━━\n\n"

        # 3. Pegar Títulos e Textos
        # No site da CNBB, cada leitura está em uma div col-12
        leituras = soup.find_all("div", class_="col-12")
        
        conteudo_detectado = False
        for item in leituras:
            titulo_tag = item.find("h3", class_="titulo-leitura")
            if titulo_tag:
                conteudo_detectado = True
                titulo = titulo_tag.get_text(strip=True)
                
                ref_tag = item.find("p", class_="referencia-leitura")
                ref = ref_tag.get_text(strip=True) if ref_tag else ""
                
                texto_tag = item.find("div", class_="texto-leitura")
                # Pegamos o texto e formatamos as quebras de linha
                texto = texto_tag.get_text(separator='\n').strip() if texto_tag else ""
                
                mensagem += f"📑 *{titulo.upper()}*\n"
                if ref:
                    mensagem += f"📍 _{ref}_\n\n"
                if texto:
                    mensagem += texto + "\n\n"
                
                mensagem += "──────────────────\n\n"

        if not conteudo_detectado:
            mensagem += "⚠️ Não foi possível extrair o texto completo. Acesse o link abaixo.\n"

        mensagem += f"🔗 [Leia no site da CNBB]({url})"
        return mensagem

    except Exception as e:
        return f"❌ Erro ao acessar a CNBB: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Chaves não configuradas.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Se o texto for muito grande (limite 4096), envia em partes
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            part = text[i:i+4000]
            requests.post(url, data={"chat_id": chat_id, "text": part, "parse_mode": "Markdown"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    resultado = get_liturgia_cnbb()
    send_telegram(resultado)

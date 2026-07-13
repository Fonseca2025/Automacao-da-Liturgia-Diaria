import requests
from bs4 import BeautifulSoup
import os

def get_liturgia():
    # Usando o site da Paulus como alternativa robusta
    url = "https://www.paulus.com.br/portal/liturgia-diaria/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Pegar a data/título
        # No site da Paulus, o conteúdo principal fica dentro de uma div com classe 'content'
        container = soup.find("div", class_="texto_liturgia")
        
        if not container:
            # Tenta um seletor alternativo se o principal falhar
            container = soup.find("div", class_="post")

        if not container:
            return "⚠️ Não foi possível localizar o texto da liturgia no site da Paulus."

        # 2. Limpeza e Formatação
        # Vamos extrair os textos de forma organizada
        texto_bruto = ""
        
        # O site da Paulus organiza por títulos e parágrafos
        for elemento in container.find_all(['h1', 'h2', 'h3', 'p', 'strong']):
            txt = elemento.get_text(strip=True)
            if not txt:
                continue
                
            if elemento.name in ['h1', 'h2', 'h3']:
                texto_bruto += f"\n<b>{txt.upper()}</b>\n"
            elif elemento.name == 'strong':
                texto_bruto += f"<b>{txt}</b> "
            else:
                texto_bruto += f"{txt}\n\n"

        if len(texto_bruto) < 100:
            return "⚠️ O conteúdo extraído parece estar incompleto."

        # Cabeçalho decorativo
        mensagem_final = "<b>📖 LITURGIA DIÁRIA</b>\n"
        mensagem_final += "━━━━━━━━━━━━━━━━━━\n"
        mensagem_final += texto_bruto

        return mensagem_final

    except Exception as e:
        return f"❌ Erro ao acessar o site: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Token ou ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Se o texto for muito grande, divide em partes (limite 4096)
    if len(text) > 4000:
        # Divide por parágrafos para não cortar palavras ao meio
        partes = text.split('\n\n')
        mensagem_atual = ""
        for parte in partes:
            if len(mensagem_atual) + len(parte) < 4000:
                mensagem_atual += parte + "\n\n"
            else:
                requests.post(url, data={"chat_id": chat_id, "text": mensagem_atual, "parse_mode": "HTML"})
                mensagem_atual = parte + "\n\n"
        # Envia a última parte
        if mensagem_atual:
            requests.post(url, data={"chat_id": chat_id, "text": mensagem_atual, "parse_mode": "HTML"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "HTML"})

if __name__ == "__main__":
    resultado = get_liturgia()
    send_telegram(resultado)

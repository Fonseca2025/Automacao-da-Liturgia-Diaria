import requests
from bs4 import BeautifulSoup
import os

def get_liturgia():
    # Usando Canção Nova por ser mais estável para robôs
    url = "https://liturgia.cancaonova.com/pb/"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Pegar o título/data
        titulo = soup.find("h1", class_="entry-title")
        dia = titulo.get_text(strip=True) if titulo else "Liturgia de Hoje"

        mensagem = f"📖 *LITURGIA DIÁRIA*\n📅 {dia}\n"
        mensagem += "━━━━━━━━━━━━━━━━━━\n\n"

        # 2. Pegar as leituras
        # Na Canção Nova, as leituras ficam dentro de divs com IDs específicos
        # como 'leitura-1', 'salmo', 'evangelho'
        secoes = soup.find_all("div", class_="content-liturgia")
        
        conteudo_encontrado = False
        for secao in secoes:
            conteudo_encontrado = True
            
            # Título da parte (ex: 1ª Leitura)
            h3 = secao.find("h3")
            if h3:
                mensagem += f"📑 *{h3.get_text(strip=True).upper()}*\n"
            
            # Referência (ex: Ap 1,1-4; 2,1-5)
            ref = secao.find("span", class_="referencia-leitura")
            if ref:
                mensagem += f"📍 _{ref.get_text(strip=True)}_\n\n"
            
            # Texto da leitura
            # Removemos scripts e propagandas que podem estar no meio
            for extra in secao.find_all(["script", "style", "ins"]):
                extra.decompose()
                
            texto = secao.get_text(separator='\n').strip()
            # Limpeza simples para não repetir o título no corpo do texto
            if h3 and h3.get_text(strip=True) in texto:
                texto = texto.replace(h3.get_text(strip=True), "", 1).strip()
            if ref and ref.get_text(strip=True) in texto:
                texto = texto.replace(ref.get_text(strip=True), "", 1).strip()
                
            mensagem += texto + "\n\n"
            mensagem += "──────────────────\n\n"

        if not conteudo_encontrado:
            return "⚠️ Não consegui extrair os textos. O formato do site pode ter mudado."

        return mensagem

    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Token ou Chat ID não configurados.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Quebra o texto se passar de 4000 caracteres
    if len(text) > 4000:
        partes = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for parte in partes:
            requests.post(url, data={"chat_id": chat_id, "text": parte, "parse_mode": "Markdown"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    resultado = get_liturgia()
    send_telegram(resultado)

import requests
from bs4 import BeautifulSoup
import os

def get_liturgia():
    # Site alternativo muito mais estável para automações
    url = "https://www.catolico.org.br/liturgia_diaria.php"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.encoding = 'iso-8859-1' # Site antigo costuma usar esse encoding
        
        if response.status_code != 200:
            return f"❌ Erro ao acessar site (Status {response.status_code})"

        soup = BeautifulSoup(response.text, 'html.parser')

        # No catolico.org.br, o texto principal fica dentro de divs ou tabelas simples
        # Vamos buscar o conteúdo principal
        corpo = soup.find("div", class_="conteudo_interna")
        
        if not corpo:
            # Segunda tentativa: busca por tags de texto direto
            corpo = soup.find("td", class_="texto")

        if not corpo:
            return "⚠️ Estrutura do site não reconhecida. Tente novamente mais tarde."

        # Limpeza de tags desnecessárias (scripts, estilos, links de propaganda)
        for tag in corpo(["script", "style", "a", "ins"]):
            tag.decompose()

        # Montagem do texto
        texto_final = "<b>📖 LITURGIA DIÁRIA</b>\n"
        texto_final += "━━━━━━━━━━━━━━━━━━\n\n"

        # Pegamos os parágrafos e títulos
        elementos = corpo.find_all(['h2', 'h3', 'p', 'strong', 'b'])
        
        for el in elementos:
            txt = el.get_text(strip=True)
            if not txt or len(txt) < 3:
                continue
            
            # Se for um título (Leitura, Salmo, Evangelho)
            if el.name in ['h2', 'h3'] or "Leitura" in txt or "Evangelho" in txt or "Salmo" in txt:
                texto_final += f"\n<b>{txt.upper()}</b>\n"
            else:
                texto_final += f"{txt}\n\n"

        if len(texto_final) < 200:
            return "⚠️ O texto extraído ficou muito curto. O site pode ter mudado."

        return texto_final

    except Exception as e:
        return f"❌ Erro crítico: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Token ou ID não configurados nas Secrets.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Dividir se o texto for muito longo (Telegram aceita 4096 caracteres)
    if len(text) > 4000:
        partes = [text[i:i+4000] for i in range(0, len(text), 4000)]
        for parte in partes:
            data = {"chat_id": chat_id, "text": parte, "parse_mode": "HTML"}
            requests.post(url, data=data)
    else:
        data = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}
        requests.post(url, data=data)

if __name__ == "__main__":
    resultado = get_liturgia()
    send_telegram(resultado)
    print("Execução finalizada.")

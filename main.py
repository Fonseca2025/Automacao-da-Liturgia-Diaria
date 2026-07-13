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

        # 1. Tentar pegar a data e título do dia
        # O site costuma usar H2 para a data e H1 ou títulos fortes para o tempo litúrgico
        header = soup.find("div", class_="header-liturgia")
        if header:
            dia_info = header.get_text(separator=" - ", strip=True)
        else:
            # Caso mude a classe, pegamos o primeiro título grande que aparecer
            dia_info = soup.find("h2").text.strip() if soup.find("h2") else "Liturgia Diária"

        cor = "Não identificada"
        cor_div = soup.find("div", id="cor-liturgica-dia")
        if cor_div:
            cor = cor_div.text.strip()

        mensagem = f"📖 *LITURGIA DIÁRIA*\n📅 {dia_info}\n🎨 *Cor:* {cor}\n"
        mensagem += "━━━━━━━━━━━━━━━━━━\n\n"

        # 2. Captura Flexível de Leituras
        # Vamos buscar todos os blocos de conteúdo e filtrar o que é relevante
        # O site novo usa muito a classe 'col-12' ou tags de parágrafo direto
        corpo = soup.find_all(['h3', 'p', 'div'], class_=['titulo-leitura', 'referencia-leitura', 'texto-leitura', 'col-12'])
        
        conteudo_detectado = False
        for item in corpo:
            texto = item.get_text(strip=True)
            
            # Se for um título (Primeira Leitura, Salmo, Evangelho)
            if item.name == 'h3' or 'titulo-leitura' in item.get('class', []):
                mensagem += f"\n📑 *{texto.upper()}*\n"
                conteudo_detectado = True
            
            # Se for a referência bíblica (itálico)
            elif 'referencia-leitura' in item.get('class', []):
                mensagem += f"📍 _{texto}_\n\n"
            
            # Se for o texto da leitura em si
            elif 'texto-leitura' in item.get('class', []):
                # Limpa espaços extras e adiciona o texto
                txt_limpo = item.get_text(separator='\n').strip()
                mensagem += f"{txt_limpo}\n\n"
                mensagem += "──────────────────\n"

        if not conteudo_detectado:
            # Fallback: Se os seletores falharem, pegamos o texto bruto da div principal
            main_content = soup.find("div", id="liturgia-diaria")
            if main_content:
                return f"📖 *LITURGIA (Modo Simples)*\n\n{main_content.get_text(separator='\n', strip=True)}"
            return "⚠️ Não consegui extrair os textos. O site pode estar em manutenção ou mudou o formato."

        return mensagem

    except Exception as e:
        return f"❌ Erro de conexão: {str(e)}"

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    # Telegram suporta até 4096 caracteres
    if len(text) > 4000:
        for i in range(0, len(text), 4000):
            part = text[i:i+4000]
            requests.post(url, data={"chat_id": chat_id, "text": part, "parse_mode": "Markdown"})
    else:
        requests.post(url, data={"chat_id": chat_id, "text": text, "parse_mode": "Markdown"})

if __name__ == "__main__":
    resultado = get_liturgia_cnbb()
    send_telegram(resultado)

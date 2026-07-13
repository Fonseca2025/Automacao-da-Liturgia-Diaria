import requests
import os

def get_liturgia_link():
    url = "https://liturgiadiaria.edicoescnbb.com.br/"
    
    # Montagem direta do texto conforme solicitado
    mensagem = "📖 *LITURGIA DIÁRIA*\n\n\n"
    mensagem += f"🔗 [Leia a liturgia completa aqui]({url})"
    
    return mensagem

def send_telegram(text):
    token = os.environ.get('TELEGRAM_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Erro: Verifique as Secrets TELEGRAM_TOKEN e TELEGRAM_CHAT_ID no GitHub.")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "disable_web_page_preview": False
    }
    
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
        print("Mensagem enviada com sucesso!")
    except Exception as e:
        print(f"Erro ao enviar mensagem: {e}")

if __name__ == "__main__":
    conteudo = get_liturgia_link()
    send_telegram(conteudo)

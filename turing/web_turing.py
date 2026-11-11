#!/usr/bin/env python3
"""
servidor local para execução da interface gráfica retro-futurista
inicia um servidor web local e abre a interface no navegador padrão
inclui endpoint /save-jff para salvar os arquivos gerados dinamicamente na pasta jflap/
"""

import http.server
import socketserver
import webbrowser
import os
import sys
import json

# porta padrão utilizada pelo servidor local
PORT = 8085
# diretório base onde se localiza o script e os arquivos do projeto
DIRECTORY = os.path.dirname(os.path.abspath(__file__))
JFLAP_DIR = os.path.join(DIRECTORY, "jflap")

os.makedirs(JFLAP_DIR, exist_ok=True)

class TuringServerHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def do_POST(self):
        # endpoint para salvar arquivo jff diretamente na pasta jflap/
        if self.path == "/save-jff":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)
            try:
                data = json.loads(body.decode("utf-8"))
                filename = data.get("filename")
                content = data.get("content")

                if not filename or not content:
                    self.send_error(400, "dados incompletos")
                    return

                # segurança: impede fuga de diretório
                safe_filename = os.path.basename(filename)
                target_path = os.path.join(JFLAP_DIR, safe_filename)

                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(content)

                print(f"[jflap] arquivo salvo: {target_path}")

                response = json.dumps({"ok": True, "path": target_path}).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(response)))
                self.end_headers()
                self.wfile.write(response)
            except Exception as e:
                self.send_error(500, f"erro ao salvar jff: {e}")
        else:
            self.send_error(404, "endpoint desconhecido")

def run():
    # muda para o diretório dos arquivos visuais e inicia o serviço
    os.chdir(DIRECTORY)
    with socketserver.TCPServer(("", PORT), TuringServerHandler) as httpd:
        url = f"http://localhost:{PORT}/index.html"
        print("=" * 65)
        print(" maquina de turing tradutora - interface visual iniciada")
        print("=" * 65)
        print(f" acesse no navegador: {url}")
        print(" pressione ctrl+c no terminal para encerrar o servidor.")
        print("=" * 65)
        try:
            webbrowser.open(url)
        except Exception:
            pass
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nservidor encerrado.")

if __name__ == "__main__":
    run()

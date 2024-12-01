from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from database import MyDatabase
import json
import cgi

class MyDomainServer(BaseHTTPRequestHandler):
    def do_GET(self):
        # Define a rota com base no valor de self.path
        if self.path == "/list":
            self.list_domains()
        else:
            self.handle_404()

    def do_POST(self):
        # Define a rota com base no valor de self.path
        if self.path == "/select-domain":
            self.select_domain()
        elif self.path == "/upload-files":
            self.upload_files()
        else:
            self.handle_404()

    def list_domains(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        domains = MyDatabase.list_domains_json()

        # Convertendo os dados para JSON e enviando
        self.wfile.write(json.dumps(domains).encode('utf-8'))

    def upload_files(self):
        pass
    
    def select_domain(self):
        from utils import parse_multipart_data

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        
        if(body == b'' or len(body) == 0):
            status_code = 404
            header = ('Content-Type', 'application/json')
            response = f"{{'status': 'error', 'message': 'Não encontrado campos domain_name e username', 'status_code': 409}}"
            self.send_response(status_code)
            self.send_header(header[0], header[1])
            self.end_headers()
            self.wfile.write(response.encode('utf-8'))

        # Processar o corpo para obter os campos
        fields = parse_multipart_data(body)

        domain_name = fields.get("domain_name", None) 
        username = fields.get("username", None)

        if(not domain_name):
            status_code = 404
            header = ('Content-Type', 'application/json')
            response = f"{{'status': 'error', 'message': 'Não encontrado campo domain_name', 'status_code': 409}}"
        elif(not username):
            status_code = 404
            header = ('Content-Type', 'application/json')
            response = f"{{'status': 'error', 'message': 'Não encontrado campo username', 'status_code': 409}}"
        else:
            dict_response = MyDatabase.select_domain(domain_name, username)
            if(not dict_response['status'] == 'error'):
                status_code = dict_response['status_code']
                header = ('Content-Type', 'application/json')
                response = f"{dict_response}"
            else:
                status_code = dict_response['status_code']
                header = ('Content-Type', 'application/json')
                response = f"{dict_response}"
       
        # Enviar a resposta
        self.send_response(status_code)
        self.send_header(header[0], header[1])
        self.end_headers()
        
        self.wfile.write(response.encode('utf-8'))

    def handle_404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        response = "<html><body><h1>404 Not Found</h1><p>The requested page was not found.</p></body></html>"
        self.wfile.write(response.encode('utf-8'))

# Define o endereço e porta do servidor
server_address = ('', 8000)

# Conecta banco de dados SQLITE
MyDatabase.connect_db()

# Cria e inicia o servidor
httpd = HTTPServer(server_address, MyDomainServer)
print("Server running on port 8000...")
httpd.serve_forever()

from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from database import MyDatabase
import json
import cgi

class MyDomainServer(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/list":
            self.list_domains()
        elif self.path.endswith('.webserver'):
            domain = self.path.rsplit('/', 1)[-1][:-len('.webserver')]
            self.get_domain_access(domain)
        elif self.path.startswith('/temp/'): 
            self.serve_temp_file(self.path[6:]) 
        else:
            self.handle_404()
    
    def do_POST(self):
        if self.path == "/select-domain":
            self.select_domain()
        elif self.path == "/upload-files":
            self.upload_files()
        else:
            self.handle_404()

    def get_domain_access(self, domain):
        response = MyDatabase.check_domain_exists(domain)

        if response["status_code"] == 200:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(response["html_content"].encode("utf-8"))
        else:
            self.send_response(response["status_code"])
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(response["message"].encode("utf-8"))

    def serve_temp_file(self, filename):
        content, mime_type = MyDatabase.get_temp_file(filename)
        if content:
            self.send_response(200)
            self.send_header("Content-type", mime_type)
            self.end_headers()
            self.wfile.write(content)
        else:
            self.handle_404()

    def list_domains(self):
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        domains = MyDatabase.list_domains_json()

        self.wfile.write(json.dumps(domains).encode('utf-8'))

    def upload_files(self):
        from form import FormsRequest

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        form = FormsRequest(['file_content', 'domain_id'], body)

        if form.is_valid():
            dict_response = MyDatabase.upload_file(
                form.get_file_content, form.get_file_name, form.get_domain_id
            )
            if(not dict_response['status'] == 'error'):
                status_code = dict_response['status_code']
                header = ('Content-Type', 'application/json')
                response = dict_response
            else:
                status_code = dict_response['status_code']
                header = ('Content-Type', 'application/json')
                response = dict_response
        else:
            response, status_code = form.get_errors()
       
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json') 
        self.end_headers()
        response = json.dumps(response)
        self.wfile.write(response.encode('utf-8'))
    
    def select_domain(self):
        from form import FormsRequest

        content_length = int(self.headers['Content-Length'])
        body = self.rfile.read(content_length)
        form = FormsRequest(['domain_name','username'], body)

        if form.is_valid():
            dict_response = MyDatabase.select_domain(form.get_domain_name, form.get_username)
            if(not dict_response['status'] == 'error'):
                status_code = dict_response['status_code']
                header = ('Content-Type', 'application/json')
                response = dict_response
            else:
                status_code = dict_response['status_code']
                header = ('Content-Type', 'application/json')
                response = dict_response
        else:
            response, status_code = form.get_errors()
            
        self.send_response(status_code)
        self.send_header('Content-Type', 'application/json') 
        self.end_headers()
        response = json.dumps(response)
        self.wfile.write(response.encode('utf-8'))

    def handle_404(self):
        self.send_response(404)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        response = "<html><body><h1>404 Not Found</h1><p>The requested page was not found.</p></body></html>"
        self.wfile.write(response.encode('utf-8'))

server_address = ('', 8000)

MyDatabase.connect_db()

httpd = HTTPServer(server_address, MyDomainServer)
print("Server running on port 8000...")
httpd.serve_forever()

import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

class MyDatabase(BaseHTTPRequestHandler):
    def connect_db():
        try:
        
            sqliteConnection = sqlite3.connect('domains.db')
            cursor = sqliteConnection.cursor()
            print('DB Init')
        
            query = 'select sqlite_version();'
            cursor.execute(query)
        
            result = cursor.fetchall()
            print('SQLite Version is {}'.format(result))
        
            cursor.close()
        
        except sqlite3.Error as error:
            print('Error occurred - ', error)
        
        finally:
        
            if sqliteConnection:
                sqliteConnection.close()
                print('SQLite Connection closed')
                
                MyDatabase.create_table_domains()

        print('\n')
    
    def create_table_domains():
        connection_obj = sqlite3.connect('domains.db')
        
        connection_obj.execute("PRAGMA foreign_keys = ON;")
        
        cursor_obj = connection_obj.cursor()
        
        cursor_obj.execute("DROP TABLE IF EXISTS FILES")
        cursor_obj.execute("DROP TABLE IF EXISTS DOMAINS")

        print('\n')

        print('Creating Tables')

        table_domain = """ 
        CREATE TABLE DOMAINS (
            DomainID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR(255) NOT NULL,
            IsSelected INTEGER DEFAULT 0,
            Username VARCHAR(255)
        ); """
        
        table_file = """ 
        CREATE TABLE FILES (
            FileID INTEGER PRIMARY KEY AUTOINCREMENT,
            DomainID INTEGER, 
            FileName VARCHAR(255) NOT NULL,
            FileContent LONGBLOB NOT NULL, 
            FOREIGN KEY (DomainID) REFERENCES DOMAINS(DomainID)
        ); """
        
        cursor_obj.execute(table_domain)
        print('Created Table DOMAINS')
        cursor_obj.execute(table_file)
        print('Created Table FILES')

        cursor_obj.execute( 
            "INSERT INTO DOMAINS (Name) VALUES ('example');") 
        cursor_obj.execute( 
            "INSERT INTO DOMAINS (Name, IsSelected) VALUES ('example2', 1);") 
        cursor_obj.execute( 
            "INSERT INTO DOMAINS (Name) VALUES ('example3');") 
        
        print("Tables are ready")
        print('\n')

        connection_obj.commit()
        connection_obj.close()

    def select_domain(domain_name, username):
        connection = sqlite3.connect('domains.db')
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM DOMAINS WHERE Name = ?", (domain_name,))
            existing_domain = cursor.fetchone()

            if not existing_domain:
                return {"status": "error", "message": "Dominio não está disponivel para uso", "status_code": 404}

            cursor.execute("SELECT * FROM DOMAINS WHERE Name = ? AND IsSelected = ?", (domain_name, 1))
            is_selected_domain = cursor.fetchone()

            if is_selected_domain:
                return {"status": "error", "message": "Dominio já esta sendo utilizado", "status_code": 409}

            cursor.execute(
                "UPDATE DOMAINS SET isSelected = ?, Username = ? WHERE Name = ?", 
                (1, username, domain_name)
            )
            connection.commit()
           
            return {"status": "success", "message": f"O dominio {domain_name}, foi selecionado com sucesso", "status_code": 200}

        except sqlite3.Error as e:
            return {"status": "error", "message": "Database error", "status_code": 500}

    def check_domain_exists(domain):
        connection = sqlite3.connect('domains.db')
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT * FROM DOMAINS WHERE Name = ?", (domain,))
            existing_domain = cursor.fetchone()

            if not existing_domain:
                return {"status_code": 404, "message": "Dominio não está disponível para uso"}

            domain_id = existing_domain[0]
            cursor.execute("SELECT FileName, FileContent FROM FILES WHERE DomainID = ?", (domain_id,))
            files = cursor.fetchall()

            if not files:
                return {"status_code": 404, "message": "Nenhum arquivo encontrado para este domínio"}

            html_file = next((f for f in files if f[0].endswith('.html')), None)
            image_files = {f[0]: f[1] for f in files if f[0].endswith(('.jpg', '.png', '.gif'))}
            js_files = {f[0]: f[1] for f in files if f[0].endswith('.js')}

            if not html_file:
                return {"status_code": 404, "message": "Arquivo HTML não encontrado"}

            html_content = html_file[1].decode('utf-8')
            for image in image_files:
                html_content = html_content.replace(image, f"/temp/{image}")
            for js in js_files:
                html_content = html_content.replace(js, f"/temp/{js}")

            return {"status_code": 200, "html_content": html_content}

        except sqlite3.Error as e:
            return {"status_code": 500, "message": "Database error"}

    def get_temp_file(filename):
        connection = sqlite3.connect('domains.db')
        cursor = connection.cursor()

        try:
            cursor.execute("SELECT FileContent, FileName FROM FILES WHERE FileName = ?", (filename,))
            file = cursor.fetchone()

            if file:
                mime_type = "application/javascript" if filename.endswith(".js") else "image/png"
                return file[0], mime_type
            return None, None

        except sqlite3.Error as e:
            return {"status_code": 500, "message": "Database error"}

    def upload_file(file_content, file_name, domain_id):
        connection = sqlite3.connect('domains.db')
        cursor = connection.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO FILES (DomainID, FileContent, FileName) VALUES (?, ?, ?)", 
                (domain_id, file_content, file_name)
            )
            connection.commit()  

            return {"status": "success", "message": f"O arquivo {file_name} foi carregado com sucesso", "status_code": 200}

        except sqlite3.Error as e:
            return {"status": "error", "message": "Database error", "status_code": 500}

    def list_domains_json():
        connection = sqlite3.connect('domains.db') 
        
        cursor = connection.execute( 
            "SELECT Name,DomainID from DOMAINS Where IsSelected = 0 ORDER BY Name DESC") 
        
        response_data = []
        for i in cursor:
            response_data.append({
                'domain_name': i[0],
                'domain_id': i[1]
            })

        return response_data
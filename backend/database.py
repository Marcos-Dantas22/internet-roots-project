import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler

class MyDatabase(BaseHTTPRequestHandler):
    def connect_db():
        try:
        
            # Connect to DB and create a cursor
            sqliteConnection = sqlite3.connect('domains.db')
            cursor = sqliteConnection.cursor()
            print('DB Init')
        
            # Write a query and execute it with cursor
            query = 'select sqlite_version();'
            cursor.execute(query)
        
            # Fetch and output result
            result = cursor.fetchall()
            print('SQLite Version is {}'.format(result))
        
            # Close the cursor
            cursor.close()
        
        # Handle errors
        except sqlite3.Error as error:
            print('Error occurred - ', error)
        
        # Close DB Connection irrespective of success
        # or failure
        finally:
        
            if sqliteConnection:
                sqliteConnection.close()
                print('SQLite Connection closed')
                
                # Creating table Domains
                MyDatabase.create_table_domains()

        print('\n')
    
    def create_table_domains():
        # Connecting to sqlite
        connection_obj = sqlite3.connect('domains.db')
        
        # Enable foreign key support in SQLite
        connection_obj.execute("PRAGMA foreign_keys = ON;")
        
        # cursor object
        cursor_obj = connection_obj.cursor()
        
        # Drop the tables if already exists.
        cursor_obj.execute("DROP TABLE IF EXISTS DOMAINS")
        cursor_obj.execute("DROP TABLE IF EXISTS FILES")

        print('\n')

        print('Creating Tables')

        # Creating table DOMAINS
        table_domain = """ 
        CREATE TABLE DOMAINS (
            DomainID INTEGER PRIMARY KEY AUTOINCREMENT,
            Name VARCHAR(255) NOT NULL,
            IsSelected INTEGER DEFAULT 0,
            Username VARCHAR(255)
        ); """
        
        # Creating table FILES
        table_file = """ 
        CREATE TABLE FILES (
            FileID INTEGER PRIMARY KEY AUTOINCREMENT,
            DomainID INTEGER, 
            FileName VARCHAR(255) NOT NULL,
            FileType VARCHAR(50) NOT NULL,
            FileContent TEXT NOT NULL,
            FOREIGN KEY (DomainID) REFERENCES DOMAINS(DomainID)
        ); """
        
        cursor_obj.execute(table_domain)
        print('Created Table DOMAINS')
        cursor_obj.execute(table_file)
        print('Created Table FILES')

        # create instances testes
        cursor_obj.execute( 
            "INSERT INTO DOMAINS (Name) VALUES ('example');") 
        cursor_obj.execute( 
            "INSERT INTO DOMAINS (Name, IsSelected) VALUES ('example2', 1);") 
        cursor_obj.execute( 
            "INSERT INTO DOMAINS (Name) VALUES ('example3');") 
        
        print("Tables are ready")
        print('\n')

        # Commit changes and close the connection
        connection_obj.commit()
        connection_obj.close()

    def select_domain(domain_name, username):
        connection = sqlite3.connect('domains.db')
        cursor = connection.cursor()

        try:
            # Verificar se o domínio já existe
            cursor.execute("SELECT * FROM DOMAINS WHERE Name = ?", (domain_name,))
            existing_domain = cursor.fetchone()

            if not existing_domain:
                return {"status": "error", "message": "Dominio não está disponivel para uso", "status_code": 404}

            cursor.execute("SELECT * FROM DOMAINS WHERE Name = ? AND IsSelected = ?", (domain_name, 1))
            is_selected_domain = cursor.fetchone()

            if is_selected_domain:
                return {"status": "error", "message": "Dominio já esta sendo utilizado", "status_code": 409}

            # Atualizar o valor de isSelected para o domínio especificado
            cursor.execute(
                "UPDATE DOMAINS SET isSelected = ?, Username = ? WHERE Name = ?", 
                (1, username, domain_name)
            )
            connection.commit()
           
            return {"status": "success", "message": f"O dominio {domain_name}, foi selecionado com sucesso", "status_code": 200}

        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return {"status": "error", "message": "Database error", "status_code": 500}

    def upload_file(file_type, file_content, file_name, domain_id):
        pass

    def list_domains_json():
        # create connection to the database 
        connection = sqlite3.connect('domains.db') 
        
        # sql query to display all details from  
        # table in ascending order based on address. 
        cursor = connection.execute( 
            "SELECT Name,DomainID from DOMAINS Where IsSelected = 0 ORDER BY Name DESC") 
        
        # cursor.execute("SELECT * FROM DOMAINS WHERE Name = ?", (domain_name,))
          
        # display data row by row 
        response_data = []
        for i in cursor:
            print(i[0])  # Exibe o nome do domínio
            response_data.append({
                'domain_name': i[0],
                'domain_id': i[1]
            })

        return response_data
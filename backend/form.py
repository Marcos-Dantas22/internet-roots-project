

class FormsRequest:
    def __init__(self, fields, request_body_fields):
        self.fields = fields
        self.request_body_fields = request_body_fields

    def is_valid(self):
        from utils import parse_multipart_data
        is_valid = True

        if(self.request_body_fields == b'' or len(self.request_body_fields) == 0):
            is_valid = False
            return is_valid
            
        # Processar o corpo para obter os campos
        fields_data = parse_multipart_data(self.request_body_fields)

        for field in self.fields:
            if not fields_data.get(field, None):
                is_valid = False
                break
        
        return is_valid
    
    @property
    def get_domain_name(self):
        try:
            from utils import parse_multipart_data
            # Processar o corpo para obter os campos
            fields_data = parse_multipart_data(self.request_body_fields)
            domain_name = fields_data.get('domain_name', None)
            return domain_name
        except Exception as error:
            print(error)

    @property
    def get_username(self):
        try:
            from utils import parse_multipart_data
            # Processar o corpo para obter os campos
            fields_data = parse_multipart_data(self.request_body_fields)
            username = fields_data.get('username', None)
            return username
        except Exception as error:
            print(error)

    @property
    def get_file_type(self):
        try:
            from utils import parse_multipart_data
            # Processar o corpo para obter os campos
            fields_data = parse_multipart_data(self.request_body_fields)
            username = fields_data.get('file_type', None)
            return username
        except Exception as error:
            print(error)
    
    @property
    def get_file_content(self):
        try:
            from utils import parse_multipart_data
            # Processar o corpo para obter os campos
            fields_data = parse_multipart_data(self.request_body_fields)
            username = fields_data.get('file_content', None)
            return username
        except Exception as error:
            print(error)

    @property
    def get_file_name(self):
        try:
            from utils import parse_multipart_data
            # Processar o corpo para obter os campos
            fields_data = parse_multipart_data(self.request_body_fields)
            username = fields_data.get('file_name', None)
            return username
        except Exception as error:
            print(error)
    
    @property
    def get_domain_id(self):
        try:
            from utils import parse_multipart_data
            # Processar o corpo para obter os campos
            fields_data = parse_multipart_data(self.request_body_fields)
            username = fields_data.get('get_domain_id', None)
            return username
        except Exception as error:
            print(error)

    def get_errors(self):
        from utils import parse_multipart_data
        errors = []
        status_code = 400
        
        if(self.request_body_fields == b'' or len(self.request_body_fields) == 0):
            errors.append({'error': 'Nenhum campo foi enviado na requisição'})
            return errors, status_code
            
        # Processar o corpo para obter os campos
        fields_data = parse_multipart_data(self.request_body_fields)

        for field in self.fields:
            if not fields_data.get(field, None):
                errors.append({'error': f'O campo {field} não foi enviado na requisição'})

        return errors, status_code
def parse_multipart_data(data):
    fields = {}
    boundary = data.split(b'\r\n')[0]  # A primeira linha contém o delimitador
    parts = data.split(boundary)

    for part in parts:
        # Ignorar partes vazias
        if not part or part == b'--\r\n':
            continue
        
        # Separar cabeçalho do conteúdo
        header, content = part.split(b'\r\n\r\n', 1)
        content = content.rstrip(b'\r\n--')  # Remover terminações de fim de parte
        
        # Analisar cabeçalho para obter o nome do campo
        header_lines = header.decode('utf-8').split('\r\n')
        for line in header_lines:
            if line.startswith('Content-Disposition'):
                # Extrair o nome do campo
                parts = line.split(';')
                for part in parts:
                    if part.strip().startswith('name='):
                        field_name = part.split('=')[1].strip('"')
                        fields[field_name] = content.decode('utf-8')
                        break
    
    return fields
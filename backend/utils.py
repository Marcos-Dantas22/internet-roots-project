def parse_multipart_data(data):
    fields = {}
    boundary = data.split(b'\r\n')[0] 
    parts = data.split(boundary)

    for part in parts:
        if not part or part == b'--\r\n':
            continue

        try:
            header, content = part.split(b'\r\n\r\n', 1)
        except ValueError:
            continue  

        content = content.rstrip(b'\r\n--') 

        header_lines = header.decode('utf-8').split('\r\n')
        field_name = None
        is_file = False
        file_name = None

        for line in header_lines:
            if line.startswith('Content-Disposition'):
                # Extrair o nome do campo e, se for o caso, o nome do arquivo
                parts = line.split(';')
                for part in parts:
                    part = part.strip()
                    if part.startswith('name='):
                        field_name = part.split('=')[1].strip('"')
                    elif part.startswith('filename='):
                        is_file = True
                        file_name = part.split('=')[1].strip('"')

        if field_name:
            if is_file:
                # Armazenar arquivos binários como dicionário com o conteúdo e nome do arquivo
                fields[field_name] = {
                    "filename": file_name,
                    "content": content
                }
            else:
                # Armazenar campos de texto como string
                fields[field_name] = content.decode('utf-8')

    return fields
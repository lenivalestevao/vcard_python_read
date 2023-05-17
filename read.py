import re
import base64

def extract_field(line, field_name):
    match = re.search(f'{field_name}:(.*)', line)
    if match:
        return match.group(1).strip()

def extract_photo(line):
    match = re.search(r'PHOTO;ENCODING=b;TYPE=([^:]*):(.*)', line)
    if match:
        photo_type = match.group(1).strip()
        photo_data = match.group(2).strip()

        # Remove espaços em branco e quebras de linha
        photo_data = re.sub(r'\s', '', photo_data)

        photo_bytes = base64.b64decode(photo_data)
        return photo_type, photo_bytes
    else:
        return None, None

def format_address(address):
    address_parts = address.split(';')
    formatted_parts = []
    for part in address_parts:
        if part.strip():
            formatted_parts.append(part.strip())
    formatted_address = ', '.join(formatted_parts)
    return formatted_address

def parse_vcard(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    contacts = []
    contact = {}

    for line in lines:
        if line.startswith('BEGIN:VCARD'):
            contact = {}
        elif line.startswith('END:VCARD'):
            contacts.append(contact)
        else:
            name = extract_field(line, 'FN')
            org = extract_field(line, 'ORG')
            title = extract_field(line, 'TITLE')
            email_match = re.match(r'EMAIL;.*:(.*)', line)
            phone_match = re.match(r'TEL;.*:(.*)', line)
            address_match = re.match(r'ADR;.*:(.*)', line)
            photo_type, photo = extract_photo(line)

            if name:
                contact['name'] = name
            if org:
                contact['org'] = org
            if title:
                contact['title'] = title
            if email_match:
                if 'emails' not in contact:
                    contact['emails'] = []
                email = email_match.group(1).strip()
                contact['emails'].append(email)
            if phone_match:
                contact['phone'] = phone_match.group(1).strip()
            if address_match:
                address = address_match.group(1).strip()
                formatted_address = format_address(address)
                contact['address'] = formatted_address
            if photo:
                contact['photo_type'] = photo_type
                contact['photo'] = photo

    return contacts


def save_contacts_html(contacts):
    html = '''
    <html>
    <head>
        <style>
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th, td {
                padding: 8px;
                border: 1px solid #ccc;
            }
            img {
                max-width: 100px;
                max-height: 100px;
            }
        </style>
    </head>
    <body>
    <table>
        <thead>
            <tr>
                <th>Nome</th>
                <th>Organização</th>
                <th>Título</th>
                <th>Endereço</th>
                <th>Telefone</th>
                <th>E-mails</th>
                <th>Foto</th>
            </tr>
        </thead>
        <tbody>
    '''

    for contact in contacts:
        html += '<tr>'
        html += f'<td>{contact.get("name", "N/A")}</td>'
        html += f'<td>{contact.get("org", "N/A")}</td>'
        html += f'<td>{contact.get("title", "N/A")}</td>'
        html += f'<td>{contact.get("address", "N/A")}</td>'
        html += f'<td>{contact.get("phone", "N/A")}</td>'
        if 'emails' in contact:
            emails = ', '.join(contact['emails'])
            html += f'<td>{emails}</td>'
        else:
            html += '<td>N/A</td>'
        if 'photo' in contact and 'photo_type' in contact:
            photo_type = contact['photo_type']
            photo_data = base64.b64encode(contact['photo']).decode('utf-8')
            html += f'<td><img src="data:image/{photo_type};base64,{photo_data}" alt="Foto"></td>'
        else:
            html += '<td>N/A</td>'
        html += '</tr>'

    html += '''
        </tbody>
    </table>
    </body>
    </html>
    '''

    return html

file_path = 'contacts.vcf'
contacts = parse_vcard(file_path)

html = save_contacts_html(contacts)

with open('contatos.html', 'w') as file:
    file.write(html)
    
for contact in contacts:
    #/*html = save_contact_html(contact)
    #file_name = f'{contact.get("name", "N_A")}.html'
    #with open(file_name, 'w') as file:
    #    file.write(html)*/
        
    print('Nome:', contact.get('name', 'N/A'))
    print('Organização:', contact.get('org', 'N/A'))
    print('Título:', contact.get('title', 'N/A'))
    print('Endereço:', contact.get('address', 'N/A'))
    print('Telefone:', contact.get('phone', 'N/A'))
    if 'emails' in contact:
        print('E-mails:')
        for email in contact['emails']:
            print('-', email)
    if 'photo' in contact and 'photo_type' in contact:
        photo_type = contact['photo_type']
        photo_bytes = contact['photo']
        print('Tipo de foto:', photo_type)
        print('Foto:', photo_bytes)
    print()

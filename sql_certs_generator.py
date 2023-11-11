sql= ""

for x in range(10):
    owner = f"owner_{x}"
    common_name = f"common_name_{x}"
    sql = sql + f"""
    INSERT INTO certificates (owner, common_name, serial_number, fingerprint, cert_b64, expiration_date)
    VALUES ('{owner}', '{common_name}' , '123456789', 'abcdef123456', 'base64_certificate_data', '2023-12-31');
    """ + '\n'

with open("./certs_10.sql", "w") as f:
    f.write(sql)

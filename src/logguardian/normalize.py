import pandas as pd
import re
import datetime
from anonymizeip import anonymize_ip

def normalize_log(input_file: str, output_file: str):
    """Normaliza um arquivo de log do Traefik em formato CSV."""
    ufw_re = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(\s-\s[-|[a-z]+\s)\[(\d{2}/[a-zA-Z]{3}/\d{4}:\d{2}:\d{2}:\d{2})(\s[\-|\+]\d{4})\]\s["](GET|POST|HEAD|OPTIONS|CONNECT|PUT|PATCH)\s(.*)HTTP.*["]\s([2][0][0]|[4][0][4]|[4][2][9]|[\s-])\s([0-9]*)\s(.*)'

    pattern = re.compile(ufw_re)
    split_list = []

    with open(input_file, 'r') as log_data:
        for line in log_data:
            x = re.search(ufw_re, line)
            if x:
                data = x.group(3)
                data1 = datetime.datetime.strptime(data, '%d/%b/%Y:%H:%M:%S').strftime('%Y-%m-%d %H:%M:%S')
                data2 = datetime.datetime.strptime(data, '%d/%b/%Y:%H:%M:%S').strftime('%Y-%m-%d')
                ip = "0.0.0.0"
                try:
                    ip = anonymize_ip(x.group(1))
                except Exception:
                    ip = "0.0.0.0"
                split_list.append([data1, data2, ip, x.group(7), x.group(5), x.group(6), x.group(8)])

    df = pd.DataFrame(split_list, columns=['data1', 'data2', 'ip', 'status', 'metodo', 'recurso', 'tamanho'])
    df.status = df.status.replace('-', 404)
    df.status = pd.to_numeric(df.status)
    df.to_csv(output_file, index=False)

    print(f"Normalização concluída: {output_file}")
    return output_file
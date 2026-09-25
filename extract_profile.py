import zipfile, os
import xml.etree.ElementTree as ET

base = r'C:\Users\Hamdy\Downloads\OneDrive_2026-09-24\OPRELL PROFILE'

def all_text(path):
    z = zipfile.ZipFile(path)
    names = [n for n in z.namelist() if n.endswith('.xml') and ('slide' in n or 'document' in n)]
    out = []
    for n in sorted(names):
        try:
            root = ET.fromstring(z.read(n))
            buf = []
            for el in root.iter():
                if el.tag.endswith('}t') and el.text and el.text.strip():
                    buf.append(el.text.strip())
            if buf:
                out.append('=== ' + n + ' ===')
                out.append(' | '.join(buf))
        except Exception:
            pass
    return '\n'.join(out)

for f in os.listdir(base):
    if f.endswith(('.pptx', '.docx')):
        p = os.path.join(base, f)
        try:
            print('\n\n##########', f, '##########')
            print(all_text(p))
        except Exception as e:
            print(f, 'ERR', e)

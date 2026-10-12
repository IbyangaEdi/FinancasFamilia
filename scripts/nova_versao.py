"""Marca uma nova versão do site antes de publicar: atualiza VERSAO em docs/index.html e docs/versao.json.
Quem estiver com a página aberta vê o aviso "Há uma versão nova do sistema" em até 5 minutos.
Uso: python3 scripts/nova_versao.py"""
import datetime, json, pathlib, re
raiz = pathlib.Path(__file__).resolve().parent.parent
v = datetime.datetime.now().strftime('%Y-%m-%d.%H%M%S')
idx = raiz / 'docs' / 'index.html'
s = idx.read_text()
s, n = re.subn(r"const VERSAO = '[^']*';", f"const VERSAO = '{v}';", s, count=1)
assert n == 1, 'VERSAO não encontrada em docs/index.html'
idx.write_text(s)
(raiz / 'docs' / 'versao.json').write_text(json.dumps({'versao': v}) + '\n')
print('versão', v)

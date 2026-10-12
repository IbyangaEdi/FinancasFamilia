"""Funções mínimas para conversar com a API da Pluggy (uso local, nos testes da Fase 1)."""
import json, pathlib, re, urllib.request, urllib.error

RAIZ = pathlib.Path(__file__).resolve().parent.parent
BASE = 'https://api.pluggy.ai'

def ler_env():
    env = {}
    for l in (RAIZ / '.env').read_text().splitlines():
        if '=' in l and not l.lstrip().startswith('#'):
            k, v = l.split('=', 1); v = v.strip()
            env[k.strip()] = '' if v.startswith('#') else re.split(r'\s+#', v, maxsplit=1)[0].strip().strip('"\'')
    return env

class Pluggy:
    def __init__(self):
        env = ler_env()
        self.key = None
        self.key = self.req('POST', '/auth', {'clientId': env['PLUGGY_CLIENT_ID'], 'clientSecret': env['PLUGGY_CLIENT_SECRET']})['apiKey']

    def req(self, metodo, caminho, corpo=None):
        r = urllib.request.Request(BASE + caminho, method=metodo, data=json.dumps(corpo).encode() if corpo is not None else None)
        r.add_header('Content-Type', 'application/json'); r.add_header('User-Agent', 'financas-familia/0.1')
        if self.key: r.add_header('X-API-KEY', self.key)
        try:
            with urllib.request.urlopen(r, timeout=60) as resp:
                txt = resp.read(); return json.loads(txt) if txt else {}
        except urllib.error.HTTPError as e:
            raise RuntimeError(f'{metodo} {caminho} → HTTP {e.code}: {e.read()[:400].decode(errors="replace")}')

    def transacoes(self, account_id):
        """GET /v2/transactions com paginação por cursor (o /transactions antigo foi desativado)."""
        out, cursor = [], None
        while True:
            d = self.req('GET', f'/v2/transactions?accountId={account_id}' + (f'&cursor={cursor}' if cursor else ''))
            out += d.get('results', [])
            cursor = d.get('next')
            if not cursor: return out

    def todas_paginas(self, caminho):
        sep = '&' if '?' in caminho else '?'; pag, out = 1, []
        while True:
            d = self.req('GET', f'{caminho}{sep}page={pag}&pageSize=500')
            out += d.get('results', [])
            if pag >= d.get('totalPages', 1): return out
            pag += 1

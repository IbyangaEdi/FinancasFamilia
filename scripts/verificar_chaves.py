"""Confere as chaves do .env sem mostrar os valores. Uso: python3 scripts/verificar_chaves.py"""
import json, pathlib, urllib.request, urllib.error

def ler_env(caminho):
    env = {}
    for linha in pathlib.Path(caminho).read_text().splitlines():
        linha = linha.strip()
        if not linha or linha.startswith('#') or '=' not in linha:
            continue
        k, v = linha.split('=', 1)
        v = v.strip()
        if v.startswith('#'):
            v = ''
        if v and v[0] not in '"\'':
            v = v.split(' #')[0].split('\t#')[0].strip()
        env[k.strip()] = v.strip('"\'')
    return env

def chamar(url, headers=None, data=None):
    req = urllib.request.Request(url, headers={'User-Agent': 'financas-familia/0.1', **(headers or {})}, data=json.dumps(data).encode() if data else None,
                                 method='POST' if data else 'GET')
    if data:
        req.add_header('Content-Type', 'application/json')
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return r.status, json.loads(r.read() or b'{}')
    except urllib.error.HTTPError as e:
        try:
            return e.code, json.loads(e.read() or b'{}')
        except Exception:
            return e.code, {}

env = ler_env(pathlib.Path(__file__).resolve().parent.parent / '.env')
ok = lambda b: '✅' if b else '❌'

def testar(nome, chave, fn):
    if not env.get(chave):
        print(f'⬜ {nome}: ainda não preenchida ({chave})'); return
    try:
        print(fn())
    except Exception as e:
        print(f'❌ {nome}: erro ao testar ({type(e).__name__})')

def supa_pub():
    s, _ = chamar(env['SUPABASE_URL'] + '/auth/v1/settings', {'apikey': env['SUPABASE_PUBLISHABLE_KEY']})
    return f'{ok(s == 200)} Supabase chave pública (HTTP {s})'

def supa_sec():
    s, d = chamar(env['SUPABASE_URL'] + '/auth/v1/admin/users?per_page=1', {'apikey': env['SUPABASE_SECRET_KEY']})
    return f'{ok(s == 200)} Supabase chave secreta (HTTP {s})' + ('' if s == 200 else f" — {d.get('msg') or d.get('message') or ''}")

def pluggy():
    s, d = chamar('https://api.pluggy.ai/auth', data={'clientId': env.get('PLUGGY_CLIENT_ID'), 'clientSecret': env['PLUGGY_CLIENT_SECRET']})
    return f"{ok(s == 200 and 'apiKey' in d)} Pluggy Client ID + Secret (HTTP {s})"

def resend():
    s, d = chamar('https://api.resend.com/api-keys', {'Authorization': 'Bearer ' + env['RESEND_API_KEY']})
    # chave "Sending access" não pode listar chaves (401/403 com mensagem de permissão) — isso já prova que ela existe
    valida = s == 200 or (s in (401, 403) and 'restricted' in json.dumps(d).lower())
    return f'{ok(valida)} Resend (HTTP {s}{", chave só de envio — correto" if s != 200 and valida else ""})'

def brapi():
    s, d = chamar('https://brapi.dev/api/quote/PETR4', {'Authorization': 'Bearer ' + env['BRAPI_TOKEN']})
    return f'{ok(s == 200)} brapi.dev (HTTP {s})'

testar('Supabase chave pública', 'SUPABASE_PUBLISHABLE_KEY', supa_pub)
testar('Supabase chave secreta', 'SUPABASE_SECRET_KEY', supa_sec)
print(f"{'✅' if env.get('SUPABASE_DB_PASSWORD') else '⬜'} Senha do banco {'preenchida' if env.get('SUPABASE_DB_PASSWORD') else 'ainda não preenchida'} (testada à parte)")
testar('Pluggy', 'PLUGGY_CLIENT_SECRET', pluggy)
testar('Resend', 'RESEND_API_KEY', resend)
testar('brapi.dev', 'BRAPI_TOKEN', brapi)

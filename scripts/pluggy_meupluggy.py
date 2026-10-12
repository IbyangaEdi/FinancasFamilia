"""Fase 1, passo 2: liga a aplicação ao Meu Pluggy do Edval e resume o que chega.
Uso: python3 scripts/pluggy_meupluggy.py         (cria a conexão e mostra o link de autorização)
     python3 scripts/pluggy_meupluggy.py resumo  (só relê a conexão já autorizada)"""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from pluggy_lib import Pluggy, RAIZ

ARQ = RAIZ / '.pluggy_items.json'   # fora do Git (só ids, nenhum segredo)
p = Pluggy()
estado = json.loads(ARQ.read_text()) if ARQ.exists() else {}

if sys.argv[1:] != ['resumo']:
    item = p.req('POST', '/items', {'connectorId': 200, 'parameters': {}, 'clientUserId': 'edval'})
    estado['meupluggy'] = item['id']; ARQ.write_text(json.dumps(estado, indent=1))
    url = None
    for _ in range(30):
        item = p.req('GET', f"/items/{item['id']}")
        par = item.get('parameter') or {}
        url = par.get('data') if str(par.get('type', '')).lower() in ('oauth', 'oauth_url') or str(par.get('data', '')).startswith('http') else None
        if url or item['status'] in ('UPDATED', 'LOGIN_ERROR'): break
        time.sleep(2)
    if url:
        print('ABRA ESTE LINK NO NAVEGADOR PARA AUTORIZAR:\n' + url, flush=True)
    print('Aguardando autorização (até 15 min)…', flush=True)
    for _ in range(300):
        item = p.req('GET', f"/items/{item['id']}")
        if item['status'] in ('UPDATED', 'LOGIN_ERROR', 'OUTDATED') and item.get('executionStatus') not in ('CREATED',): break
        time.sleep(3)
    print('Status:', item['status'], item.get('executionStatus'), item.get('error') or '')

iid = estado['meupluggy']
contas = p.req('GET', f'/accounts?itemId={iid}')['results']
print(f'\n{len(contas)} contas/cartões recebidos:')
for c in contas:
    tx = p.transacoes(c['id'])
    datas = sorted(t['date'][:10] for t in tx)
    banco = (c.get('bankData') or {}).get('transferNumber') or ''
    print(f"• {c.get('type')}/{c.get('subtype')} · {c.get('name')} {c.get('marketingName') or ''} · titular {c.get('owner') or '—'} · saldo {c.get('balance')} · {len(tx)} transações" + (f' ({datas[0]} a {datas[-1]})' if datas else ''))
    if c.get('type') == 'CREDIT':
        cd = c.get('creditData') or {}
        bills = p.req('GET', f"/bills?accountId={c['id']}").get('results', [])
        print(f"    limite {cd.get('creditLimit')} · disponível {cd.get('availableCreditLimit')} · vence {str(cd.get('balanceDueDate'))[:10]} · {len(bills)} faturas")
inv = p.req('GET', f'/investments?itemId={iid}').get('results', [])
print(f'Investimentos: {len(inv)}')

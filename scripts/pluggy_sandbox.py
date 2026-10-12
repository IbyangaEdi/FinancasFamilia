"""Fase 1, passo 1: conecta o banco de teste da Pluggy e resume o que chega. Não usa dados reais."""
import json, sys, time, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).parent)); from pluggy_lib import Pluggy

p = Pluggy()
# credenciais públicas do sandbox, documentadas pela Pluggy
item = p.req('POST', '/items', {'connectorId': 2, 'parameters': {'user': 'user-ok', 'password': 'password-ok'}})
print('Conexão de teste criada; aguardando sincronizar…')
for _ in range(40):
    item = p.req('GET', f"/items/{item['id']}")
    if item['status'] in ('UPDATED', 'LOGIN_ERROR', 'OUTDATED', 'WAITING_USER_INPUT'): break
    time.sleep(3)
print('Status:', item['status'], item.get('executionStatus'))

try:
  contas = p.req('GET', f"/accounts?itemId={item['id']}")['results']
  dump = {'item': item, 'contas': []}
  for c in contas:
      tx = p.transacoes(c['id'])
      bills = p.req('GET', f"/bills?accountId={c['id']}").get('results', []) if c['type'] == 'CREDIT' else []
      dump['contas'].append({'conta': c, 'transacoes': tx, 'faturas': bills})
      datas = sorted(t['date'][:10] for t in tx)
      print(f"\n• {c['type']}/{c.get('subtype')}: {c.get('name')} — saldo {c.get('balance')} {c.get('currencyCode')}")
      if c['type'] == 'CREDIT':
          cd = c.get('creditData') or {}
          print(f"  limite {cd.get('creditLimit')} · disponível {cd.get('availableCreditLimit')} · fecha {str(cd.get('balanceCloseDate'))[:10]} · vence {str(cd.get('balanceDueDate'))[:10]} · faturas: {len(bills)}")
      print(f"  {len(tx)} transações" + (f" de {datas[0]} a {datas[-1]}" if datas else ''))
      cats = {}
      for t in tx: cats[t.get('category') or '—'] = cats.get(t.get('category') or '—', 0) + 1
      print('  categorias:', ', '.join(f'{k} ({v})' for k, v in sorted(cats.items(), key=lambda x: -x[1])[:8]))
      for t in tx[:3]:
          print(f"  ex.: {t['date'][:10]} | {t['description'][:40]:40} | {t['amount']:>10} | {t.get('type')} | parcela: {(t.get('creditCardMetadata') or {}).get('installmentNumber')}/{(t.get('creditCardMetadata') or {}).get('totalInstallments')}")
  inv = p.req('GET', f"/investments?itemId={item['id']}").get('results', [])
  print(f"\nInvestimentos: {len(inv)}", '; '.join(f"{i.get('type')}/{i.get('subtype')} {i.get('name','')[:25]} = {i.get('balance')}" for i in inv[:5]))
  dump['investimentos'] = inv
  out = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else None
  if out: out.write_text(json.dumps(dump, ensure_ascii=False, indent=1)); print('\nDados completos salvos para análise.')
finally:
  p.req('DELETE', f"/items/{item['id']}"); print('Conexão de teste apagada.')

"""Teste de ponta a ponta com um servidor HTTP REAL (uvicorn), simulando o que o frontend faz.
O Firebase é substituído por versões em memória (não precisa de credenciais).
Rodar (dentro de backend/, com o venv ativo):  python -m tests.e2e_servidor_real
"""
import base64
import hashlib
import io
import threading
import time

import httpx
import uvicorn
from PIL import Image

from app import emailer
from app.deps import get_auth, get_db, get_rtdb, get_rtdb_opcional
from app.main import app
from tests.fakes import FakeAuth, FakeFirestore, FakeRTDB

BASE, ORIGEM = "http://127.0.0.1:8765", "http://localhost:3000"
db, fb, rt = FakeFirestore(), FakeAuth(), FakeRTDB()
app.dependency_overrides[get_db] = lambda: db
app.dependency_overrides[get_auth] = lambda: fb
app.dependency_overrides[get_rtdb] = lambda: rt
app.dependency_overrides[get_rtdb_opcional] = lambda: rt
servidor = uvicorn.Server(uvicorn.Config(app, port=8765, log_level="warning"))
threading.Thread(target=servidor.run, daemon=True).start()
while not servidor.started:
    time.sleep(0.05)

passos = 0


def ok(cond, texto):
    global passos
    passos += 1
    print(f"  {'✓' if cond else '✗ FALHOU'} {texto}")
    if not cond:
        raise SystemExit(1)


c = httpx.Client(base_url=BASE, headers={"Origin": ORIGEM}, timeout=15)
SENHA, EMAIL = "Senha@123", "responsavel@exemplo.com"

print("1) CORS (o navegador faz um 'preflight' antes de cada chamada)")
r = c.options("/categorias", headers={"Access-Control-Request-Method": "POST", "Access-Control-Request-Headers": "authorization,content-type"})
ok(r.status_code == 200 and r.headers.get("access-control-allow-origin") == ORIGEM, "origem http://localhost:3000 liberada")
r = c.options("/categorias", headers={"Origin": "http://site-malicioso.com", "Access-Control-Request-Method": "GET"})
ok("access-control-allow-origin" not in r.headers, "origem desconhecida NÃO liberada")

print("2) Cadastro só cria a conta depois do código")
ok(c.post("/auth/cadastro", json={"nome": "Zeus Alves", "email": EMAIL, "senha": SENHA}).status_code == 202, "etapa 1: código enviado")
ok(fb.usuarios == {}, "conta AINDA não existe no Firebase")
for _ in range(60):  # o e-mail sai em segundo plano, logo depois da resposta
    if emailer.outbox:
        break
    time.sleep(0.05)
ok(len(emailer.outbox) == 1 and emailer.outbox[-1]["para"] == EMAIL, "e-mail com o código chegou à caixa de entrada")
codigo = emailer.outbox[-1]["corpo"].split("Seu código: ")[1][:6]
ok(c.post("/auth/confirmar", json={"email": EMAIL, "codigo": "000000", "senha": SENHA}).status_code == 400, "código errado é recusado")
ok(fb.usuarios == {}, "conta continua inexistente")
ok(c.post("/auth/confirmar", json={"email": EMAIL, "codigo": codigo, "senha": SENHA}).status_code == 201, "etapa 2: código certo cria a conta")
ok(EMAIL in fb.usuarios, "conta existe, com e-mail verificado")

uid = fb.usuarios[EMAIL]["uid"]
auth = {"Authorization": f"Bearer tok:{uid}:{EMAIL}:1"}  # no real, é o ID token do Firebase
c.headers.update(auth)

print("3) Perfil e preferências")
perfil = c.get("/me").json()
ok(perfil["email"] == EMAIL and perfil["nome"] == "Zeus Alves", "GET /me cria o perfil com o nome do cadastro")
ok(c.patch("/me", json={"tamanho_fonte": 14, "modo_escuro": True}).json()["tamanho_fonte"] == 14, "preferências salvas")
ok(httpx.get(f"{BASE}/me").status_code == 401, "sem token → 401")

print("4) Categorias e botões com imagem e áudio (multipart real)")
cat = c.post("/categorias", json={"nome": "Casa"}).json()
buf = io.BytesIO(); Image.new("RGB", (800, 400), (30, 120, 200)).save(buf, "PNG")
img = c.post("/midias", files={"arquivo": ("agua.png", buf.getvalue(), "image/png")}, data={"tipo": "imagem"}).json()
wav = b"RIFF" + (36).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 32
aud = c.post("/midias", files={"arquivo": ("agua.wav", wav, "audio/wav")}, data={"tipo": "audio"}).json()
ok(img["mime"] == "image/jpeg" and aud["tipo"] == "audio", "upload de imagem e áudio")
b = c.post(f"/categorias/{cat['id']}/botoes", json={"rotulo": "Beber água", "imagem_id": img["id"], "audio_id": aud["id"]}).json()
ok(b["audio"] == "agua.wav", "botão criado com áudio e imagem")
blob = c.get(f"/midias/{aud['id']}/arquivo")
ok(blob.status_code == 200 and blob.content == wav, "áudio baixado como blob (para tocar no navegador)")
ok(Image.open(io.BytesIO(c.get(f"/midias/{img['id']}/arquivo").content)).size == (240, 240), "imagem reduzida para 240×240")

print("5) Dispositivo ESP32 (pareamento → config → telemetria)")
disp = c.post("/dispositivos", json={"mac": "24:62:AB:E4:C1:0C", "nome": "ESP32 - C.A.S.A."}).json()
ok(disp["device_token"].startswith("casa_") and disp["codigo"] == "ESP32-C10C", "pareado; token mostrado uma vez")
esp = httpx.Client(base_url=BASE, headers={"X-Device-Token": disp["device_token"]}, timeout=15)
cfg = esp.get("/device/config").json()
ok(cfg["layout"]["categorias"][0]["botoes"][0]["rotulo"] == "Beber água" and len(cfg["arquivos"]) == 2, "aparelho baixa layout e lista de arquivos")
ok(esp.get(cfg["arquivos"][0]["url"]).status_code == 200, "aparelho baixa a mídia")
lote = {"bateria_pct": 15, "ssid": "casa_2G", "sinal_wifi": 80, "ip": "192.168.0.9", "firmware": "v1.0",
        "acionamentos": [{"botao_id": b["id"], "uid_local": f"u{i}", "ha_segundos": 60 * i} for i in range(3)]}
ok(esp.post("/device/telemetria", json=lote).json()["recebidos"] == 3, "3 acionamentos recebidos")
ok(esp.post("/device/telemetria", json=lote).json()["duplicados"] == 3, "reenvio não duplica")
ok(c.get("/dispositivos").json()[0]["online"] is True, "dispositivo aparece online no dashboard")

print("6) Histórico, desempenho, PDF e notificações")
h = c.get("/historico", params={"periodo": "dia"}).json()
ok(h["total_acionamentos"] == 3 and h["mais_acionados"][0]["nome"] == "Beber água", "histórico mostra o uso")
d = c.get("/desempenho", params={"periodo": "semana"}).json()
ok(d["total"] == 3 and len(d["serie"]) == 7, "gráfico: 7 pontos (semana)")
pdf = c.get("/desempenho/relatorio", params={"periodo": "semana"})
ok(pdf.content.startswith(b"%PDF") and "attachment" in pdf.headers["content-disposition"], "PDF gerado para download")
n = c.get("/notificacoes").json()
ok(n["nao_lidas"] == 2 and {i["tipo"] for i in n["itens"]} == {"dispositivo_conectado", "bateria_baixa"}, "notificações: pareamento + bateria baixa")
ok(c.delete(f"/historico/{h['mais_acionados'][0]['id']}").status_code == 200, "histórico de um botão removido")

print("6b) Fluxo do IoT: app → API → Firestore (base64) → sinal no Realtime Database → aparelho → concluído → limpeza")
foto = io.BytesIO(); Image.new("RGB", (900, 500), (200, 60, 60)).save(foto, "PNG")
r = c.post("/iot/midias", files={"arquivo": ("agua.png", foto.getvalue(), "image/png")},
           data={"dispositivo": "24:62:AB:E4:C1:0C", "botao_id": b["id"]})
ok(r.status_code == 201 and r.json()["estado"] == "pendente" and r.json()["largura"] == 240, "app envia a imagem: API converte (240×240) e enfileira")
mid = r.json()["id"]
doc = db.data[("dispositivos", "24:62:AB:E4:C1:0C", "fila", mid)]
jpeg = base64.b64decode(doc["base64"])
ok(Image.open(io.BytesIO(jpeg)).size == (240, 240) and doc["mime"] == "image/jpeg", "Firestore guarda o BASE64 de um JPEG 240×240")
ok(rt.get(f"dispositivos/24:62:AB:E4:C1:0C/sync/{mid}")["estado"] == "pendente", "flag 'pendente' gravada no Realtime Database")
ok(c.get(f"/iot/midias/{mid}", params={"dispositivo": "24:62:AB:E4:C1:0C"}).json()["estado"] == "pendente", "app consulta o estado do envio")
ok([i["id"] for i in esp.get("/device/iot/pendentes").json()] == [mid], "aparelho vê o item pendente")
item = esp.get(f"/device/iot/midias/{mid}").json()
bruto = base64.b64decode(item["base64"])
ok(hashlib.sha256(bruto).hexdigest() == item["sha256"] and item["rotulo"] == "Beber água", "aparelho baixa, decodifica e confere o SHA-256")
ok(rt.get(f"dispositivos/24:62:AB:E4:C1:0C/sync/{mid}")["estado"] == "baixando", "estado passa a 'baixando'")
ok(esp.post(f"/device/iot/midias/{mid}/concluido", json={"sha256": "0" * 64}).status_code == 422, "hash errado é recusado (nada é apagado)")
ok(("dispositivos", "24:62:AB:E4:C1:0C", "fila", mid) in db.data, "o conteúdo continua no Firestore após o hash errado")
ok(esp.post(f"/device/iot/midias/{mid}/concluido", json={"sha256": item["sha256"]}).json()["estado"] == "concluido", "aparelho confirma 'concluído'")
ok(("dispositivos", "24:62:AB:E4:C1:0C", "fila", mid) not in db.data, "base64 APAGADO do Firestore (limpeza)")
ok(rt.get(f"dispositivos/24:62:AB:E4:C1:0C/sync/{mid}")["estado"] == "concluido", "app enxerga 'concluído' no Realtime Database")
ok(esp.post(f"/device/iot/midias/{mid}/concluido", json={}).status_code == 200, "confirmação repetida (resposta perdida) é aceita")
ok(esp.get(f"/device/iot/midias/{mid}").status_code == 404, "item concluído não pode ser baixado de novo")
wav2 = b"RIFF" + (4000).to_bytes(4, "little") + b"WAVEfmt " + b"\x00" * 4000
r2 = c.post("/iot/midias", files={"arquivo": ("agua.wav", wav2, "audio/wav")}, data={"dispositivo": "24:62:AB:E4:C1:0C"})
ok(r2.status_code == 201 and r2.json()["tipo"] == "audio", "áudio WAV segue o mesmo fluxo")
ok(c.delete(f"/iot/midias/{r2.json()['id']}", params={"dispositivo": "24:62:AB:E4:C1:0C"}).status_code == 204, "app cancela um envio pendente")
ok(c.post("/iot/midias", files={"arquivo": ("x.txt", b"nao sou imagem", "image/png")}, data={"dispositivo": "24:62:AB:E4:C1:0C"}).status_code == 415, "arquivo falso recusado")
ok(httpx.post(f"{BASE}/iot/midias", files={"arquivo": ("a.png", foto.getvalue(), "image/png")}, data={"dispositivo": "24:62:AB:E4:C1:0C"}).status_code == 401, "sem login → 401")

print("7) Exclusão de conta (LGPD)")
ok(c.delete("/me").status_code == 204, "conta excluída")
ok(fb.apagados == [uid] and db.data == {}, "usuário apagado do Auth e nenhum dado restou no banco")
ok(rt.get("dispositivos/24:62:AB:E4:C1:0C") is None, "nenhum sinal restou no Realtime Database")
ok(esp.get("/device/config").status_code == 401, "token do aparelho deixa de valer")
print(f"\nTODOS OS {passos} PASSOS OK")

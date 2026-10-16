"""Cálculos de histórico e desempenho a partir de usuarios/{uid}/acionamentos."""
import hashlib
from collections import Counter
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .config import settings

TZ = ZoneInfo(settings.timezone)
DIAS = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]


def inicio_janela(periodo: str) -> datetime | None:
    """dia = hoje (00h local) · semana = últimos 7 dias · mes = últimos 30 dias · todos = sem limite."""
    dias = {"dia": 0, "semana": 6, "mes": 29}.get(periodo)
    if dias is None:
        return None
    hoje0 = datetime.now(TZ).replace(hour=0, minute=0, second=0, microsecond=0)
    return (hoje0 - timedelta(days=dias)).astimezone(timezone.utc)


def _dt(valor) -> datetime:
    d = valor if isinstance(valor, datetime) else datetime.fromisoformat(valor)
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def colecao(db, uid):
    return db.collection("usuarios").document(uid).collection("acionamentos")


def carregar(db, uid: str, periodo: str, dispositivo: str | None = None, busca: str | None = None) -> list[dict]:
    ini, out = inicio_janela(periodo), []
    for s in colecao(db, uid).stream():
        a = s.to_dict()
        dt = _dt(a["acionado_em"])
        if ini and dt < ini:
            continue
        if dispositivo and a.get("dispositivo") != dispositivo:
            continue
        if busca and busca.strip().lower() not in a["botao_nome"].lower():
            continue
        out.append({**a, "_id": s.id, "_dt": dt})
    return out


def id_item(nome: str, categoria: str) -> str:
    return hashlib.sha1(f"{nome}|{categoria}".encode()).hexdigest()[:12]


def _fmt_data(dt: datetime) -> str:
    local, hoje = dt.astimezone(TZ).date(), datetime.now(TZ).date()
    if local == hoje:
        return "Hoje"
    if local == hoje - timedelta(days=1):
        return "Ontem"
    return local.strftime("%d/%m/%Y")


def _fmt_relativo(dt: datetime) -> str:
    seg = int((datetime.now(timezone.utc) - dt).total_seconds())
    if seg < 90:
        return "Agora"
    if seg < 3600:
        return f"{seg // 60} min atrás"
    if seg < 86400:
        return f"{seg // 3600} h atrás"
    return f"{seg // 86400} d atrás"


def ranking(registros: list[dict], limite: int) -> dict:
    grupos: dict[tuple, dict] = {}
    for a in registros:
        g = grupos.setdefault((a["botao_nome"], a["categoria_nome"]), {"total": 0, "ultimo": a["_dt"]})
        g["total"] += 1
        g["ultimo"] = max(g["ultimo"], a["_dt"])
    itens = []
    for (nome, cat), g in grupos.items():
        t, ult = g["total"], g["ultimo"]
        itens.append({"id": id_item(nome, cat), "nome": nome, "categoria": cat, "total": t,
                      "ultimo_acionamento": ult.isoformat(),
                      "detalhe": f"{t} {'VEZ' if t == 1 else 'VEZES'} - {_fmt_relativo(ult)}",
                      "hora": ult.astimezone(TZ).strftime("%H:%M"), "data": _fmt_data(ult), "_u": ult})
    itens.sort(key=lambda i: (-i["total"], -i["_u"].timestamp()))
    for i in itens:
        del i["_u"]
    metade = (len(itens) + 1) // 2  # topo = mais acionados; resto (invertido) = menos acionados
    return {"total": len(registros), "mais": itens[:metade][:limite], "menos": list(reversed(itens[metade:]))[:limite]}


def desempenho(registros: list[dict], periodo: str) -> dict:
    locais = [(a["_dt"].astimezone(TZ), a["botao_nome"], a["categoria_nome"]) for a in registros]
    agora = datetime.now(TZ)
    if periodo == "dia":
        c = Counter(l[0].hour for l in locais)
        serie, dias = [{"name": f"{h:02d}h", "valor": c.get(h, 0)} for h in range(24)], 1
    elif periodo in ("semana", "mes"):
        n = 7 if periodo == "semana" else 30
        c = Counter(l[0].date() for l in locais)
        lista = [(agora - timedelta(days=i)).date() for i in range(n - 1, -1, -1)]
        serie = [{"name": DIAS[d.weekday()] if n == 7 else d.strftime("%d/%m"), "valor": c.get(d, 0)} for d in lista]
        dias = n
    else:
        c = Counter(l[0].strftime("%Y-%m") for l in locais)
        serie = [{"name": f"{k[5:]}/{k[:4]}", "valor": v} for k, v in sorted(c.items())]
        dias = max(1, (agora.date() - min(l[0] for l in locais).date()).days + 1) if locais else 1
    total = len(locais)
    return {"periodo": periodo, "total": total, "tem_dados": total > 0, "media_por_dia": round(total / dias, 2),
            "serie": serie,
            "por_categoria": [{"name": n, "valor": v} for n, v in Counter(l[2] for l in locais).most_common()],
            "top_botoes": [{"name": n, "valor": v} for n, v in Counter(l[1] for l in locais).most_common(5)]}

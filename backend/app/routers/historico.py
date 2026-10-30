"""Histórico (mais/menos acionados), desempenho (gráfico + PDF)."""
import uuid
from typing import Literal

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from .. import metricas
from ..deps import erro, get_db, usuario_atual
from ..relatorio import gerar_pdf
from ..schemas import AcionamentoApp
from ..util import agora_iso

Periodo = Literal["dia", "semana", "mes", "todos"]
router = APIRouter(tags=["Histórico e desempenho"])


@router.get("/historico", summary="Botões mais e menos acionados (tela Histórico)")
def historico(periodo: Periodo = "todos", busca: str | None = None, dispositivo: str | None = Query(None, description="MAC"),
              limite: int = Query(10, ge=1, le=50), u=Depends(usuario_atual), db=Depends(get_db)):
    regs = metricas.carregar(db, u["uid"], periodo, dispositivo, busca)
    r = metricas.ranking(regs, limite)
    return {"periodo": periodo, "total_acionamentos": r["total"], "tem_dados": r["total"] > 0,
            "mais_acionados": r["mais"], "menos_acionados": r["menos"]}


@router.post("/historico/acionamentos", status_code=201, summary="Registra o toque de um pictograma feito no app")
def registrar_do_app(dados: AcionamentoApp, u=Depends(usuario_atual), db=Depends(get_db)):
    for s in db.collection("usuarios").document(u["uid"]).collection("categorias").stream():
        cat = s.to_dict()
        for b in cat.get("botoes", []):
            if b["id"] == dados.botao_id:
                doc = {"botao_id": b["id"], "botao_nome": b["rotulo"], "categoria_nome": cat["nome"],
                       "dispositivo": None, "origem": "app", "acionado_em": agora_iso()}
                metricas.colecao(db, u["uid"]).document(uuid.uuid4().hex[:16]).set(doc)
                return doc
    raise erro(404, "nao_encontrado", "Botão não encontrado.")


@router.delete("/historico", summary="Apaga TODO o histórico de uso")
def limpar_tudo(u=Depends(usuario_atual), db=Depends(get_db)):
    n = 0
    for s in list(metricas.colecao(db, u["uid"]).stream()):
        s.reference.delete()
        n += 1
    return {"mensagem": f"{n} registro(s) removido(s)."}


@router.delete("/historico/{item_id}", summary="Remove o histórico de um botão (use o 'id' do item do ranking)")
def remover_item(item_id: str, u=Depends(usuario_atual), db=Depends(get_db)):
    alvo = [s for s in metricas.colecao(db, u["uid"]).stream()
            if metricas.id_item(s.to_dict()["botao_nome"], s.to_dict()["categoria_nome"]) == item_id]
    if not alvo:
        raise erro(404, "nao_encontrado", "Registro não encontrado.")
    for s in alvo:
        s.reference.delete()
    return {"mensagem": f"{len(alvo)} registro(s) removido(s)."}


@router.get("/desempenho", summary="Série para o gráfico de linhas (name/valor)")
def desempenho(periodo: Periodo = "semana", dispositivo: str | None = None, u=Depends(usuario_atual), db=Depends(get_db)):
    return metricas.desempenho(metricas.carregar(db, u["uid"], periodo, dispositivo), periodo)


@router.get("/desempenho/relatorio", summary="Relatório em PDF (botão 'Gerar PDF')")
def relatorio(periodo: Periodo = "semana", dispositivo: str | None = None, u=Depends(usuario_atual), db=Depends(get_db)):
    snap = db.collection("usuarios").document(u["uid"]).get()
    nome = (snap.to_dict().get("nome") if snap.exists else None) or u["email"] or "Responsável"
    pdf = gerar_pdf(nome, periodo, metricas.desempenho(metricas.carregar(db, u["uid"], periodo, dispositivo), periodo))
    return Response(pdf, media_type="application/pdf",
                    headers={"Content-Disposition": f'attachment; filename="relatorio-casa-{periodo}.pdf"'})

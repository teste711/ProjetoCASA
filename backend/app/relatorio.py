"""Relatório de desempenho em PDF (botão 'Gerar PDF')."""
import io
from datetime import datetime

from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.shapes import Drawing
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

from .metricas import TZ

ROTULO = {"dia": "Hoje", "semana": "Últimos 7 dias", "mes": "Últimos 30 dias", "todos": "Todo o período"}


def _tabela(linhas, larguras):
    t = Table(linhas, colWidths=larguras, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#5F7DE3")), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"), ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#CBD5E1")), ("ALIGN", (1, 0), (-1, -1), "CENTER")]))
    return t


def gerar_pdf(nome: str, periodo: str, d: dict) -> bytes:
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, title="Relatório de Desempenho — C.A.S.A.",
                            leftMargin=2 * cm, rightMargin=2 * cm, topMargin=2 * cm, bottomMargin=2 * cm)
    st = getSampleStyleSheet()
    el = [Paragraph("Projeto C.A.S.A. — Relatório de Desempenho", st["Title"]),
          Paragraph(f"Responsável: {nome}<br/>Período: {ROTULO.get(periodo, periodo)}<br/>"
                    f"Gerado em: {datetime.now(TZ).strftime('%d/%m/%Y %H:%M')}", st["Normal"]), Spacer(1, 0.5 * cm),
          Paragraph(f"Total de acionamentos: <b>{d['total']}</b> &nbsp;·&nbsp; Média por dia: <b>{d['media_por_dia']}</b>",
                    st["Normal"]), Spacer(1, 0.4 * cm)]
    if not d["tem_dados"]:
        el.append(Paragraph("Sem acionamentos registrados no período selecionado.", st["Italic"]))
    else:
        serie, desenho, g = d["serie"], Drawing(480, 200), VerticalBarChart()
        g.x, g.y, g.width, g.height = 30, 30, 430, 150
        g.data = [[p["valor"] for p in serie]]
        g.categoryAxis.categoryNames = [p["name"] for p in serie]
        longa = len(serie) > 12
        g.categoryAxis.labels.fontSize, g.categoryAxis.labels.angle = (6, 45) if longa else (8, 0)
        g.categoryAxis.labels.boxAnchor = "ne" if longa else "n"
        g.valueAxis.valueMin, g.valueAxis.labels.fontSize = 0, 8
        g.bars[0].fillColor = colors.HexColor("#F97316")
        desenho.add(g)
        el += [Paragraph("Acionamentos ao longo do tempo", st["Heading3"]), desenho]
        for titulo, chave, rot in (("Botões mais acionados", "top_botoes", "Botão"), ("Uso por categoria", "por_categoria", "Categoria")):
            if d[chave]:
                el += [Paragraph(titulo, st["Heading3"]),
                       _tabela([[rot, "Acionamentos"]] + [[p["name"], p["valor"]] for p in d[chave]], [10 * cm, 4 * cm])]
    el += [Spacer(1, 0.8 * cm), Paragraph("Este relatório descreve apenas a frequência de uso dos botões. "
                                          "Não constitui avaliação clínica ou terapêutica.", st["Italic"])]
    doc.build(el)
    return buf.getvalue()

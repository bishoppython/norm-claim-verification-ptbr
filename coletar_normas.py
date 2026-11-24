"""Coleta reprodutível das normas públicas usadas no benchmark.

Fontes oficiais apenas:
- BCB: API pública que alimenta https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo
- Planalto: páginas de leis em planalto.gov.br

Para cada norma grava fontes/<id>.json (metadados + texto limpo) e um
fontes/inventario.csv com URL, data de acesso, status e hash do texto.
Uso: python3 coletar_normas.py
"""
import csv, datetime, hashlib, html, json, re, sys, time, urllib.parse, urllib.request
from pathlib import Path

AQUI = Path(__file__).parent
SAIDA = AQUI / "fontes"
UA = {"User-Agent": "Mozilla/5.0 (pesquisa academica; coleta de normas publicas)"}

# (id, origem, tipo/url, numero, produto, papel)
NORMAS = [
    ("cmn-3919-2010", "bcb", "Resolução", "3919", "conta;cartao", "tarifas e serviços essenciais"),
    ("cmn-4753-2019", "bcb", "Resolução", "4753", "conta", "abertura, manutenção e encerramento de conta"),
    ("cmn-4881-2020", "bcb", "Resolução CMN", "4881", "consignado;cartao", "custo efetivo total (substitui a 3.517)"),
    ("cmn-4549-2017", "bcb", "Resolução", "4549", "cartao", "financiamento do saldo da fatura (rotativo)"),
    ("cmn-5112-2023", "bcb", "Resolução CMN", "5112", "cartao", "alterações da 4.549 (Lei 14.690)"),
    ("cmn-5057-2022", "bcb", "Resolução CMN", "5057", "consignado;cartao", "portabilidade de crédito (substitui a 4.292)"),
    ("bcb-96-2021", "bcb", "Resolução BCB", "96", "conta;cartao", "contas de pagamento e tarifas"),
    ("lei-8078-1990", "planalto", "https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm", "", "todos", "CDC"),
    ("lei-14181-2021", "planalto", "https://www.planalto.gov.br/ccivil_03/_ato2019-2022/2021/lei/l14181.htm", "", "consignado;cartao", "superendividamento"),
    ("lei-14690-2023", "planalto", "https://www.planalto.gov.br/ccivil_03/_ato2023-2026/2023/lei/l14690.htm", "", "cartao", "Desenrola; limite de juros do rotativo"),
    ("lei-10820-2003", "planalto", "https://www.planalto.gov.br/ccivil_03/leis/2003/l10.820.htm", "", "consignado", "consignado (margem)"),
    ("lei-13709-2018", "planalto", "https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709compilado.htm", "", "todos", "LGPD (dados pessoais no atendimento)"),
]

def baixar(url, tentativas=3):
    for i in range(tentativas):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=60) as r:
                return r.read()
        except Exception as e:  # noqa: BLE001
            erro = e
            time.sleep(2 * (i + 1))
    raise erro

def limpar(h):
    h = re.sub(r"(?is)<(script|style).*?</\1>", " ", h)
    h = re.sub(r"(?i)<br\s*/?>|</p>|</div>|</tr>|</li>", "\n", h)
    t = html.unescape(re.sub(r"<[^>]+>", " ", h))
    t = re.sub(r"[ \t\xa0]+", " ", t)
    return re.sub(r"\n\s*\n+", "\n\n", t).strip()

def coletar_bcb(tipo, numero):
    q = urllib.parse.urlencode({"p1": tipo, "p2": numero})
    api = f"https://www.bcb.gov.br/api/conteudo/app/normativos/exibenormativo?{q}"
    dados = json.loads(baixar(api))["conteudo"]
    if not dados:
        return None
    c = dados[0]
    texto = limpar(c.get("Texto") or "")
    pdf = None
    if c.get("Documentos"):
        # normas antigas trazem no HTML só o texto original; o vigente está no PDF
        # compilado mais recente (_L = versão limpa; _P = com histórico de redações)
        nomes = [x for x in c["Documentos"].replace("#", ";").split(";") if x.endswith(".pdf")]
        def chave(n):
            m = re.search(r"_v(\d+)_([A-Z])\.pdf$", n)
            return (int(m.group(1)), m.group(2) == "L") if m else (0, False)
        nomes = sorted((n for n in nomes if chave(n)[0] > 1), key=chave)
        if nomes:
            import subprocess, tempfile
            pdf = f"https://normativos.bcb.gov.br/Lists/Normativos/Attachments/{c['Id']}/{nomes[-1]}"
            with tempfile.NamedTemporaryFile(suffix=".pdf") as tmp:
                tmp.write(baixar(pdf)); tmp.flush()
                texto = subprocess.run(["pdftotext", "-layout", tmp.name, "-"],
                                       capture_output=True, text=True, check=True).stdout
    publica = "https://www.bcb.gov.br/estabilidadefinanceira/exibenormativo?" + urllib.parse.urlencode({"tipo": tipo, "numero": numero})
    return {
        "titulo": c.get("Titulo"), "data": c.get("DataTexto"), "assunto": c.get("Assunto"),
        "revogado": c.get("Revogado") == "True", "cancelado": c.get("Cancelado") == "True",
        "atualizacoes": [x.strip() for x in (c.get("Atualizacoes") or "").split(";#") if x.strip()],
        "texto": texto, "url_publica": publica, "url_api": api, "url_pdf_compilado": pdf,
    }

from html.parser import HTMLParser

VAZIAS = {"br", "img", "hr", "meta", "link", "input", "col", "area", "base", "wbr"}


class _SemTachado(HTMLParser):
    """Remove do HTML do Planalto o texto revogado, que a página mostra tachado
    (<strike>, <s>, <del> ou style com line-through). Sem isso, a extração
    mistura redações antigas e vigentes do mesmo artigo."""

    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.saida, self.pilha, self.tachado = [], [], 0

    @staticmethod
    def _eh_tachado(tag, attrs):
        if tag in ("strike", "s", "del"):
            return True
        estilo = dict(attrs).get("style") or ""
        return "line-through" in estilo.replace(" ", "").lower()

    def handle_starttag(self, tag, attrs):
        if tag in VAZIAS:
            if not self.tachado:
                self.saida.append(self.get_starttag_text())
            return
        t = self._eh_tachado(tag, attrs)
        self.pilha.append((tag, t))
        if t:
            self.tachado += 1
        elif not self.tachado:
            self.saida.append(self.get_starttag_text())

    def handle_endtag(self, tag):
        if tag in VAZIAS:
            return
        # fecha até a tag correspondente (HTML do Planalto nem sempre é bem formado)
        for i in range(len(self.pilha) - 1, -1, -1):
            if self.pilha[i][0] == tag:
                for _, t in self.pilha[i:]:
                    if t:
                        self.tachado -= 1
                del self.pilha[i:]
                if not self.tachado:
                    self.saida.append(f"</{tag}>")
                return

    def handle_data(self, d):
        if not self.tachado:
            self.saida.append(d)

    def handle_entityref(self, n):
        if not self.tachado:
            self.saida.append(f"&{n};")

    def handle_charref(self, n):
        if not self.tachado:
            self.saida.append(f"&#{n};")


def sem_tachado(h):
    p = _SemTachado()
    p.feed(h)
    p.close()
    return "".join(p.saida)


def coletar_planalto(url):
    bruto = baixar(url)
    for cod in ("utf-8", "cp1252", "latin-1"):
        try:
            h = bruto.decode(cod); break
        except UnicodeDecodeError:
            continue
    texto = limpar(sem_tachado(h))
    return {"titulo": texto[:120], "revogado": None, "tachado_removido": True, "texto": texto, "url_publica": url, "url_api": url}

def main():
    SAIDA.mkdir(exist_ok=True)
    hoje = datetime.date.today().isoformat()
    # uso: python coletar_normas.py [id ...]  -> coleta só os ids pedidos e
    # preserva as demais linhas do inventário
    so = set(sys.argv[1:])
    linhas = []
    inv = SAIDA / "inventario.csv"
    antigas = {}
    if so and inv.exists():
        with open(inv, encoding="utf-8") as f:
            antigas = {r["id"]: r for r in csv.DictReader(f)}
    for id_, origem, ref, num, produto, papel in NORMAS:
        if so and id_ not in so:
            if id_ in antigas:
                linhas.append(antigas[id_])
            continue
        try:
            reg = coletar_bcb(ref, num) if origem == "bcb" else coletar_planalto(ref)
        except Exception as e:  # noqa: BLE001
            reg, status = None, f"erro: {e}"
        else:
            status = "ok" if reg and reg["texto"] else "vazio"
        if reg:
            reg.update({"id": id_, "produto": produto, "papel": papel, "acesso": hoje})
            (SAIDA / f"{id_}.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
        h = hashlib.sha256(reg["texto"].encode()).hexdigest()[:16] if reg else ""
        linhas.append({"id": id_, "papel": papel, "produto": produto, "status_coleta": status,
                       "revogado": reg.get("revogado") if reg else "", "caracteres": len(reg["texto"]) if reg else 0,
                       "url": reg["url_publica"] if reg else ref, "acesso": hoje, "sha256_16": h})
        print(f"{id_:18} {status:8} revogado={linhas[-1]['revogado']} chars={linhas[-1]['caracteres']}")
        time.sleep(1)
    with open(SAIDA / "inventario.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0])); w.writeheader(); w.writerows(linhas)
    return 0

if __name__ == "__main__":
    sys.exit(main())

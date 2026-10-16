"""Firestore e Firebase Auth falsos (em memória) para testar sem credenciais."""
import copy


class Snap:
    def __init__(self, ref, data):
        self.reference, self.id, self._d = ref, ref.id, data
        self.exists = data is not None

    def to_dict(self):
        return copy.deepcopy(self._d)


class DocRef:
    def __init__(self, db, path):
        self.db, self.path, self.id = db, path, path[-1]

    def get(self):
        return Snap(self, self.db.data.get(self.path))

    def set(self, data, merge=False):
        self.db.data[self.path] = {**self.db.data.get(self.path, {}), **copy.deepcopy(data)} if merge else copy.deepcopy(data)

    def update(self, campos):
        if self.path not in self.db.data:
            raise KeyError("documento inexistente")
        self.db.data[self.path].update(copy.deepcopy(campos))

    def delete(self):
        self.db.data.pop(self.path, None)

    def collection(self, nome):
        return ColRef(self.db, self.path + (nome,))


class ColRef:
    def __init__(self, db, path, filtros=()):
        self.db, self.path, self.filtros = db, path, filtros

    def document(self, id):
        return DocRef(self.db, self.path + (id,))

    def where(self, filter):
        assert filter.op_string == "=="
        return ColRef(self.db, self.path, self.filtros + ((filter.field_path, filter.value),))

    def stream(self):
        n = len(self.path)
        for p, d in list(self.db.data.items()):
            if len(p) == n + 1 and p[:n] == self.path and all(d.get(c) == v for c, v in self.filtros):
                yield Snap(DocRef(self.db, p), d)


class FakeFirestore:
    def __init__(self):
        self.data = {}

    def collection(self, nome):
        return ColRef(self, (nome,))

    def recursive_delete(self, ref):
        for p in [p for p in self.data if p[:len(ref.path)] == ref.path]:
            del self.data[p]


class FakeAuth:
    """Tokens de teste: 'tok:<uid>:<email>:<verificado 1/0>'."""
    def __init__(self):
        self.apagados, self.usuarios = [], {}   # usuarios: email -> dict(uid, nome, email_verified)

    def verify(self, token):
        partes = token.split(":")
        if len(partes) != 4 or partes[0] != "tok":
            raise ValueError("token inválido")
        claims = {"uid": partes[1], "email": partes[2], "email_verified": partes[3] == "1"}
        if partes[2] in self.usuarios:  # o Firebase real inclui o displayName no token ("name")
            claims["name"] = self.usuarios[partes[2]]["nome"]
        return claims

    def email_existe(self, email):
        return email in self.usuarios

    def create_user(self, email, senha, nome):
        from app.firebase import EmailJaExiste
        if email in self.usuarios:
            raise EmailJaExiste()
        uid = f"uid_{len(self.usuarios) + 1}"
        self.usuarios[email] = {"uid": uid, "nome": nome, "senha": senha, "email_verified": True}
        return uid

    def delete_user(self, uid):
        self.apagados.append(uid)

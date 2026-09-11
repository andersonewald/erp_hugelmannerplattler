# controllers/danca_controller.py
from config.database import get_db
from models.models import Danca

class DancaController:
    @staticmethod
    def listar_dancas(filtro=""):
        db = get_db()
        try:
            query = db.query(Danca).filter(Danca.ativo == True)
            if filtro:
                termo = f"%{filtro}%"
                query = query.filter(
                    (Danca.nome.ilike(termo)) | 
                    (Danca.origem.ilike(termo)) |
                    (Danca.interprete_compositor.ilike(termo))  # <--- Incluído no filtro de busca
                )
            return query.order_by(Danca.nome.asc()).all()
        finally:
            db.close()

    @staticmethod
    def buscar_por_id(danca_id: int):
        db = get_db()
        try:
            return db.query(Danca).filter(Danca.id == danca_id).first()
        finally:
            db.close()

    @staticmethod
    def salvar_danca(dados: dict, danca_id: int = None):
        db = get_db()
        try:
            nome = dados.get("nome", "").strip()
            if not nome:
                return False, "O campo 'Nome da Dança' é obrigatório!"

            if danca_id:
                danca = db.query(Danca).filter(Danca.id == danca_id).first()
                if not danca:
                    return False, "Dança não encontrada para atualização!"
            else:
                danca = Danca()
                db.add(danca)

            danca.nome = nome
            danca.origem = dados.get("origem")
            danca.tempo_musica = dados.get("tempo_musica")
            danca.interprete_compositor = dados.get("interprete_compositor")  # <--- Salvando o novo campo
            danca.detalhamento_historico = dados.get("detalhamento_historico")

            db.commit()
            msg = "Dança atualizada com sucesso!" if danca_id else "Dança cadastrada com sucesso!"
            return True, msg

        except Exception as e:
            db.rollback()
            return False, f"Erro ao salvar dança: {str(e)}"
        finally:
            db.close()
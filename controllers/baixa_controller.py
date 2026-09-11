# controllers/baixa_controller.py
from datetime import datetime
from config.database import get_db
from models.models import BaixaBem, BemMaterial

class BaixaController:
    @staticmethod
    def listar_baixas():
        """Retorna o histórico de baixas realizadas."""
        db = get_db()
        try:
            baixas = db.query(BaixaBem).order_by(BaixaBem.data_baixa.desc()).all()
            resultado = []
            for b in baixas:
                resultado.append({
                    "id": b.id,
                    "bem": b.bem.nome if b.bem else "N/A",
                    "codigo": b.bem.codigo_patrimonio if b.bem else "N/A",
                    "qtd": b.quantidade,
                    "motivo": b.motivo,
                    "data": b.data_baixa.strftime("%d/%m/%Y %H:%M") if b.data_baixa else "",
                    "obs": b.observacao or ""
                })
            return resultado
        finally:
            db.close()

    @staticmethod
    def registrar_baixa(bem_id, quantidade, motivo, obs=""):
        """Efetua a baixa de um item e abate no estoque total e disponível."""
        db = get_db()
        try:
            bem = db.query(BemMaterial).get(bem_id)
            if not bem:
                return False, "Material não encontrado!"

            if bem.quantidade_disponivel < quantidade:
                return False, f"Não é possível dar baixa nessa quantidade! Disponível: {bem.quantidade_disponivel}"

            # Abate do estoque total e disponível
            bem.quantidade_total -= quantidade
            bem.quantidade_disponivel -= quantidade

            baixa = BaixaBem(
                bem_id=bem_id,
                quantidade=quantidade,
                motivo=motivo,
                observacao=obs,
                data_baixa=datetime.now()
            )
            db.add(baixa)
            db.commit()

            return True, "Baixa de patrimônio concluída com sucesso!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao dar baixa: {str(e)}"
        finally:
            db.close()
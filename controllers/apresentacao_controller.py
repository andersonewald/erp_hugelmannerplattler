# controllers/apresentacao_controller.py
from datetime import datetime
from sqlalchemy.orm import joinedload
from config.database import get_db
from models.models import Apresentacao, ApresentacaoDanca, ApresentacaoIntegrante, Danca, Pessoa

class ApresentacaoController:
    @staticmethod
    def listar_apresentacoes():
        """Retorna todas as apresentações trazendo suas danças de forma antecipada (eager loading)."""
        db = get_db()
        try:
            return db.query(Apresentacao)\
                     .options(joinedload(Apresentacao.dancas_escaladas))\
                     .order_by(Apresentacao.data_evento.desc())\
                     .all()
        finally:
            db.close()

    @staticmethod
    def buscar_por_id(apresentacao_id: int):
        db = get_db()
        try:
            return db.query(Apresentacao)\
                     .options(joinedload(Apresentacao.dancas_escaladas))\
                     .filter(Apresentacao.id == apresentacao_id)\
                     .first()
        finally:
            db.close()

    @staticmethod
    def buscar_detalhes_completos(apresentacao_id: int):
        """Retorna uma estrutura pronta com danças e nomes de integrantes para edição ou visualização."""
        db = get_db()
        try:
            aprs = db.query(Apresentacao)\
                     .options(
                         joinedload(Apresentacao.dancas_escaladas)
                         .joinedload(ApresentacaoDanca.integrantes)
                     )\
                     .filter(Apresentacao.id == apresentacao_id)\
                     .first()
            
            if not aprs:
                return None

            repertorio = []
            dancas_ordenadas = sorted(aprs.dancas_escaladas, key=lambda x: x.ordem_execucao)

            for ad in dancas_ordenadas:
                danca = db.query(Danca).filter(Danca.id == ad.danca_id).first()
                integrantes_ids = []
                integrantes_nomes = []

                for ai in ad.integrantes:
                    p = db.query(Pessoa).filter(Pessoa.id == ai.pessoa_id).first()
                    if p:
                        integrantes_ids.append(p.id)
                        integrantes_nomes.append(p.nome)

                repertorio.append({
                    "danca_id": danca.id if danca else ad.danca_id,
                    "nome_danca": danca.nome if danca else "Dança Indefinida",
                    "ordem": ad.ordem_execucao,
                    "integrantes_ids": integrantes_ids,
                    "integrantes_nomes": integrantes_nomes
                })

            return {
                "id": aprs.id,
                "nome_evento": aprs.nome_evento,
                "data_evento": aprs.data_evento,
                "local_evento": aprs.local_evento,
                "observacoes": aprs.observacoes,
                "repertorio": repertorio
            }
        finally:
            db.close()

    @staticmethod
    def salvar_apresentacao(dados_evento: dict, repertorio_escalado: list, apresentacao_id: int = None):
        db = get_db()
        try:
            if not dados_evento.get("nome_evento") or not dados_evento.get("local_evento"):
                return False, "Nome do Evento e Local são obrigatórios!"

            dt_evento = datetime.strptime(dados_evento["data_evento"], "%d/%m/%Y").date()

            if apresentacao_id:
                aprs = db.query(Apresentacao).filter(Apresentacao.id == apresentacao_id).first()
                if not aprs:
                    return False, "Apresentação não encontrada!"
                # Remove itens antigos para regravar a nova escala
                db.query(ApresentacaoDanca).filter(ApresentacaoDanca.apresentacao_id == apresentacao_id).delete()
            else:
                aprs = Apresentacao()
                db.add(aprs)

            aprs.nome_evento = dados_evento["nome_evento"]
            aprs.data_evento = dt_evento
            aprs.local_evento = dados_evento["local_evento"]
            aprs.observacoes = dados_evento.get("observacoes", "")

            db.flush()

            for item in repertorio_escalado:
                ad = ApresentacaoDanca(
                    apresentacao_id=aprs.id,
                    danca_id=item["danca_id"],
                    ordem_execucao=item["ordem"]
                )
                db.add(ad)
                db.flush()

                for p_id in item["integrantes_ids"]:
                    ai = ApresentacaoIntegrante(
                        apresentacao_danca_id=ad.id,
                        pessoa_id=p_id
                    )
                    db.add(ai)

            db.commit()
            return True, aprs.id
        except Exception as e:
            db.rollback()
            return False, f"Erro ao salvar apresentação: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def excluir_apresentacao(apresentacao_id: int):
        db = get_db()
        try:
            aprs = db.query(Apresentacao).filter(Apresentacao.id == apresentacao_id).first()
            if aprs:
                db.delete(aprs)
                db.commit()
                return True, "Apresentação excluída com sucesso!"
            return False, "Registro não encontrado."
        except Exception as e:
            db.rollback()
            return False, f"Erro ao excluir apresentação: {str(e)}"
        finally:
            db.close()
# controllers/estoque_controller.py
from config.database import get_db
from models.models import BemMaterial, EmprestimoItem, BaixaBem
from sqlalchemy import or_

class EstoqueController:
    @staticmethod
    def obter_posicao_estoque(filtro=""):
        """Retorna os dados consolidados do estoque para a EstoqueView."""
        db = get_db()
        try:
            query = db.query(BemMaterial)

            # Aplica busca por Filtro se houver texto
            if filtro:
                termo = f"%{filtro}%"
                query = query.filter(
                    or_(
                        BemMaterial.nome.ilike(termo),
                        BemMaterial.codigo_patrimonio.ilike(termo),
                        BemMaterial.categoria.ilike(termo)
                    )
                )

            bens = query.all()
            posicao = []

            for bem in bens:
                # Se o bem está marcado como Baixado, ignoramos ou tratamos
                is_baixado = (bem.status == "Baixado")
                
                # Regra para bens patrimoniais individuais:
                total = 0 if is_baixado else 1
                emprestado = 1 if bem.status == "Emprestado" else 0
                disponivel = 1 if bem.status == "Disponível" else 0

                posicao.append({
                    "id": bem.id,
                    "codigo": bem.codigo_patrimonio,
                    "nome": bem.nome,
                    "categoria": bem.categoria,
                    "total": total,
                    "emprestado": emprestado,
                    "disponivel": disponivel,
                    "estado": bem.estado_conservacao if not is_baixado else "Baixado/Inativo"
                })

            return posicao
        except Exception as e:
            print(f"Erro ao consultar estoque: {e}")
            return []
        finally:
            db.close()
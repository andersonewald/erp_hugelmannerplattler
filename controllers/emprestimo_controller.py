# controllers/emprestimo_controller.py
from datetime import datetime
from config.database import get_db
from models.models import Emprestimo, EmprestimoItem, BemMaterial, Pessoa

class EmprestimoController:
    @staticmethod
    def listar_emprestimos(status_filtro="Aberto"):
        """Retorna os empréstimos cadastrados com filtro de status."""
        db = get_db()
        try:
            query = db.query(Emprestimo)
            if status_filtro != "Todos":
                query = query.filter(Emprestimo.status == status_filtro)
            
            emprestimos = query.order_by(Emprestimo.data_emprestimo.desc()).all()
            
            resultado = []
            for emp in emprestimos:
                # Formata a lista de bens vinculados
                itens_str = ", ".join([
                    f"{i.bem.nome} [{i.bem.codigo_patrimonio}]" 
                    for i in emp.itens if i.bem
                ])
                resultado.append({
                    "id": emp.id,
                    "pessoa": emp.pessoa.nome if emp.pessoa else "N/A",
                    "data": emp.data_emprestimo.strftime("%d/%m/%Y %H:%M") if emp.data_emprestimo else "",
                    "previsao": emp.data_previsao_devolucao.strftime("%d/%m/%Y") if emp.data_previsao_devolucao else "",
                    "status": emp.status,
                    "itens": itens_str
                })
            return resultado
        finally:
            db.close()

    @staticmethod
    def registrar_emprestimo(pessoa_id, bem_id, data_previsao_str, obs=""):
        """Registra um novo empréstimo de um item patrimonial para uma pessoa."""
        db = get_db()
        try:
            bem = db.query(BemMaterial).get(bem_id)
            if not bem:
                return False, "Material selecionado não foi encontrado!"

            if bem.status != "Disponível":
                return False, f"O item '{bem.nome}' ({bem.codigo_patrimonio}) já está com status: '{bem.status}'!"

            # Converte a data da previsão
            data_prev = datetime.strptime(data_previsao_str, "%d/%m/%Y")

            emp = Emprestimo(
                pessoa_id=pessoa_id,
                data_emprestimo=datetime.now(),
                data_previsao_devolucao=data_prev,
                status="Aberto",
                observacao=obs
            )
            db.add(emp)
            db.flush()  # Gera o ID do empréstimo

            # Adiciona o item ao empréstimo (quantidade fixa de 1 por item individual)
            item = EmprestimoItem(
                emprestimo_id=emp.id,
                bem_id=bem_id,
                quantidade=1
            )
            db.add(item)

            # Atualiza o status do bem para "Emprestado"
            bem.status = "Emprestado"

            db.commit()
            return True, "Empréstimo registrado com sucesso!"
            
        except Exception as e:
            db.rollback()
            return False, f"Erro ao registrar empréstimo: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def devolver_emprestimo(emprestimo_id):
        """Devolve os itens emprestados e restabelece seus status para 'Disponível'."""
        db = get_db()
        try:
            emp = db.query(Emprestimo).get(emprestimo_id)
            if not emp or emp.status == "Devolvido":
                return False, "Empréstimo já devolvido ou inválido!"

            # Retorna o status de cada bem vinculado para Disponível
            for item in emp.itens:
                if item.bem:
                    item.bem.status = "Disponível"

            emp.status = "Devolvido"
            emp.data_devolucao = datetime.now()

            db.commit()
            return True, "Devolução realizada com sucesso!"
            
        except Exception as e:
            db.rollback()
            return False, f"Erro na devolução: {str(e)}"
        finally:
            db.close()
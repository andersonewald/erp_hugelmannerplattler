# controllers/bem_controller.py
import re
from sqlalchemy.orm import joinedload
from config.database import get_db
from models.models import BemMaterial, FotoBemMaterial

class BemController:
    @staticmethod
    def listar_todos(filtro=""):
        """Retorna todos os bens cadastrados individualmente trazendo as fotos de forma otimizada."""
        db = get_db()
        try:
            query = db.query(BemMaterial)
            if filtro:
                filtro_limpo = f"%{filtro.strip()}%"
                query = query.filter(
                    BemMaterial.nome.ilike(filtro_limpo) | 
                    BemMaterial.codigo_patrimonio.ilike(filtro_limpo) |
                    BemMaterial.categoria.ilike(filtro_limpo)
                )
            return query.order_by(BemMaterial.codigo_patrimonio).all()
        finally:
            db.close()

    @staticmethod
    def _obter_ultimo_numero_sequencial(db, prefixo="PAT-"):
        """Obtém o maior valor numérico associado ao prefixo no banco."""
        bens = db.query(BemMaterial.codigo_patrimonio).filter(
            BemMaterial.codigo_patrimonio.like(f"{prefixo}%")
        ).all()

        max_num = 0
        for (codigo,) in bens:
            num_part = codigo.replace(prefixo, "")
            if num_part.isdigit():
                max_num = max(max_num, int(num_part))
        
        return max_num

    @staticmethod
    def cadastrar_lote(nome, descricao, categoria, quantidade, valor_unitario, estado, prefixo="PAT-", fotos=None):
        """Gera N itens individuais de patrimônio e anexa as fotos enviadas."""
        if not nome or not nome.strip():
            return False, "O Nome do Material/Bem é obrigatório!"
        if quantidade <= 0:
            return False, "A quantidade de entrada deve ser maior que zero!"

        db = get_db()
        try:
            ultimo_num = BemController._obter_ultimo_numero_sequencial(db, prefixo)
            novos_itens = []

            for i in range(1, quantidade + 1):
                proximo_num = ultimo_num + i
                cod_patrimonio = f"{prefixo}{proximo_num:04d}"
                
                bem = BemMaterial(
                    codigo_patrimonio=cod_patrimonio,
                    nome=nome.strip(),
                    descricao=descricao.strip() if descricao else "",
                    categoria=categoria.strip() if categoria else "",
                    valor_estimado=valor_unitario,
                    estado_conservacao=estado.strip() if estado else "",
                    status="Disponível"
                )

                # Anexa as fotos se enviadas no cadastro em lote
                if fotos:
                    for foto_bytes, mimetype in fotos:
                        nova_foto = FotoBemMaterial(
                            foto_blob=foto_bytes,
                            mimetype=mimetype
                        )
                        bem.fotos.append(nova_foto)

                db.add(bem)
                novos_itens.append(cod_patrimonio)

            db.commit()
            return True, f"Sucesso! Foram gerados {len(novos_itens)} itens ({novos_itens[0]} até {novos_itens[-1]})."
        except Exception as e:
            db.rollback()
            return False, f"Erro ao gerar patrimônios: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def salvar_edicao(id_bem, estado, descricao, valor, fotos=None):
        """Atualiza dados de um item específico e adiciona novas fotos."""
        db = get_db()
        try:
            bem = db.get(BemMaterial, id_bem) if hasattr(db, 'get') else db.query(BemMaterial).get(id_bem)
            
            if not bem:
                return False, "Item não encontrado!"

            bem.estado_conservacao = estado.strip() if estado else ""
            bem.descricao = descricao.strip() if descricao else ""
            bem.valor_estimado = valor

            # Adiciona novas fotos se enviadas na edição
            if fotos:
                for foto_bytes, mimetype in fotos:
                    nova_foto = FotoBemMaterial(
                        bem_id=bem.id,
                        foto_blob=foto_bytes,
                        mimetype=mimetype
                    )
                    db.add(nova_foto)
            
            db.commit()
            return True, "Item atualizado com sucesso!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao atualizar: {str(e)}"
        finally:
            db.close()

    @staticmethod
    def excluir(id_bem):
        """Exclui o item individual do patrimônio e suas fotos em cascata."""
        db = get_db()
        try:
            bem = db.get(BemMaterial, id_bem) if hasattr(db, 'get') else db.query(BemMaterial).get(id_bem)
            
            if not bem:
                return False, "Item não encontrado!"

            if bem.status != "Disponível":
                return False, f"Não é possível excluir: o item está '{bem.status}'!"

            db.delete(bem)
            db.commit()
            return True, "Item excluído com sucesso!"
        except Exception as e:
            db.rollback()
            return False, f"Erro ao excluir: {str(e)}"
        finally:
            db.close()
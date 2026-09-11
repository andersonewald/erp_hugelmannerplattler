# utils/pdf_generator.py
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from sqlalchemy.orm import joinedload
from config.database import get_db
from models.models import Apresentacao, ApresentacaoDanca, Pessoa, Danca
from controllers.pessoa_controller import PessoaController


class RelatorioApresentacaoPDF:
    @staticmethod
    def gerar_pdf(apresentacao_id: int, caminho_saida: str):
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
                return False, "Apresentação não encontrada para geração do PDF."

            doc = SimpleDocTemplate(
                caminho_saida,
                pagesize=letter,
                rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
            )

            styles = getSampleStyleSheet()
            
            title_style = ParagraphStyle(
                'DocTitle',
                parent=styles['Heading1'],
                fontSize=20,
                leading=24,
                textColor=colors.HexColor('#1a2a3a'),
                alignment=1,
                spaceAfter=15
            )

            subtitle_style = ParagraphStyle(
                'SubTitle',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,
                textColor=colors.HexColor('#333333'),
            )

            dance_title = ParagraphStyle(
                'DanceTitle',
                parent=styles['Heading2'],
                fontSize=14,
                leading=18,
                textColor=colors.HexColor('#2c3e50'),
                spaceBefore=10,
                spaceAfter=5
            )

            body_style = ParagraphStyle(
                'Body',
                parent=styles['Normal'],
                fontSize=10,
                leading=14,
                textColor=colors.HexColor('#444444')
            )

            elements = []

            # Cabeçalho do Grupo e Evento
            elements.append(Paragraph("<b>GRUPO FOLCLÓRICO HUGELMANNERPLATTLER</b>", title_style))
            elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#27ae60'), spaceAfter=15))

            info_evento = [
                [Paragraph(f"<b>Evento:</b> {aprs.nome_evento}", subtitle_style),
                 Paragraph(f"<b>Data:</b> {aprs.data_evento.strftime('%d/%m/%Y')}", subtitle_style)],
                [Paragraph(f"<b>Local:</b> {aprs.local_evento}", subtitle_style),
                 Paragraph(f"<b>Observações:</b> {aprs.observacoes or 'Nenhuma'}", subtitle_style)]
            ]

            t_info = Table(info_evento, colWidths=[300, 240])
            t_info.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
                ('PADDING', (0,0), (-1,-1), 8),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dcdfe6')),
            ]))
            elements.append(t_info)
            elements.append(Spacer(1, 15))

            elements.append(Paragraph("<b>ROTEIRO E ESCALA DA APRESENTAÇÃO</b>", ParagraphStyle('Sec', fontSize=12, leading=14, textColor=colors.HexColor('#27ae60'))))
            elements.append(Spacer(1, 10))

            dancas_ordenadas = sorted(aprs.dancas_escaladas, key=lambda x: x.ordem_execucao)

            for idx, ad in enumerate(dancas_ordenadas, start=1):
                danca = db.query(Danca).filter(Danca.id == ad.danca_id).first()
                
                elements.append(Paragraph(f"{idx}. Dança: <b>{danca.nome if danca else 'N/A'}</b> (Origem: {danca.origem if danca and danca.origem else 'Não Inf.'})", dance_title))
                
                historico = danca.detalhamento_historico if danca and danca.detalhamento_historico else "Sem histórico cadastrado."
                elements.append(Paragraph(f"<b>Histórico / Detalhes:</b> {historico}", body_style))
                elements.append(Spacer(1, 6))

                integrantes_nomes = []
                for ai in ad.integrantes:
                    p = db.query(Pessoa).filter(Pessoa.id == ai.pessoa_id).first()
                    if p:
                        integrantes_nomes.append(p.nome)

                if integrantes_nomes:
                    # Tabela em Listagem Única (Uma Coluna)
                    t_data = [["Dançarinos Escalados"]]
                    for nome in integrantes_nomes:
                        t_data.append([f"• {nome}"])

                    t_dan = Table(t_data, colWidths=[540])
                    t_dan.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eaeded')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2c3e50')),
                        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                        ('FONTSIZE', (0,0), (-1,-1), 9),
                        ('PADDING', (0,0), (-1,-1), 5),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
                    ]))
                    elements.append(t_dan)
                else:
                    elements.append(Paragraph("<i>Nenhum integrante escalado para esta dança.</i>", body_style))

                elements.append(Spacer(1, 15))
                elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#bdc3c7')))

            doc.build(elements)
            return True, "Relatório PDF gerado com sucesso!"
        except Exception as e:
            return False, f"Erro ao gerar PDF: {str(e)}"
        finally:
            db.close()


class RelatorioPessoaPDF:
    @staticmethod
    def gerar_pdf(pessoa_id: int, caminho_saida: str):
        """Gera a ficha cadastral e currículo em PDF do integrante com histórico de apresentações."""
        dados = PessoaController.buscar_detalhes_completos(pessoa_id)
        if not dados:
            return False, "Integrante não encontrado para geração da ficha."

        pessoa = dados["pessoa"]
        historico = dados["historico"]

        try:
            doc = SimpleDocTemplate(
                caminho_saida,
                pagesize=letter,
                rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36
            )

            styles = getSampleStyleSheet()

            title_style = ParagraphStyle(
                'DocTitlePessoa',
                parent=styles['Heading1'],
                fontSize=18,
                leading=22,
                textColor=colors.HexColor('#1a2a3a'),
                alignment=1,
                spaceAfter=10
            )

            sec_style = ParagraphStyle(
                'SecPessoa',
                parent=styles['Heading2'],
                fontSize=12,
                leading=16,
                textColor=colors.HexColor('#27ae60'),
                spaceBefore=12,
                spaceAfter=6
            )

            body_style = ParagraphStyle(
                'BodyPessoa',
                parent=styles['Normal'],
                fontSize=9,
                leading=13,
                textColor=colors.HexColor('#333333')
            )

            elements = []

            # Cabeçalho do Grupo e Título
            elements.append(Paragraph("<b>GRUPO FOLCLÓRICO HUGELMANNERPLATTLER</b>", title_style))
            elements.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#27ae60'), spaceAfter=12))

            elements.append(Paragraph(f"<b>FICHA CADASTRAL DO INTEGRANTE</b>", ParagraphStyle('SubHeader', fontSize=13, leading=16, textColor=colors.HexColor('#2c3e50'), alignment=1)))
            elements.append(Spacer(1, 10))

            # 1. DADOS PESSOAIS E CONTROLE
            elements.append(Paragraph("<b>1. DADOS PESSOAIS E VÍNCULO</b>", sec_style))
            
            data_nasc_str = pessoa.data_nascimento.strftime('%d/%m/%Y') if pessoa.data_nascimento else "—"
            
            dados_pessoais = [
                [Paragraph(f"<b>Nome:</b> {pessoa.nome}", body_style), Paragraph(f"<b>Categoria:</b> {pessoa.categoria or '—'}", body_style)],
                [Paragraph(f"<b>Data de Nasc.:</b> {data_nasc_str}", body_style), Paragraph(f"<b>Gênero:</b> {pessoa.genero or '—'}", body_style)],
                [Paragraph(f"<b>CPF / RG:</b> {pessoa.cpf_rg or '—'}", body_style), Paragraph(f"<b>Telefone:</b> {pessoa.telefone or '—'}", body_style)],
                [Paragraph(f"<b>E-mail:</b> {pessoa.email or '—'}", body_style), Paragraph(f"<b>Status:</b> {pessoa.status or 'Ativo'}", body_style)],
                [Paragraph(f"<b>Mês/Ano Entrada:</b> {pessoa.mes_ano_entrada or '—'}", body_style), Paragraph(f"<b>Mês/Ano Saída:</b> {pessoa.mes_ano_saida or '—'}", body_style)],
            ]

            t_pessoais = Table(dados_pessoais, colWidths=[270, 270])
            t_pessoais.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#f8f9fa')),
                ('PADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dcdfe6')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#eaeded')),
            ]))
            elements.append(t_pessoais)
            elements.append(Spacer(1, 10))

            # 2. ENDEREÇO E SAÚDE
            elements.append(Paragraph("<b>2. ENDEREÇO E FICHA DE SAÚDE</b>", sec_style))
            
            plano_str = "Sim" if pessoa.possui_plano_saude else "Não"
            cidade_uf = f"{pessoa.cidade or '—'} / {pessoa.estado or '—'}"

            dados_saude = [
                [Paragraph(f"<b>Rua/Avenida:</b> {pessoa.rua or '—'}", body_style), Paragraph(f"<b>Cidade/UF:</b> {cidade_uf}", body_style)],
                [Paragraph(f"<b>Plano de Saúde:</b> {plano_str}", body_style), Paragraph(f"<b>Alergias/Restrições:</b> {pessoa.alergias or 'Nenhuma'}", body_style)],
                [Paragraph(f"<b>Contato Emergência:</b> {pessoa.contato_emergencia_nome or '—'}", body_style), Paragraph(f"<b>Tel. Emergência:</b> {pessoa.contato_emergencia_telefone or '—'}", body_style)],
            ]

            t_saude = Table(dados_saude, colWidths=[270, 270])
            t_saude.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#ffffff')),
                ('PADDING', (0,0), (-1,-1), 6),
                ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#dcdfe6')),
                ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#eaeded')),
            ]))
            elements.append(t_saude)
            elements.append(Spacer(1, 10))

            # 3. HISTÓRICO DE APRESENTAÇÕES
            elements.append(Paragraph("<b>3. HISTÓRICO DE APRESENTAÇÕES</b>", sec_style))

            if historico:
                t_hist_data = [[
                    Paragraph("<b>Data</b>", body_style),
                    Paragraph("<b>Evento</b>", body_style),
                    Paragraph("<b>Local</b>", body_style),
                    Paragraph("<b>Danças Executadas</b>", body_style)
                ]]

                for h in historico:
                    data_str = h["data_evento"].strftime('%d/%m/%Y') if h["data_evento"] else "—"
                    dancas_str = ", ".join(h["dancas"])
                    t_hist_data.append([
                        Paragraph(data_str, body_style),
                        Paragraph(h["nome_evento"], body_style),
                        Paragraph(h["local_evento"], body_style),
                        Paragraph(dancas_str, body_style)
                    ])

                t_hist = Table(t_hist_data, colWidths=[65, 150, 145, 180])
                t_hist.setStyle(TableStyle([
                    ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#eaeded')),
                    ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#2c3e50')),
                    ('PADDING', (0,0), (-1,-1), 5),
                    ('VALIGN', (0,0), (-1,-1), 'TOP'),
                    ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#bdc3c7')),
                ]))
                elements.append(t_hist)
            else:
                elements.append(Paragraph("<i>Nenhum registro de apresentação escalada encontrado para este integrante.</i>", body_style))

            doc.build(elements)
            return True, "Ficha cadastral gerada com sucesso!"

        except Exception as e:
            return False, f"Erro ao gerar ficha PDF: {str(e)}"
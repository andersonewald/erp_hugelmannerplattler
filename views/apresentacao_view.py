# views/apresentacao_view.py
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, 
    QHeaderView, QAbstractItemView, QMessageBox, QDateEdit, QListWidget,
    QListWidgetItem, QFileDialog, QTabWidget
)
from PyQt6.QtCore import Qt, QDate
from controllers.apresentacao_controller import ApresentacaoController
from controllers.danca_controller import DancaController
from controllers.pessoa_controller import PessoaController
from utils.pdf_generator import RelatorioApresentacaoPDF

class ApresentacaoView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.repertorio_temp = []
        self.apresentacao_id_edicao = None
        self._init_ui()
        self.carregar_combos_e_listas()
        self.carregar_historico_apresentacoes()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # -------------------------------------------------------------
        # ABA 1: NOVO EVENTO / EDICÃO DE ESCALA
        # -------------------------------------------------------------
        tab_cadastro = QWidget()
        lay_cad = QVBoxLayout(tab_cadastro)

        # 1. Informações do Evento
        box_evento = QGroupBox("1. Informações do Evento")
        lay_ev = QHBoxLayout()

        lay_ev.addWidget(QLabel("Nome do Evento:*"))
        self.txt_nome_evento = QLineEdit()
        self.txt_nome_evento.setPlaceholderText("Ex: Oktobertanz 2026")
        lay_ev.addWidget(self.txt_nome_evento)

        lay_ev.addWidget(QLabel("Data:*"))
        self.dt_evento = QDateEdit()
        self.dt_evento.setDisplayFormat("dd/MM/yyyy")
        self.dt_evento.setDate(QDate.currentDate())
        lay_ev.addWidget(self.dt_evento)

        lay_ev.addWidget(QLabel("Local / Cidade:*"))
        self.txt_local = QLineEdit()
        self.txt_local.setPlaceholderText("Ex: Pavilhão de Eventos - Treze Tílias")
        lay_ev.addWidget(self.txt_local)

        box_evento.setLayout(lay_ev)
        lay_cad.addWidget(box_evento)

        # 2. Escala de Danças e Integrantes
        box_montagem = QGroupBox("2. Escala de Danças e Integrantes")
        lay_montagem = QHBoxLayout()

        # Esquerda: Selecionar Dança
        v_danca = QVBoxLayout()
        v_danca.addWidget(QLabel("<b>a) Selecione a Dança:</b>"))
        self.lst_dancas = QListWidget()
        v_danca.addWidget(self.lst_dancas)
        
        # Direita: Selecionar Integrantes
        v_pess = QVBoxLayout()
        v_pess.addWidget(QLabel("<b>b) Marque os Integrantes Escalados:</b>"))
        self.lst_pessoas = QListWidget()
        v_pess.addWidget(self.lst_pessoas)

        lay_montagem.addLayout(v_danca, 1)
        lay_montagem.addLayout(v_pess, 1)

        btn_add_danca = QPushButton("➕ Adicionar Dança à Escala")
        btn_add_danca.setStyleSheet("background-color: #2980b9; color: white; font-weight: bold; padding: 8px;")
        btn_add_danca.clicked.connect(self.adicionar_danca_escala)

        v_box_full = QVBoxLayout()
        v_box_full.addLayout(lay_montagem)
        v_box_full.addWidget(btn_add_danca)
        box_montagem.setLayout(v_box_full)

        lay_cad.addWidget(box_montagem)

        # 3. Roteiro Montado
        box_roteiro = QGroupBox("3. Roteiro Final da Apresentação")
        lay_rot = QVBoxLayout()

        self.tabela_roteiro = QTableWidget()
        self.tabela_roteiro.setColumnCount(3)
        self.tabela_roteiro.setHorizontalHeaderLabels(["Ordem", "Dança", "Integrantes Escalados"])
        self.tabela_roteiro.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Interactive)
        self.tabela_roteiro.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Interactive)
        self.tabela_roteiro.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        lay_rot.addWidget(self.tabela_roteiro)

        # Botões de Ação
        lay_btns = QHBoxLayout()
        
        btn_limpar = QPushButton("🧹 Cancelar / Novo Roteiro")
        btn_limpar.clicked.connect(self.limpar_tudo)
        lay_btns.addWidget(btn_limpar)

        lay_btns.addStretch()

        self.btn_apenas_salvar = QPushButton("💾 Salvar Apresentação")
        self.btn_apenas_salvar.setStyleSheet("background-color: #34495e; color: white; font-weight: bold; padding: 10px 15px;")
        self.btn_apenas_salvar.clicked.connect(self.salvar_apresentacao_apenas)
        lay_btns.addWidget(self.btn_apenas_salvar)

        self.btn_salvar_pdf = QPushButton("🖨️ Salvar e Gerar Roteiro PDF")
        self.btn_salvar_pdf.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 10px 15px;")
        self.btn_salvar_pdf.clicked.connect(self.salvar_e_gerar_pdf)
        lay_btns.addWidget(self.btn_salvar_pdf)

        lay_rot.addLayout(lay_btns)
        box_roteiro.setLayout(lay_rot)

        lay_cad.addWidget(box_roteiro)
        self.tabs.addTab(tab_cadastro, "➕ Nova / Editar Apresentação")

        # -------------------------------------------------------------
        # ABA 2: CONSULTA E REIMPRESSÃO DE APRESENTAÇÕES CADASTRADAS
        # -------------------------------------------------------------
        tab_historico = QWidget()
        lay_hist = QVBoxLayout(tab_historico)

        box_hist = QGroupBox("Apresentações Cadastradas")
        lay_box_h = QVBoxLayout()

        self.tabela_historico = QTableWidget()
        self.tabela_historico.setColumnCount(4)
        self.tabela_historico.setHorizontalHeaderLabels(["Data", "Nome do Evento", "Local", "Qtd. Danças"])
        self.tabela_historico.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela_historico.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.tabela_historico.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        lay_box_h.addWidget(self.tabela_historico)

        # Botões de Ação do Histórico
        lay_h_btns = QHBoxLayout()
        
        btn_atualizar_h = QPushButton("🔄 Atualizar Lista")
        btn_atualizar_h.clicked.connect(self.carregar_historico_apresentacoes)
        lay_h_btns.addWidget(btn_atualizar_h)

        lay_h_btns.addStretch()

        btn_excluir_h = QPushButton("🗑️ Excluir Selecionada")
        btn_excluir_h.setStyleSheet("background-color: #c0392b; color: white; font-weight: bold;")
        btn_excluir_h.clicked.connect(self.excluir_apresentacao_selecionada)
        lay_h_btns.addWidget(btn_excluir_h)

        btn_carregar_edicao = QPushButton("✏️ Carregar / Editar Escala")
        btn_carregar_edicao.clicked.connect(self.carregar_apresentacao_para_edicao)
        lay_h_btns.addWidget(btn_carregar_edicao)

        btn_reimprimir = QPushButton("🖨️ Reimprimir Roteiro PDF")
        btn_reimprimir.setStyleSheet("background-color: #27ae60; color: white; font-weight: bold; padding: 8px 15px;")
        btn_reimprimir.clicked.connect(self.reimprimir_roteiro_pdf)
        lay_h_btns.addWidget(btn_reimprimir)

        lay_box_h.addLayout(lay_h_btns)
        box_hist.setLayout(lay_box_h)
        lay_hist.addWidget(box_hist)

        self.tabs.addTab(tab_historico, "📋 Apresentações Cadastradas (Consulta)")

        layout_principal.addWidget(self.tabs)

    def carregar_combos_e_listas(self):
        self.lst_dancas.clear()
        dancas = DancaController.listar_dancas()
        for d in dancas:
            item = QListWidgetItem(f"{d.nome} ({d.origem or 'Geral'})")
            item.setData(Qt.ItemDataRole.UserRole, d.id)
            self.lst_dancas.addItem(item)

        self.lst_pessoas.clear()
        pessoas = PessoaController.listar_pessoas()
        for p in pessoas:
            item = QListWidgetItem(f"{p.nome} - [{p.categoria or 'Integrante'}]")
            item.setData(Qt.ItemDataRole.UserRole, p.id)
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            self.lst_pessoas.addItem(item)

    def adicionar_danca_escala(self):
        item_danca = self.lst_dancas.currentItem()
        if not item_danca:
            QMessageBox.warning(self, "Aviso", "Selecione uma dança na lista à esquerda!")
            return

        danca_id = item_danca.data(Qt.ItemDataRole.UserRole)
        nome_danca = item_danca.text()

        integrantes_ids = []
        integrantes_nomes = []

        for i in range(self.lst_pessoas.count()):
            item_p = self.lst_pessoas.item(i)
            if item_p.checkState() == Qt.CheckState.Checked:
                integrantes_ids.append(item_p.data(Qt.ItemDataRole.UserRole))
                integrantes_nomes.append(item_p.text().split(' - ')[0])

        if not integrantes_ids:
            QMessageBox.warning(self, "Aviso", "Marque pelo menos um integrante para esta dança!")
            return

        ordem = len(self.repertorio_temp) + 1

        self.repertorio_temp.append({
            "danca_id": danca_id,
            "nome_danca": nome_danca,
            "ordem": ordem,
            "integrantes_ids": integrantes_ids,
            "integrantes_nomes": integrantes_nomes
        })

        self.atualizar_tabela_roteiro()

        for i in range(self.lst_pessoas.count()):
            self.lst_pessoas.item(i).setCheckState(Qt.CheckState.Unchecked)

    def atualizar_tabela_roteiro(self):
        self.tabela_roteiro.setRowCount(0)
        for item in self.repertorio_temp:
            pos = self.tabela_roteiro.rowCount()
            self.tabela_roteiro.insertRow(pos)

            self.tabela_roteiro.setItem(pos, 0, QTableWidgetItem(str(item["ordem"])))
            self.tabela_roteiro.setItem(pos, 1, QTableWidgetItem(item["nome_danca"]))
            self.tabela_roteiro.setItem(pos, 2, QTableWidgetItem(", ".join(item["integrantes_nomes"])))

    def carregar_historico_apresentacoes(self):
        apresentacoes = ApresentacaoController.listar_apresentacoes()
        self.tabela_historico.setRowCount(0)

        for apr in apresentacoes:
            pos = self.tabela_historico.rowCount()
            self.tabela_historico.insertRow(pos)

            item_data = QTableWidgetItem(apr.data_evento.strftime("%d/%m/%Y") if apr.data_evento else "—")
            item_data.setData(Qt.ItemDataRole.UserRole, apr.id)

            qtd_dancas = len(apr.dancas_escaladas)

            self.tabela_historico.setItem(pos, 0, item_data)
            self.tabela_historico.setItem(pos, 1, QTableWidgetItem(apr.nome_evento))
            self.tabela_historico.setItem(pos, 2, QTableWidgetItem(apr.local_evento))
            self.tabela_historico.setItem(pos, 3, QTableWidgetItem(f"{qtd_dancas} dança(s)"))

    def _validar_e_salvar_banco(self):
        if not self.repertorio_temp:
            QMessageBox.warning(self, "Aviso", "Adicione pelo menos uma dança ao roteiro antes de salvar!")
            return None

        dados_ev = {
            "nome_evento": self.txt_nome_evento.text().strip(),
            "data_evento": self.dt_evento.text(),
            "local_evento": self.txt_local.text().strip(),
            "observacoes": ""
        }

        sucesso, res = ApresentacaoController.salvar_apresentacao(dados_ev, self.repertorio_temp, self.apresentacao_id_edicao)
        if not sucesso:
            QMessageBox.critical(self, "Erro", res)
            return None

        self.carregar_historico_apresentacoes()
        return res, dados_ev["nome_evento"]

    def salvar_apresentacao_apenas(self):
        res = self._validar_e_salvar_banco()
        if res:
            ap_id, nome_ev = res
            QMessageBox.information(self, "Sucesso", f"Apresentação '{nome_ev}' salva com sucesso no banco de dados!")
            self.limpar_tudo()

    def salvar_e_gerar_pdf(self):
        res = self._validar_e_salvar_banco()
        if res:
            apresentacao_id, nome_ev = res
            self._gerar_pdf_dialogo(apresentacao_id, nome_ev)
            self.limpar_tudo()

    def reimprimir_roteiro_pdf(self):
        linha = self.tabela_historico.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma apresentação da lista para reimprimir!")
            return

        item_id = self.tabela_historico.item(linha, 0)
        apresentacao_id = item_id.data(Qt.ItemDataRole.UserRole)
        nome_ev = self.tabela_historico.item(linha, 1).text()

        self._gerar_pdf_dialogo(apresentacao_id, nome_ev)

    def _gerar_pdf_dialogo(self, apresentacao_id: int, nome_evento: str):
        caminho_pdf, _ = QFileDialog.getSaveFileName(
            self, 
            "Salvar Roteiro da Apresentação em PDF", 
            f"Apresentacao_{nome_evento.replace(' ', '_')}.pdf", 
            "Arquivos PDF (*.pdf)"
        )

        if caminho_pdf:
            ok_pdf, msg_pdf = RelatorioApresentacaoPDF.gerar_pdf(apresentacao_id, caminho_pdf)
            if ok_pdf:
                QMessageBox.information(self, "Sucesso", f"Relatório PDF gerado com sucesso em:\n{caminho_pdf}")
                try:
                    os.startfile(caminho_pdf)
                except Exception:
                    pass
            else:
                QMessageBox.warning(self, "Aviso", f"Erro ao gerar PDF: {msg_pdf}")

    def carregar_apresentacao_para_edicao(self):
        linha = self.tabela_historico.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma apresentação da lista para carregar!")
            return

        item_id = self.tabela_historico.item(linha, 0)
        apresentacao_id = item_id.data(Qt.ItemDataRole.UserRole)

        detalhes = ApresentacaoController.buscar_detalhes_completos(apresentacao_id)
        if not detalhes:
            QMessageBox.warning(self, "Aviso", "Não foi possível carregar os detalhes do evento.")
            return

        self.apresentacao_id_edicao = detalhes["id"]
        self.txt_nome_evento.setText(detalhes["nome_evento"])
        self.txt_local.setText(detalhes["local_evento"])
        if detalhes["data_evento"]:
            self.dt_evento.setDate(QDate(detalhes["data_evento"].year, detalhes["data_evento"].month, detalhes["data_evento"].day))

        self.repertorio_temp = detalhes["repertorio"]
        self.atualizar_tabela_roteiro()

        self.tabs.setCurrentIndex(0)
        self.btn_apenas_salvar.setText("✏️ Atualizar Apresentação")

    def excluir_apresentacao_selecionada(self):
        linha = self.tabela_historico.currentRow()
        if linha < 0:
            QMessageBox.warning(self, "Aviso", "Selecione uma apresentação para excluir!")
            return

        item_id = self.tabela_historico.item(linha, 0)
        apresentacao_id = item_id.data(Qt.ItemDataRole.UserRole)
        nome_ev = self.tabela_historico.item(linha, 1).text()

        resposta = QMessageBox.question(
            self, "Confirmação", 
            f"Tem certeza que deseja excluir a apresentação '{nome_ev}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if resposta == QMessageBox.StandardButton.Yes:
            sucesso, msg = ApresentacaoController.excluir_apresentacao(apresentacao_id)
            if sucesso:
                QMessageBox.information(self, "Sucesso", msg)
                self.carregar_historico_apresentacoes()
            else:
                QMessageBox.critical(self, "Erro", msg)

    def limpar_tudo(self):
        self.apresentacao_id_edicao = None
        self.repertorio_temp = []
        self.txt_nome_evento.clear()
        self.txt_local.clear()
        self.dt_evento.setDate(QDate.currentDate())
        self.btn_apenas_salvar.setText("💾 Salvar Apresentação")
        self.atualizar_tabela_roteiro()
# views/baixa_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QComboBox, QSpinBox, QLineEdit, QPushButton, QTableWidget, 
    QTableWidgetItem, QHeaderView, QMessageBox, QAbstractItemView
)
from controllers.baixa_controller import BaixaController
from controllers.bem_controller import BemController

class BaixaView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.carregar_combos()
        self.carregar_dados()

    def _init_ui(self):
        layout_principal = QVBoxLayout()

        # Formulário de Baixa
        box_form = QGroupBox("Registrar Baixa / Descarte de Material")
        form_lay = QVBoxLayout()

        l1 = QHBoxLayout()
        l1.addWidget(QLabel("Selecione o Bem:*"))
        self.cb_bem = QComboBox()
        l1.addWidget(self.cb_bem, stretch=3)

        l1.addWidget(QLabel("Quantidade:*"))
        self.spn_qtd = QSpinBox()
        self.spn_qtd.setRange(1, 999)
        l1.addWidget(self.spn_qtd)

        l1.addWidget(QLabel("Motivo:*"))
        self.cb_motivo = QComboBox()
        self.cb_motivo.addItems(["Danificado / Quebrado", "Perda / Extravio", "Descarte por Desgaste", "Outros"])
        l1.addWidget(self.cb_motivo, stretch=2)
        form_lay.addLayout(l1)

        l2 = QHBoxLayout()
        l2.addWidget(QLabel("Justificativa / Obs:"))
        self.txt_obs = QLineEdit()
        self.txt_obs.setPlaceholderText("Explique detalhadamente o motivo da baixa...")
        l2.addWidget(self.txt_obs, stretch=3)

        self.btn_confirmar = QPushButton(" Confirmar Baixa")
        self.btn_confirmar.clicked.connect(self.salvar_baixa)
        l2.addWidget(self.btn_confirmar)
        form_lay.addLayout(l2)

        box_form.setLayout(form_lay)
        layout_principal.addWidget(box_form)

        # Grid do Histórico de Baixas
        box_grid = QGroupBox("Histórico de Baixas")
        grid_lay = QVBoxLayout()

        self.tabela = QTableWidget()
        self.tabela.setColumnCount(7)
        self.tabela.setHorizontalHeaderLabels([
            "ID", "Código", "Material", "Qtd Baixada", "Motivo", "Data Baixa", "Observações"
        ])
        self.tabela.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tabela.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tabela.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)

        grid_lay.addWidget(self.tabela)
        box_grid.setLayout(grid_lay)
        layout_principal.addWidget(box_grid)

        self.setLayout(layout_principal)

    def carregar_combos(self):
        self.cb_bem.clear()
        bens = BemController.listar_todos()
        for b in bens:
            if b.quantidade_disponivel > 0:
                self.cb_bem.addItem(f"{b.codigo_patrimonio} - {b.nome} (Disp: {b.quantidade_disponivel})", b.id)

    def carregar_dados(self):
        baixas = BaixaController.listar_baixas()
        self.tabela.setRowCount(0)
        for b in baixas:
            pos = self.tabela.rowCount()
            self.tabela.insertRow(pos)

            self.tabela.setItem(pos, 0, QTableWidgetItem(str(b["id"])))
            self.tabela.setItem(pos, 1, QTableWidgetItem(b["codigo"]))
            self.tabela.setItem(pos, 2, QTableWidgetItem(b["bem"]))
            self.tabela.setItem(pos, 3, QTableWidgetItem(str(b["qtd"])))
            self.tabela.setItem(pos, 4, QTableWidgetItem(b["motivo"]))
            self.tabela.setItem(pos, 5, QTableWidgetItem(b["data"]))
            self.tabela.setItem(pos, 6, QTableWidgetItem(b["obs"]))

    def salvar_baixa(self):
        if self.cb_bem.currentIndex() < 0:
            QMessageBox.warning(self, "Aviso", "Selecione um bem!")
            return

        bem_id = self.cb_bem.currentData()
        qtd = self.spn_qtd.value()
        motivo = self.cb_motivo.currentText()
        obs = self.txt_obs.text()

        confirm = QMessageBox.question(
            self, "Atenção", "Essa ação abaterá definitivamente os itens do patrimônio. Confirmar baixa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )

        if confirm == QMessageBox.StandardButton.Yes:
            sucesso, msg = BaixaController.registrar_baixa(bem_id, qtd, motivo, obs)
            if sucesso:
                QMessageBox.information(self, "Sucesso", msg)
                self.txt_obs.clear()
                self.carregar_combos()
                self.carregar_dados()
            else:
                QMessageBox.warning(self, "Aviso", msg)
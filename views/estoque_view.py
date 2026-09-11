# views/estoque_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
    QLineEdit, QPushButton, QTreeWidget, QTreeWidgetItem, 
    QHeaderView, QAbstractItemView
)
from PyQt6.QtCore import Qt
from controllers.bem_controller import BemController

class EstoqueView(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._init_ui()
        self.carregar_dados()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)

        # Filtros de Busca
        box_filtro = QGroupBox("Consulta Agrupada do Estoque")
        lay_filtro = QHBoxLayout()

        lay_filtro.addWidget(QLabel("Filtrar Material:"))
        self.txt_filtro = QLineEdit()
        self.txt_filtro.setPlaceholderText("Buscar por Nome do Material ou Categoria...")
        self.txt_filtro.textChanged.connect(self.carregar_dados)
        lay_filtro.addWidget(self.txt_filtro)

        btn_atualizar = QPushButton("Atualizar")
        btn_atualizar.clicked.connect(self.carregar_dados)
        lay_filtro.addWidget(btn_atualizar)

        box_filtro.setLayout(lay_filtro)
        layout_principal.addWidget(box_filtro)

        # Árvore do Estoque (QTreeWidget)
        self.tree_estoque = QTreeWidget()
        self.tree_estoque.setColumnCount(5)
        self.tree_estoque.setHeaderLabels([
            "Item / Código Patrimonial", "Categoria", 
            "Qtd / Total Consolidado", "Conservação", "Status"
        ])
        
        # Configurações de seleção e comportamento
        self.tree_estoque.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.tree_estoque.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.tree_estoque.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)

        layout_principal.addWidget(self.tree_estoque)

    def carregar_dados(self):
        filtro = self.txt_filtro.text().strip()
        
        # Busca todos os bens cadastrados via controller
        bens = BemController.listar_todos(filtro)

        self.tree_estoque.clear()

        # Agrupa os bens pelo nome
        agrupados = {}
        for b in bens:
            nome = getattr(b, 'nome', 'Sem Nome')
            if nome not in agrupados:
                agrupados[nome] = []
            agrupados[nome].append(b)

        # Constrói os nós da árvore
        for nome_material, lista_itens in agrupados.items():
            total_unidades = len(lista_itens)
            categoria_material = getattr(lista_itens[0], 'categoria', '') or 'N/A'

            # Nó Pai (Material Consolidado)
            no_pai = QTreeWidgetItem(self.tree_estoque)
            no_pai.setText(0, f"📦 {nome_material}")
            no_pai.setText(1, categoria_material)
            no_pai.setText(2, f"{total_unidades} Unidade(s)")
            no_pai.setText(3, "—")
            no_pai.setText(4, "Consolidado")

            # Destaca a linha do Nó Pai
            for col in range(5):
                no_pai.setBackground(col, Qt.GlobalColor.lightGray)

            # Nós Filhos (Itens Patrimoniais Individuais)
            for item in lista_itens:
                no_filho = QTreeWidgetItem(no_pai)
                
                # Guarda o ID real no UserRole do filho
                id_bem = getattr(item, 'id', None)
                no_filho.setData(0, Qt.ItemDataRole.UserRole, id_bem)

                cod_patrimonio = getattr(item, 'codigo_patrimonio', 'N/A')
                conservacao = getattr(item, 'estado_conservacao', '') or 'N/A'
                status = getattr(item, 'status', '') or 'Disponível'

                no_filho.setText(0, f"🏷️ {cod_patrimonio}")
                no_filho.setText(1, categoria_material)
                no_filho.setText(2, "1 un")
                no_filho.setText(3, conservacao)
                no_filho.setText(4, status)
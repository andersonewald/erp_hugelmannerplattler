# views/main_window.py
from PyQt6.QtWidgets import (
    QMainWindow, QMdiArea, QMdiSubWindow, QMenu, QMenuBar, 
    QStatusBar, QMessageBox, QApplication, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout, QToolButton, QLabel
)
from PyQt6.QtGui import QAction, QFont
from PyQt6.QtCore import Qt, QSize


class DashboardWidget(QWidget):
    """Painel central com ícones de atalho no estilo Cards."""
    def __init__(self, parent_main):
        super().__init__()
        self.main = parent_main
        self._init_ui()

    def _init_ui(self):
        layout_principal = QVBoxLayout(self)
        layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Título do Dashboard
        lbl_titulo = QLabel("Painel de Gestão Patrimonial")
        lbl_titulo.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("color: #2c3e50; margin-bottom: 25px;")
        layout_principal.addWidget(lbl_titulo)

        # Grid de Botões (3x3)
        grid = QGridLayout()
        grid.setSpacing(20)

        botoes = [
            ("Pessoas", "👥", self.main.abrir_cadastro_pessoas),
            ("Patrimônio", "📦", self.main.abrir_cadastro_bens),
            ("Danças", "💃", self.main.abrir_cadastro_dancas),
            ("Empréstimos", "🤝", self.main.abrir_emprestimos),
            ("Estoque", "📊", self.main.abrir_contagem_estoque),
            ("Apresentações", "🎭", self.main.abrir_montar_apresentacao),
            ("Baixas", "🗑️", self.main.abrir_baixa_bens),
        ]

        posicoes = [
            (0, 0), (0, 1), (0, 2),
            (1, 0), (1, 1), (1, 2),
            (2, 0)
        ]

        for (texto, icone, metodo), pos in zip(botoes, posicoes):
            btn = QToolButton()
            btn.setText(f"{icone}\n\n{texto}")
            btn.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))
            btn.setFixedSize(150, 120)
            btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
            
            btn.setStyleSheet("""
                QToolButton {
                    background-color: #ffffff;
                    border: 1px solid #dcdfe6;
                    border-radius: 12px;
                    color: #2c3e50;
                }
                QToolButton:hover {
                    background-color: #f2f6fc;
                    border: 2px solid #409eff;
                    color: #409eff;
                }
                QToolButton:pressed {
                    background-color: #ecf5ff;
                }
            """)
            btn.clicked.connect(metodo)
            grid.addWidget(btn, pos[0], pos[1])

        layout_principal.addLayout(grid)


class MainWindow(QMainWindow):
    def __init__(self, usuario=None):
        super().__init__()

        self.usuario_atual = usuario

        self.setWindowTitle("ERP Hugelmannerplattler - Controle Patrimonial")
        self.setGeometry(100, 100, 1200, 800)

        # Configura a Área MDI (Área de Trabalho)
        self.mdi_area = QMdiArea()
        self.mdi_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.mdi_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.setCentralWidget(self.mdi_area)

        # Criar o Dashboard centralizado
        self.dashboard = DashboardWidget(self)

        # Criar menus e barra de status
        self._criar_menus()
        
        # Exibe o status inicial e o Dashboard
        self._atualizar_status_bar()

        # Controle de autenticação ao iniciar
        if not self.usuario_atual:
            self._bloquear_sistema(True)
            self.exibir_login_incorporado()
        else:
            self._bloquear_sistema(False)

    def _bloquear_sistema(self, bloquear: bool):
        """Habilita ou desabilita os menus e o Dashboard."""
        self.menu_cadastros.setEnabled(not bloquear)
        self.menu_movimento.setEnabled(not bloquear)
        self.dashboard.setEnabled(not bloquear)

    def _atualizar_status_bar(self):
        if self.usuario_atual:
            nome_user = getattr(self.usuario_atual, 'nome', 'Operador')
            self.statusBar().showMessage(f"Usuário Logado: {nome_user} | Sistema Pronto")
        else:
            self.statusBar().showMessage("Aguardando Autenticação de Usuário...")

    def exibir_login_incorporado(self):
        """Abre a tela de login diretamente na área MDI."""
        from views.login_view import LoginWidget

        self.mdi_area.closeAllSubWindows()

        self.widget_login = LoginWidget(on_login_sucesso=self.sucesso_login)

        self.sub_login = QMdiSubWindow()
        self.sub_login.setWidget(self.widget_login)
        self.sub_login.setWindowTitle("Acesso ao Sistema")
        
        self.sub_login.setWindowFlags(
            Qt.WindowType.SubWindow | 
            Qt.WindowType.CustomizeWindowHint | 
            Qt.WindowType.WindowTitleHint
        )

        self.mdi_area.addSubWindow(self.sub_login)
        self.sub_login.show()
        
        self.sub_login.adjustSize()
        x = (self.mdi_area.width() - self.sub_login.width()) // 2
        y = (self.mdi_area.height() - self.sub_login.height()) // 2
        self.sub_login.move(max(0, x), max(0, y))

    def sucesso_login(self, usuario):
        """Callback executado após login aprovado."""
        self.usuario_atual = usuario
        self._bloquear_sistema(False)
        self._atualizar_status_bar()
        self.sub_login.close()
        self.exibir_dashboard_central()

    def abrir_login(self):
        """Realiza logoff e retorna à tela de login."""
        self._bloquear_sistema(True)
        self.usuario_atual = None
        self._atualizar_status_bar()
        self.exibir_login_incorporado()

    def exibir_dashboard_central(self):
        """Exibe o Dashboard centralizado na MDI sem bordas de janela."""
        for sub in self.mdi_area.subWindowList():
            if sub.windowTitle() == "Painel Inicial":
                sub.showMaximized()
                return

        sub_dash = QMdiSubWindow()
        sub_dash.setWidget(self.dashboard)
        sub_dash.setWindowTitle("Painel Inicial")
        
        # Remove a barra de título/borda da janela do Dashboard para integrá-lo ao fundo
        sub_dash.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        
        self.mdi_area.addSubWindow(sub_dash)
        sub_dash.showMaximized()

    def _criar_menus(self):
        menu_bar = self.menuBar()

        # Menu Sistema
        menu_sistema = menu_bar.addMenu("&Sistema")
        
        acao_inicio = QAction("Painel Inicial (Dashboard)", self)
        acao_inicio.triggered.connect(self.exibir_dashboard_central)
        menu_sistema.addAction(acao_inicio)

        acao_trocar_usuario = QAction("Trocar Usuário / Login", self)
        acao_trocar_usuario.triggered.connect(self.abrir_login)
        menu_sistema.addAction(acao_trocar_usuario)

        menu_sistema.addSeparator()

        acao_sair = QAction("Sair", self)
        acao_sair.setShortcut("Alt+F4")
        acao_sair.triggered.connect(QApplication.instance().quit)
        menu_sistema.addAction(acao_sair)

        # Menu Cadastros
        self.menu_cadastros = menu_bar.addMenu("&Cadastros")

        acao_pessoas = QAction("Pessoas / Integrantes", self)
        acao_pessoas.triggered.connect(self.abrir_cadastro_pessoas)
        self.menu_cadastros.addAction(acao_pessoas)

        acao_bens = QAction("Bens / Materiais (Patrimônio)", self)
        acao_bens.triggered.connect(self.abrir_cadastro_bens)
        self.menu_cadastros.addAction(acao_bens)

        acao_dancas = QAction("Danças / Repertório", self)
        acao_dancas.triggered.connect(self.abrir_cadastro_dancas)
        self.menu_cadastros.addAction(acao_dancas)

        # Menu Movimentações
        self.menu_movimento = menu_bar.addMenu("&Movimentações")

        acao_apresentacao = QAction("Montar Apresentação / Escala", self)
        acao_apresentacao.triggered.connect(self.abrir_montar_apresentacao)
        self.menu_movimento.addAction(acao_apresentacao)

        self.menu_movimento.addSeparator()

        acao_estoque = QAction("Contagem de Estoque", self)
        acao_estoque.triggered.connect(self.abrir_contagem_estoque)
        self.menu_movimento.addAction(acao_estoque)

        acao_emprestimo = QAction("Controle de Empréstimos", self)
        acao_emprestimo.triggered.connect(self.abrir_emprestimos)
        self.menu_movimento.addAction(acao_emprestimo)

        self.menu_movimento.addSeparator()

        acao_baixa = QAction("Baixa de Bens / Materiais", self)
        acao_baixa.triggered.connect(self.abrir_baixa_bens)
        self.menu_movimento.addAction(acao_baixa)

        # Menu Janelas
        menu_janelas = menu_bar.addMenu("&Janelas")

        acao_cascatas = QAction("Em Cascata", self)
        acao_cascatas.triggered.connect(self.mdi_area.cascadeSubWindows)
        menu_janelas.addAction(acao_cascatas)

        acao_lado_a_lado = QAction("Lado a Lado", self)
        acao_lado_a_lado.triggered.connect(self.mdi_area.tileSubWindows)
        menu_janelas.addAction(acao_lado_a_lado)

        acao_fechar_todas = QAction("Fechar Todas", self)
        acao_fechar_todas.triggered.connect(self.mdi_area.closeAllSubWindows)
        menu_janelas.addAction(acao_fechar_todas)

        # Menu Ajuda
        menu_ajuda = menu_bar.addMenu("&Ajuda")
        acao_sobre = QAction("Sobre o ERP", self)
        acao_sobre.triggered.connect(self.exibir_sobre)
        menu_ajuda.addAction(acao_sobre)

    def _abrir_janela_filha(self, titulo, widget_conteudo):
        """Método auxiliar MDI para abrir janelas filhas."""
        for sub_window in self.mdi_area.subWindowList():
            if sub_window.windowTitle() == titulo:
                self.mdi_area.setActiveSubWindow(sub_window)
                sub_window.showMaximized()
                return

        sub_window = QMdiSubWindow()
        sub_window.setWindowTitle(titulo)
        sub_window.setWidget(widget_conteudo)
        sub_window.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        self.mdi_area.addSubWindow(sub_window)
        sub_window.showMaximized()

    def abrir_cadastro_pessoas(self):
        from views.pessoa_view import PessoaView
        self._abrir_janela_filha("Cadastro de Pessoas / Integrantes", PessoaView())

    def abrir_cadastro_bens(self):
        from views.bem_view import BemView
        self._abrir_janela_filha("Cadastro de Bens / Materiais", BemView())

    def abrir_contagem_estoque(self):
        from views.estoque_view import EstoqueView
        self._abrir_janela_filha("Contagem de Estoque", EstoqueView())

    def abrir_emprestimos(self):
        from views.emprestimo_view import EmprestimoView
        self._abrir_janela_filha("Controle de Empréstimos", EmprestimoView())

    def abrir_baixa_bens(self):
        from views.baixa_view import BaixaView
        self._abrir_janela_filha("Baixa de Materiais", BaixaView())

    def abrir_cadastro_dancas(self):
        from views.danca_view import DancaView
        self._abrir_janela_filha("Cadastro de Danças e Repertório", DancaView())

    def abrir_montar_apresentacao(self):
        from views.apresentacao_view import ApresentacaoView
        self._abrir_janela_filha("Montagem de Apresentação e Escala", ApresentacaoView())

    def exibir_sobre(self):
        QMessageBox.about(
            self,
            "Sobre o ERP Hugelmannerplattler",
            "<b>ERP Hugelmannerplattler</b><br>"
            "Sistema de Controle Patrimonial e Gestão Interna.<br><br>"
        )
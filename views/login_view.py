# views/login_view.py
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGroupBox, QApplication
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from controllers.auth_controller import AuthController

class LoginWidget(QWidget):
    def __init__(self, on_login_sucesso, parent=None):
        super().__init__(parent)

        self.on_login_sucesso = on_login_sucesso
        self.usuario_logado = None
        
        self.setFixedSize(380, 260)
        self._init_ui()

    def _init_ui(self):
        layout_principal = QVBoxLayout()
        layout_principal.setContentsMargins(15, 15, 15, 15)

        # Cabeçalho / Título
        lbl_titulo = QLabel("Acesso ao Sistema")
        fonte_titulo = QFont()
        fonte_titulo.setPointSize(14)
        fonte_titulo.setBold(True)
        lbl_titulo.setFont(fonte_titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_principal.addWidget(lbl_titulo)

        lbl_subtitulo = QLabel("Controle Patrimonial - Hugelmannerplattler")
        lbl_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_subtitulo.setStyleSheet("color: gray;")
        layout_principal.addWidget(lbl_subtitulo)

        layout_principal.addSpacing(10)

        # Quadro do formulário (estilo caixa Delphi)
        box_login = QGroupBox("Credenciais")
        box_layout = QVBoxLayout()

        # Campo Usuário
        box_layout.addWidget(QLabel("Usuário / Login:"))
        self.txt_login = QLineEdit()
        self.txt_login.setPlaceholderText("Ex: admin")
        box_layout.addWidget(self.txt_login)

        # Campo Senha
        box_layout.addWidget(QLabel("Senha:"))
        self.txt_senha = QLineEdit()
        self.txt_senha.setEchoMode(QLineEdit.EchoMode.Password)
        self.txt_senha.setPlaceholderText("Sua senha")
        self.txt_senha.returnPressed.connect(self.validar_login)  # Permite dar Enter na senha
        box_layout.addWidget(self.txt_senha)

        box_login.setLayout(box_layout)
        layout_principal.addWidget(box_login)

        # Botões de Ação
        layout_botoes = QHBoxLayout()

        self.btn_entrar = QPushButton("Entrar")
        self.btn_entrar.setDefault(True)
        self.btn_entrar.clicked.connect(self.validar_login)
        layout_botoes.addWidget(self.btn_entrar)

        self.btn_cancelar = QPushButton("Sair")
        self.btn_cancelar.clicked.connect(QApplication.instance().quit)
        layout_botoes.addWidget(self.btn_cancelar)

        layout_principal.addLayout(layout_botoes)
        self.setLayout(layout_principal)

    def validar_login(self):
        login = self.txt_login.text().strip()
        senha = self.txt_senha.text().strip()

        if not login or not senha:
            QMessageBox.warning(self, "Aviso", "Preencha o usuário e a senha!")
            return

        sucesso, resultado = AuthController.autenticar(login, senha)

        if sucesso:
            self.usuario_logado = resultado
            # Dispara o evento de sucesso para a MainWindow liberar o sistema
            if self.on_login_sucesso:
                self.on_login_sucesso(self.usuario_logado)
        else:
            QMessageBox.critical(self, "Erro de Autenticação", "Usuário ou senha incorretos!")
            self.txt_senha.clear()
            self.txt_senha.setFocus()
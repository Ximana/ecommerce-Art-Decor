---

```markdown
# 🛒 E-commerce Django - Art & Decor

Este é um projeto de e-commerce desenvolvido com Django e PostgreSQL. A plataforma permite o cadastro de usuários, gerenciamento de produtos, controle de estoque, promoções, carrinho de compras, pedidos, formas de envio e métodos de pagamento.

## 📌 Visão Geral

Este sistema foi desenvolvido com o objetivo de simular um ambiente real de loja virtual, cobrindo desde o cadastro e visualização de produtos até a finalização do pedido com diferentes formas de pagamento.

## 🧱 Modelo de Dados

O modelo relacional foi cuidadosamente desenhado para suportar as principais operações de um e-commerce, incluindo:

- **Usuários** com diferentes tipos de acesso (cliente, administrador)
- **Produtos** com variações, imagens e controle de estoque
- **Carrinho de compras** e histórico de pedidos
- **Pagamentos** e diferentes métodos (cartão, transferência, etc.)
- **Promoções** aplicadas a produtos
- **Formas de envio** com cálculo de taxas

Você pode visualizar o modelo relacional completo [aqui](diagrama).

## ⚙️ Tecnologias Utilizadas

- **Linguagem:** Python 3.x
- **Framework Web:** Django 4.x
- **Banco de Dados:** PostgreSQL
- **ORM:** Django ORM
- **Template Engine:** Django Templates
- **Gerenciamento de dependências:** pip + virtualenv
- **Outros:** Bootstrap 5 (para o front-end), Gunicorn e Nginx (para produção)

## 📁 Estrutura de Diretórios

```


````

## 🚀 Funcionalidades

- Cadastro, login e autenticação de usuários
- CRUD de produtos com categorias e marcas
- Gerenciamento de estoque e movimentações
- Carrinho de compras e adição de itens
- Registro de pedidos com múltiplos itens
- Histórico de pedidos por usuário
- Cadastro e aplicação de promoções e cupons
- Integração com múltiplos métodos de pagamento
- Emissão de comprovantes e rastreamento de status
- Cálculo automático de taxas de envio e pagamentos

## 🧪 Como Executar Localmente

1. Clone o repositório:

```bash
git clone https://github.com/ximana/ecommerce-django.git
cd ecommerce-django
````

2. Crie e ative um ambiente virtual:

```bash
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate
```

3. Instale as dependências:

```bash
pip install -r requirements.txt
```

4. Configure o banco PostgreSQL e o arquivo `.env` com suas credenciais:

```env
DB_NAME=seubanco
DB_USER=usuario
DB_PASSWORD=senha
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=sua_chave_secreta
DEBUG=True
```

5. Execute as migrações:

```bash
python manage.py makemigrations
python manage.py migrate
```

6. Crie um superusuário:

```bash
python manage.py createsuperuser
```

7. Inicie o servidor:

```bash
python manage.py runserver
```

Acesse o projeto em: [http://localhost:8000](http://localhost:8000)

## 🧾 Diagrama do Banco de Dados



## 📦 Requisitos

* Python 3.10+
* PostgreSQL 13+
* Django 4.x
* psycopg2-binary
* Pillow

## 🧑‍💻 Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues e enviar pull requests.

## 📄 Licença

Este projeto está licenciado sob a [MIT License](LICENSE).

## 🙋‍♂️ Autor

Desenvolvido por \Paulo Ximana e Leonardo Teca.*

---

```

---

```

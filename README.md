# Estoque Fácil
Sistema web de estoque com login, cadastro de produtos, entradas, saídas e histórico.

## Tecnologias
Python 3, Flask, SQLite, HTML e CSS.

## Executar
1. Instale Python 3.10+.
2. No terminal, execute `pip install -r requirements.txt`.
3. Execute `python app.py`.
4. Abra `http://127.0.0.1:5000`.

## Primeiro acesso
Usuário: `admin`  
Senha: `admin123`

O banco SQLite é criado automaticamente. Troque a senha padrão e configure uma SECRET_KEY forte antes de usar em produção.

## Recursos
- Login e logout com senha armazenada em hash.
- Cadastro de produtos e SKU opcional.
- Entrada e saída de produtos.
- Impede saída maior que o saldo disponível.
- Painel com saldo e alerta de estoque mínimo.
- Histórico com data e usuário.

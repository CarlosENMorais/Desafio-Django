
-----

# Desafio Técnico — Estagiário 
Python/Django :: 2026.1

## 🛠 Pré-requisitos

1.  **Git** (Para clonar o repositório).
2.  **Docker Desktop** (O **Docker Engine** e o **Docker Compose Plugin V2**).

> **Atenção:** Se estiver usando WSL (Windows Subsystem for Linux), certifique-se de que a integração do Docker Desktop para a sua distribuição Linux esteja **habilitada** nas configurações.

-----

## ⚙️ Instalação e Inicialização

### 1\. Clonar o Repositório

Abra o terminal na pasta onde deseja salvar o projeto e clone o repositório:

```bash
git clone https://github.com/CarlosENMorais/Desafio-Django.git
cd estagio_PythonDjango # ou o nome da sua pasta
```

### 2\. Garantir Permissão de Execução

Antes de iniciar os contêineres pela primeira vez, torne o script de inicialização executável no seu sistema:

```bash
chmod +x entrypoint.sh
```

### 3\. Inicializar os Contêineres

Execute o comando na raiz do projeto:

```bash
# O --build é crucial na primeira execução ou após mudanças no Dockerfile
docker compose up --build 
```

### 3\. Acesso à Aplicação

Após a inicialização bem-sucedida (o terminal parará de mostrar logs de migração e mostrará a mensagem de *server running*), o projeto estará acessível em:

[http://localhost:8000]

-----

## 💻 Comandos Úteis

Para executar comandos do Django, use o prefixo `docker compose exec web` (onde `web` é o nome do serviço no `docker-compose.yml`) seguido do comando que você deseja rodar.

| Tarefa | Comando | Descrição |
| :--- | :--- | :--- |
| **Executar Migrações** | `docker compose exec web python manage.py migrate` | Aplica todas as migrações pendentes no BD. |
| **Criar Superusuário** | `docker compose exec web python manage.py createsuperuser` | Cria uma conta de administrador para o painel Django. |
| **Abrir Shell do Django** | `docker compose exec web python manage.py shell` | Inicia o shell interativo Python no contexto da aplicação. |
| **Parar Contêineres** | Pressione `Ctrl+C` (encerramento seguro). Se precisar desligar os contêineres em segundo plano: `docker compose down` |
| **Remover Dados** | `docker compose down -v` | Para e remove contêineres **e os dados** persistidos no volume `postgres_data`. **Use com cautela\!** |

-----

## 🐳 Arquitetura Docker

| Arquivo/Serviço | Função |
| :--- | :--- |
| **`Dockerfile`** | Define a imagem do serviço `web` (Django), baseada em Python 3.12-slim. Instala dependências e ferramentas como `netcat`. |
| **`docker-compose.yml`** | Define e orquestra dois serviços: `web` (Django) e `db` (PostgreSQL). |
| **`entrypoint.sh`** | Script de inicialização do Django. Contém a lógica de `wait-for-it` (`netcat`) para garantir que o BD esteja pronto antes de aplicar as migrações. |
| **`postgres_data` volume** | Volume persistente usado para salvar os dados do PostgreSQL no seu sistema, garantindo que os dados não sejam perdidos ao derrubar os contêineres. |

-----
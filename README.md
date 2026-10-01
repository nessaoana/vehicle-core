# vehicle-core

Serviço principal para cadastro de veículos e operações de negócio. A imagem da
API é construída a partir de `app/`, e a stack local fornece PostgreSQL e
LocalStack.

## Desenvolvimento local

Crie os arquivos de ambiente locais a partir de `.env.example` e execute:

```bash
python3 -m venv .venv
.venv/bin/pip install -r app/src/requirements.txt
PYTHONPATH=app/src .venv/bin/pytest app/tests --cov=app/src --cov-report=term-missing --cov-fail-under=80
docker compose up --build
```

O container da API escuta na porta `8001`, e o PostgreSQL é exposto na porta
`5433` para evitar conflitos com o serviço de venda de veículos.

## CI/CD

O workflow de CI é executado em pull requests e pushes para `main`. Ele instala
as dependências, compila o código Python e bloqueia alterações quando a
cobertura dos testes fica abaixo de 80%. O mesmo workflow executa a análise
SonarQube e bloqueia a alteração quando o quality gate configurado falha.

O build Python usa o workflow reutilizável
`fiap-soat-grupo36/reusable-actions/.github/workflows/_reusable-build-python.yml`.
Como esse workflow não aplica um limite mínimo de cobertura, o job
`coverage-gate` executa a verificação adicional de 80%.

O job de análise usa
`fiap-soat-grupo36/reusable-actions/.github/workflows/_reusable-sonar-python.yml`
e executa no SonarCloud. Configure `SONAR_TOKEN` como secret e `SONAR_ORG` como
repository variable.

Em pushes para `main`, o workflow de CD usa
`fiap-soat-grupo36/reusable-actions/.github/workflows/_reusable-dockerhub.yml`
para publicar a imagem `app` no Docker Hub. Configure `DOCKERHUB_USERNAME` e
`DOCKERHUB_TOKEN` no GitHub. Use `DOCKERHUB_USERNAME` como repository variable
e `DOCKERHUB_TOKEN` como secret.

Depois da publicação da imagem, o mesmo CD executa o deploy Terraform no
LocalStack Cloud usando
`fiap-soat-grupo36/reusable-actions/.github/workflows/_reusable-terraform.yml`.

Após um CI bem-sucedido em uma branch diferente de `main`,
o job `create-pr` usa
`fiap-soat-grupo36/reusable-actions/.github/workflows/_reusable-create-pr.yml`
para abrir um Pull Request automaticamente contra `main`.

Após o merge de um pull request em `main`, o workflow `cd.yml` publica a imagem
e executa o `apply` no LocalStack Cloud.

## Terraform e LocalStack

A configuração Terraform em `infra/` provisiona o bucket S3
`vehicle-core-assets` e habilita o versionamento. Para fazer o deploy na
instância local do LocalStack:

```bash
cd infra
terraform init
terraform plan -out=vehicle-core-local.tfplan
terraform apply vehicle-core-local.tfplan
```

O endpoint local é `http://localhost:4566`. O workflow
[`ci.yml`](.github/workflows/ci.yml) inicia o emulador LocalStack Cloud
autenticado, executa `terraform plan` em pull requests e executa `terraform
apply` após um merge em `main`.

Esse workflow usa
`fiap-soat-grupo36/reusable-actions/.github/workflows/_reusable-terraform.yml`.

Configure `LOCALSTACK_AUTH_TOKEN` como secret do repositório ou do ambiente,
usando um LocalStack CI Auth Token. O token nunca é armazenado no repositório. O
workflow Terraform usa o proxy oficial `lstk terraform`, fazendo o Terraform
apontar para o endpoint compatível com AWS do LocalStack em vez de uma conta AWS
real.
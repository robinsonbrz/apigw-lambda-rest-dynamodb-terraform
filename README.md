# AWS Amazon - ApiGateway / Lambda / DynamoDB CRUD / Sqs

## Crud Api + Gestão de eventos com Sqs / Lambda com Terraform iAc


![Diagrama Aws](/resources/aws-lambda-apigw.gif)



**Lambda function1** controla eventos da **AWS ApiGateway** processando um CRUD Movie.

```json
{
    "year":"2010",
    "title":"Inception",
    "created_at":"2024-11-25 03:09:28",
    "approval_status":"pending",	
    "approved_date":"-"
}
```

Ao criar um Movie com o método **POST**, o approval_status padrão do Movie é "pending" e o "approved_date" é "-".

Ao atualizarmos o approval_status para "approved" com o método PATCH ou PUT, uma mensagem Sqs é disparada. A mensagem **Sqs** é disparada caso o **"approval_status"** anterior seja **"pending"**, e a atualização solicite **"approved"**.

Uma segunda **Lambda function** é encarregada de receber essas mensagens **Sqs**, e atualiza o banco de dados **DynamoDb** com o novo estado do Movie para **"approval_status": "approved"**, e também registra o **"approved_date" : "2024-11-25 03:10:49"**.


### Body método PATCH 

Url exemplo PATCH: ```https://apigw_url/movies/c5b9d146-6cbc-4353-9f47-c6210c561b6d```

```json
{
"approval_status": "approved"
}
```

### Body método PUT

Url exemplo PUT: ```https://apigw_url/movies/c5b9d146-6cbc-4353-9f47-c6210c561b6d```

```json
{
    "year": 1993,
    "title": "Batman",
    "approval_status": "approved"
}
```

**Importante:**

Esta aplicação utiliza vários serviços da AWS e existem custos associados a esses serviços após o uso da Camada Gratuita - consulte a  [AWS Pricing page](https://aws.amazon.com/pricing/)  para obter detalhes. Você é responsável por quaisquer custos incorridos na AWS. Nenhuma garantia está implícita neste exemplo.




## Requisitos

* [Crie uma conta da AWS](https://portal.aws.amazon.com/gp/aws/developer/registration/index.html) caso ainda não tenha uma e faça login. O usuário IAM que você usar deve ter permissões suficientes para fazer as chamadas necessárias ao serviço da AWS e gerenciar os recursos da AWS.

* [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2.html) instalado e configurado


* [Git Instalado](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
* [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terr

* [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli?in=terraform/aws-get-started) instalado

Instruções de Deploy Aws com Terraform

1. Crie um novo diretório, navegue até esse diretório em um terminal e clone o repositório GitHub:
    ``` 
    git clone https://github.com/robinsonbrz/apigw-lambda-rest-dynamodb-terraform.git
    ```
2. Altere o diretório para o diretório do padrão:
    ```
    cd apigw-lambda-rest-dynamodb-terraform
    ```
3. ```cd infrastructure```

    3.1 Na linha de comando, inicialize o Terraform para baixar e instalar os provedores definidos na configuração:
    ```
    terraform init
    ```
4. Na linha de comando, aplique a configuração no arquivo main.tf:
    ```
    terraform apply
    ```
5. No prompts:
    * Enter yes
6. Observe as saídas do processo de implantação, elas contêm os nomes dos recursos e/ou ARNs que são usados para teste.

## 7. Anote o **apigwy_url** ao concluir o [terraform apply] esta será a Url da aplicação na AWS.

## Como funciona
Quando uma solicitação HTTP POST é enviada para o endpoint do Amazon API Gateway, a função AWS Lambda é invocada e insere um item na tabela do Amazon DynamoDB.

O método GET recebe os dados

## Testes de integração

Assim que a pilha for implantada, recupere o valor apigwy_url da saída do terraform apply, então faça uma chamada para o endpoint /movies usando curl ou Postman. Verifique a tabela do DynamoDB para certificar-se de que novos itens foram criados.

Foram disponibilizados alguns testes de integração na pasta tests/integration.

Para utilizar:

1. ```python -m venv .venv```
2. ```source .venv/bin/activate ```
3. Crie um arquivo .env na raiz do projeto com a sua apigw_url criada  no deploy da aplicação.
    
    Exemplo arquivo .env ```BASE_URL="https://e29laytl6g.execute-api.us-east-1.amazonaws.com"```

4. ```pip install -r requirements_dev_local.txt ```

5. Reinicie o terminal ou o VsCode para aplicar o .env

6. Execute o teste com pytest ``` pytest . -v ```

### Endpoints / Postman / Insomnia

Envie solicitações HTTP POST e inclua um corpo de solicitação no formato abaixo e a função lambda criará um novo item na tabela do DynamoDB

```
curl -X POST '<seu endpoint da API HTTP>'/movies \
 --header 'Content-Type: application/json' \
 -d '{"year":1977, "title":"Starwars"}' 
```
___


Todos Movies: GET /movies
GET  /movies
___

GET: Recupera movies por ID.

GET by id /movies/{id}

___

POST: Cria um filme. 

Endpoint: POST /movies
Body:
```json
{
    "year":"2010",
    "title":"Inception",
    "created_at":"2024-11-25 03:09:28",
    "approval_status":"pending",	
    "approved_date":"-"
}
```
___

PUT: Update an existing movie by ID. E posta uma mensagem AWS SQS.

Endpoint: PUT /movies/{id}
Body:
```json

{
  "year": "1983",
  "title": "Updated Movie Title",
  "approval_status": "approved"
}
```
___
PATCH: Update parcial movie por ID.  E posta uma mensagem AWS SQS.

Endpoint: PATCH /movies/{id}
Body:
```json
{
  "approval_status": "approved"
}

```
___
DELETE: Delete movie por ID.

```
curl -X DELETE '<your_api_endpoint>/movies?movie_id={id}'
```

___

HEAD: Check if a movie exists by ID.

Endpoint: HEAD /movies?id={id}

___


  <div>
  <h1 align="center"> Informações e contato </h1> 
  <div align="center">
    <table>
        </tr>
            <td>
                <a  href="https://www.linkedin.com/in/robinsonbrz/">
                <img src="https://raw.githubusercontent.com/robinsonbrz/robinsonbrz/main/static/img/linkedin.png" width="50" height="50">
            </td>
            <td>
                <a  href="https://www.linkedin.com/in/robinsonbrz/">
                <img  src="https://avatars.githubusercontent.com/u/18150643?s=96&amp;v=4" alt="@robinsonbrz" width="50" height="50">
            </td>
            <td>
                <a href="https://www.enedino.com.br/contato">
                <img src="https://raw.githubusercontent.com/robinsonbrz/robinsonbrz/main/static/img/gmail.png" width="50" height="50" ></a>
            </td>
        </tr>
    </table> 
  </div>
  <br>
  apigw-lambda-rest-dynamodb-terraform
</div>




























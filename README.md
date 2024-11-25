# Amazon API Gateway para AWS Lambda e Amazon DynamoDB com Terraform

Uma **Lambda function** controla eventos da **AWS ApiGateway** processando um CRUD Movie.

```json
{
    "id":"c5b9d146-6cbc-4353-9f47-c6210c561b6d",
    "year":"2010",
    "title":"Inception",
    "created_at":"2024-11-25 03:09:28",
    "approval_status":"approved",	
    "approved_date":"2024-11-25 03:10:49"
}
```

Ao criar um Movie com o método POST, o approval_status padrão do Movie é "pending".

Ao atualizarmos o approval_status para "approved" com o método PATCH ou PUT, uma mensagem Sqs é disparada. A mensagem **Sqs** é disparada caso o **"approval_status"** anterior seja **"pending"**, e a atualização solicite **"approved"**.

Uma segunda **Lambda function** é encarregada de receber essas mensagens **Sqs**, e atualiza o banco de dados **DynamoDb** com o novo estado do Movie para **"approval_status": "approved"**, e também registra o **"approved_date" : "2024-11-25 03:10:49"**.


### Método PATCH 

```json
{
"approval_status": "approved"
}
```

### Método PUT

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

Instruções de Implantação
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

## Como funciona
Quando uma solicitação HTTP POST é enviada para o endpoint do Amazon API Gateway, a função AWS Lambda é invocada e insere um item na tabela do Amazon DynamoDB.

O método GET recebe os dados

## Teste
Assim que a pilha for implantada, recupere o valor HttpApiEndpoint das saídas do terraform apply, então faça uma chamada para o endpoint /movies usando curl ou Postman. Verifique a tabela do DynamoDB para certificar-se de que novos itens foram criados.



Envie uma solicitação HTTP POST e inclua um corpo de solicitação no formato abaixo e a função lambda criará um novo item na tabela do DynamoDB

```
curl -X POST '<seu endpoint da API HTTP>'/movies \
 --header 'Content-Type: application/json' \
 -d '{"year":1977, "title":"Starwars"}' 
```


GET: Recupera movies por ID.

Todos Movies: GET /movies

Por ID: GET /movies/{id}

POST: Cria um filme. E posta uma mensagem AWS SQS.

Endpoint: POST /movies
Body:
```json

{
  "year": "1982",
  "title": "Some Movie Title"
}
```

PUT: Update an existing movie by ID.

Endpoint: PUT /movies/{id}
Body:
```json

{
  "year": "1983",
  "title": "Updated Movie Title"
}
```

PATCH: Update parcial movie por ID.

Endpoint: PATCH /movies?movie_id={id}
Body: (only include fields you want to update)
```json
{
  "title": "New Title"
}

# ou 
{   
    "title": "Updated Movie Title"
} 

```
DELETE: Delete movie por ID.



```
curl -X DELETE '<your_api_endpoint>/movies?movie_id={id}'
```



HEAD: Check if a movie exists by ID.

Endpoint: HEAD /movies?id={id}
OPTIONS: Get the allowed HTTP methods for the resource.





























## Limpeza
1. Altere o diretório para o diretório do padrão:
    ```
    cd apigw-lambda-dynamodb-terraform
    ```
2. Exclua todos os recursos criados
    ```bash
    terraform destroy
    ```
3. No prompt:
    * Enter yes
4. Confirme se todos os recursos criados foram excluídos
    ```bash
    terraform show
    ```

----


O código inicial original apenas com o método POST, pode ser encontrado em [Serverless Land Patterns](https://serverlessland.com/patterns/apigw-lambda-dynamodb-terraform).

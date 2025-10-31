Comecei criando um repositorio no GitHub chamado devops-project

Após isso, criei uma pasta dentro do VSCode chamado devops-project com duas pastas dentro, chamadas frontend e backend. Backend para guardar a API em python/flask e arquivo de requirements, inicialmente.

Então, para testar se a API esta funcionando corretamente, criei um ambiente virtual pelo terminal, instalei as dependencias e executei o servidor localmente. Funcionando corretamente.

Ainda na pasta backend, criei um Dockerfile. No terminal, fiz o build do Dockerfile através do comando [docker build -t(tag) backend-flask:0.1(nome da imagem) .]. E então com o comando [docker run -d(detached) -p(mapear a porta) 5000:5000(porta) backend-flask:0.1(imagem)], rodei a imagem.
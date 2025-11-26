terraform {
  required_providers {
    aws = { # define o provedor = AWS
      source  = "hashicorp/aws"
      version = "~> 5.0" # versao recente
    }

    kubernetes = { # provedor para o EKS
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
  }
}

provider "aws" {       # configurando o provider
  region = "us-east-1" # regiao definida
}

module "vpc" { # cria uma vpc usando um modulo pronto da aws
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.8.1" # versao estavel

  name = "eks-vpc"     # nome da vpc
  cidr = "10.0.0.0/16" # bloco de ip privado da vpc

  azs             = ["${var.region}a", "${var.region}b"] # az = availability zones, estamos usando 2 delas
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]       # as zonas estao guardadas em variaveis, encontradas na pasta variables.tf
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway   = true # permissao para que sub-redes privadas acessem a internet
  enable_dns_hostnames = true

  # tags para o eks saber que pode usar essa vpc
  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0" # versao estavel

  cluster_name    = "devops-project-cluster"
  cluster_version = "1.29" # versao do k8s

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  eks_managed_node_groups = { # configuracao dos nodes
    main_nodes = {            # quantidade de nodes
      min_size     = 1        # minimo de 1 servidor
      max_size     = 3        # caso tenham muitos inputs, chegara ate 3 servidores
      desired_size = 2        # tentar manter 2 servidores o tempo todo

      instance_types = ["t2.micro"] # tipo de maquina
    }
  }
}
import * as cdk from "aws-cdk-lib";
import { Cluster } from "aws-cdk-lib/aws-ecs";
import { Construct } from "constructs";
import { ECSDeploy } from "./constructs/ecs-deploy";
import { PrivateDnsNamespace } from "aws-cdk-lib/aws-servicediscovery";

interface RedisStackProps extends cdk.StackProps {
  namespace:PrivateDnsNamespace;
  cluster: Cluster;
  user:string;
  password: string;
  db:string
}

export class PostgresStack extends cdk.Stack {
  public readonly url: string;
  constructor(scope: Construct, id: string, props: RedisStackProps) {
    super(scope, id, props);
    const { cluster, password, db , user} = props;
    const service = new ECSDeploy(this, "PostgresDB", {
      cluster: cluster,
      namespace:props.namespace,
      containerName: "postgres",
      imageName: "postgres:14",
      port: 6379,
      environment: {
        POSTGRES_USER: user,
        POSTGRES_PASSWORD: password,
        POSTGRES_DB: db
      },
    });

    this.url = service.service.serviceName
  }
}

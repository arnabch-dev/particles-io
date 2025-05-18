import * as cdk from "aws-cdk-lib";
import { Cluster } from "aws-cdk-lib/aws-ecs";
import { Construct } from "constructs";
import { ECSDeploy } from "./constructs/ecs-deploy";
import { PrivateDnsNamespace } from "aws-cdk-lib/aws-servicediscovery";

interface RedisStackProps extends cdk.StackProps {
  namespace:PrivateDnsNamespace;
  cluster: Cluster;
  password: string;
}

export class RedisStack extends cdk.Stack {
  public readonly url: string;
  constructor(scope: Construct, id: string, props: RedisStackProps) {
    super(scope, id, props);
    const { cluster, password } = props;
    const service = new ECSDeploy(this, "RedisCache", {
      cluster: cluster,
      namespace:props.namespace,
      containerName: "redis",
      imageName: "redis:7",
      port: 6379,
      environment: {
        REDIS_PASSWORD: password,
      },
    });

    this.url = service.service.serviceName
  }
}

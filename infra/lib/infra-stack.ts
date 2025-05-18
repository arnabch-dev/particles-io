import * as cdk from "aws-cdk-lib";
import {
  InstanceClass,
  InstanceSize,
  InstanceType,
  Vpc,
} from "aws-cdk-lib/aws-ec2";
import { Cluster } from "aws-cdk-lib/aws-ecs";
import { Construct } from "constructs";
import * as servicediscovery from 'aws-cdk-lib/aws-servicediscovery';

export class InfraStack extends cdk.Stack {
  public readonly vpc: Vpc;
  public readonly cluster: Cluster;
  public readonly namespace:servicediscovery.PrivateDnsNamespace;

  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    this.vpc = new cdk.aws_ec2.Vpc(this, "ParticlesIO-VPC", {
      maxAzs: 1,
      natGateways: 0,
      subnetConfiguration: [
        {
          name: "PublicSubnet",
          subnetType: cdk.aws_ec2.SubnetType.PUBLIC,
        },
      ],
    });

    this.cluster = new Cluster(this, "ECS-Cluster", {
      vpc: this.vpc,
    });

    this.namespace = new servicediscovery.PrivateDnsNamespace(this,'ParticlesIO-DNS',{
      name:'local',
      vpc:this.vpc
    })

    // HACK: adding associatePublicIpAddress just for testing purpose and ssh into them
    // but it will be accessed via cloud discovery
    // can make the vpc subnet to be private since we will be using cloud discovery
    // not making it to test them
    this.cluster.addCapacity("ASG", {
      instanceType: InstanceType.of(InstanceClass.T2, InstanceSize.MICRO),
      desiredCapacity: 1,
      associatePublicIpAddress:true
    });
  }
}

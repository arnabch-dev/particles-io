import { Construct } from "constructs";
import * as ecs from "aws-cdk-lib/aws-ecs"
import { PrivateDnsNamespace } from "aws-cdk-lib/aws-servicediscovery";
export interface ECSDeployProps{
    cluster: ecs.Cluster,
    namespace:PrivateDnsNamespace,
    imageName:string,
    containerName:string,
    port:number,
    environment:Record<string,string>
}

export class ECSDeploy extends Construct{
    public readonly service: ecs.Ec2Service;
    constructor(scope:Construct,id:string,{imageName,containerName,environment,cluster,port,namespace}:ECSDeployProps){
        super(scope,id);
        const taskDef = new ecs.Ec2TaskDefinition(this,`${id}-${containerName}-EC2TaskDef`);

        taskDef.addContainer(containerName,{
            image:ecs.ContainerImage.fromRegistry(imageName),
            memoryLimitMiB:512,
            environment:environment,
            portMappings:[{containerPort:port}]
        })

        this.service = new ecs.Ec2Service(this,`${id}-${containerName}-Service`,{
            cluster:cluster,
            taskDefinition:taskDef,
            desiredCount:1,
            cloudMapOptions:{
                name:containerName,
                cloudMapNamespace:namespace
            }
        })
    }
}
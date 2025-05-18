#!/usr/bin/env node
import * as cdk from 'aws-cdk-lib';

import { InfraStack } from '../lib/infra-stack';
import { RedisStack } from '../lib/redis-stack';
import { PostgresStack } from '../lib/postgres-stack';
const env = {
    account: process.env.CDK_DEFAULT_ACCOUNT,
    region: process.env.CDK_DEFAULT_REGION,
  };

const app = new cdk.App();
const infra = new InfraStack(app, 'infra',{
    env
});

const redis = new RedisStack(app,'RedisStack',{
    cluster:infra.cluster,
    namespace:infra.namespace,
    password:process.env.REDIS_PASSWORD!,
    env
})
redis.addDependency(infra)

const postgres = new PostgresStack(app,'PgStack',{
    cluster:infra.cluster,
    namespace:infra.namespace,
    user:process.env.PG_USER!,
    db:process.env.PG_DB!,
    password:process.env.PG_PASSWORD!,
    env
})
postgres.addDependency(infra)
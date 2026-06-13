output "eks_cluster_name" {
  value = module.eks.cluster_name
}

output "rds_endpoint" {
  value = aws_db_instance.postgres.endpoint
}

output "msk_bootstrap_brokers_tls" {
  value = aws_msk_cluster.kafka.bootstrap_brokers_tls
}

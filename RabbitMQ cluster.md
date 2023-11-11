1-RabbitMQ cluster
* add rabit handler : in rabbitMq service or new service add consumer/puplisher
* consumer ---> publisher : - if it receive from it's own network vm ---> publish to rest rabbitMq cluster
                            - if it receive from different network ---> apply message to backend listener than database

2-Perf
* benshmark the time from write request made in env1 to apply to db in env2
  
3-LoadBalancing
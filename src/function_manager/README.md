# Action Controller

## config file
the config file defines all functions workable on this machine. it should be a yaml file like the following:
```yaml
functions:
  - name: utility
    qos_time: 100
    qos_requirement: 0.99
    max_containers : 10
    packages:
      - numpy
      - scipy
```

the meaning of each field:
- `functions`: a list containing all functions.
  - `name`: the name of function.
  - `qos_time`: the maximum execution time of QOS requirement.
  - `qos_requirement`: the precentage that should meet the QOS requirment.
  - `max_containers`: the maximum number of containers that the function can create for itself.
  - `packages`: a list containing all packages that the function need.
  

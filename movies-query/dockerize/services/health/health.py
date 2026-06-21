def create(amount):
    services = {}
    for i in range(amount):
        services[f'health_{i}'] = {
            'container_name': f'health_checker_{i}',
            'image': 'health:latest',
            'networks': ['tp_net'],
            'environment': [f'ID={i}'],
            'volumes': '/var/run/docker.sock:/var/run/docker.sock'
        }
    return services
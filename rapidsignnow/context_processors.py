import os



def global_settings(request):
    
    # return any necessary values
    return {
        'ENVIRONMENT': os.environ.get("ENV"),
    }
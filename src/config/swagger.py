template = {
    "swagger": "2.0",
    "info": {
        "title": "Simple Farm Manager API",
        "description": "API for farm management",
        "contact": {
            "responsibleOrganization": "",
            "responsibleDeveloper": "",
            "email": "njorogetimk@gmail.com",
            "url": "",
        },
        "termsOfService": "",
        "version": "22.09.0"
    },
    "host": "farm-manager-api.herokuapp.com",
    "basePath": "/api/v1",  # base bash for blueprint registration
    "schemes": [
        "http",
        "https"
    ],
    "securityDefinitions": {
        "Bearer": {
            "type": "apiKey",
            "name": "Authorization",
            "in": "header",
            "description": "JWT Authorization header using the Bearer scheme. Example: \"Authorization: Bearer {token}\""
        }
    },
}

swagger_config = {
    "headers": [
    ],
    "specs": [
        {
            "endpoint": 'apispec',
            "route": '/apispec.json',
            "rule_filter": lambda rule: True,  # all in
            "model_filter": lambda tag: True,  # all in
        }
    ],
    "static_url_path": "/flasgger_static",
    "swagger_ui": True,
    "specs_route": "/"
}

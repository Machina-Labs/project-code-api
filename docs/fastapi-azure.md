# FastAPI-Azure-Auth implements Azure AD and Azure AD B2C authentication and authorization for your FastAPI APIs and OpenAPI documentation.

<https://intility.github.io/fastapi-azure-auth/multi-tenant/fastapi_configuration> 
In the sidebar to the left you'll be able to find information on how to configure both Azure and your FastAPI application. If you need an example project, one can be found on GitHub here.

The first step is to decide whether your application should be single- or multi-tenant or using B2C. You can always change this later, so if you're unsure, you should choose single-tenant.

Even though FastAPI-Azure-Auth supports both v1 and v2 tokens, if you're creating a new project, you should use v2 tokens. We'll walk you through all the steps in this tutorial. If you have a project up and running already, and want to change from v1 to v2, you can do so in the manifest. To read about the difference between v1 and v2 tokens, check out this article.

# Multi tenant - Azure Configuration

Azure configuration

We'll need to create two application registrations for Azure AD authentication to cover both direct API use and usage from the OpenAPI (swagger) documentation.

We'll start with the API.
Backend API
Step 1 - Create app registration

Head over to Azure -> Azure Active Directory -> App registrations, and create a new registration.

Select a fitting name for your project; Azure will present the name to the user during consent.

    Supported account types: Multitenant - If you want to create a multi-tenant application, you should head over to the multi-tenant documentation
    Redirect URI: Choose Web and http://localhost:8000 as a value

1_application_registration

Press Register
Step 2 - Change token version to v2

First we'll change the token version to version 2. In the left menu bar, click Manifest and find the line that says accessTokenAcceptedVersion. Change its value from null to 2.

2_manifest

Press Save

(This change can take some time to happen, which is why we do this first.)
Step 3 - Note down your application IDs

Go back to the Overview, found in the left menu.

3_overview

Copy the Application (Client) ID, we'll need that for later. I like to use .env files to store variables like these:
.env

APP_CLIENT_ID=

Step 4 - Add an application scope

    Go to Expose an API in the left menu bar under your app registration.
    Press + Add a scope
    Press Save and continue

4_add_scope

Add a scope named user_impersonation that can be consented by Admins and users. 5_add_scope_props

You can use the following descriptions:

Access API as user
Allows the app to access the API as the user.

Access API as you
Allows the app to access the API as you.

OpenAPI Documentation

Our OpenAPI documentation will use the Authorization Code Grant Flow, with Proof Key for Code Exchange flow. It's a flow that enables a user of a Single-Page Application to safely log in, consent to permissions and fetch an access_token in the JWT format. When the user clicks Try out on the APIs, the access_token is attached to the header as a Bearer token. This is the token the backend will validate.

So, let's set it up!
Step 1 - Create app registration

Just like in the previous chapter, we have to create an application registration for our OpenAPI.

Head over to Azure -> Azure Active Directory -> App registrations, and create a new registration.

Use the same name, but with - OpenAPI appended to it.

    Supported account types: Multitenant
    Redirect URI: Choose Single-Page Application (SPA) and http://localhost:8000/oauth2-redirect as a value

6_application_registration_openapi

Press Register
Step 2 - Change token version to v2

Like last time, we'll change the token version to version 2. In the left menu bar, click Manifest and find the line that says accessTokenAcceptedVersion. Change its value from null to 2.

3_manifest

Press Save
Step 3 - Note down your application IDs

You should now be redirected to the Overview.

7_overview_openapi

Copy the Application (Client) ID and save it as your OPENAPI_CLIENT_ID:
.env

APP_CLIENT_ID=
OPENAPI_CLIENT_ID=

Step 4 - Allow OpenAPI to talk to the backend

To allow OpenAPI to talk to the backend API, you must add API permissions to the OpenAPI app registration. In the left menu, go to API Permissions and Add a permission.

8_api_permissions

Select the user_impersonation scope, and press Add a permission.

Your view should now look something like this:

9_api_permissions_finish

That's it! Next step is to configure the FastAPI application.

# Multi tenant - FastAPI configuration

FastAPI configuration

We'll do the simplest setup possible in these docs, through a one-file main.py. However, it's highly recommended that you read the chapters about bigger applications here, and invest in a good project structure.

We assume you've done the FastAPI tutorial and have dependencies installed, such as FastAPI and Gunicorn.

For a more "real life" project example, look at the demo_project on GitHub. This is configured as a single-tenant, but can easily be converted into a multi-tenant if you follow along here.
Getting started

First, either create your .env file and fill out your variables or insert them directly in your settings later.
.env

APP_CLIENT_ID=
OPENAPI_CLIENT_ID=

Create your main.py file:
main.py

from fastapi import FastAPI
import uvicorn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

Run your application and ensure that everything works on <http://localhost:8000/docs>
info

You need to run the application on the configured port in Azure AD for the next steps to work!
Add your settings

First, add your settings to the application. We'll need these later. The way I've set it up will look for a .env-file to populate your settings, but you can also just set a default value directly.
main.py

import uvicorn
from fastapi import FastAPI
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

Configure CORS

Now, let's configure our CORS. Without CORS your OpenAPI docs won't work as expected:
main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[Union[str, AnyHttpUrl]] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()

app = FastAPI()

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

Configure OpenAPI Documentation

In order for our OpenAPI documentation to work, we have to configure a few settings directly in the FastAPI application.
main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()

app = FastAPI(
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

The swagger_ui_oauth2_redirect_url setting for redirect should be as configured in Azure AD. The swagger_ui_init_oauth are standard mapped OpenAPI properties. You can find documentation about them here

We've used two flags: usePkceWithAuthorizationCodeGrant, which is the authentication flow. clientId is our application Client ID, which will autofill a field for the end users later.
Implementing FastAPI-Azure-Auth

Now, the fun part begins! 🚀

Import the MultiTenantAzureAuthorizationCodeBearer from fastapi_azure_auth and configure it:
main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()

app = FastAPI(
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    scopes={
        f'api://{settings.APP_CLIENT_ID}/user_impersonation': 'user_impersonation',
    },
    validate_iss=False
)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

As you can see we've set validate_iss to False. This will make sure FastAPI-Azure-Auth don't check which issuer (known as iss) the token has. In other words, we do not care which tenant the user was authenticating through. If you only want to allow a few tenants to access your API (such as your customers), see Accept specific tenants only,
Add loading of OpenID Configuration on startup

By adding on_event('startup') we're able to load the OpenID configuration immediately, instead of doing it when the first user authenticates. This isn't required, but makes things a bit quicker. When 24 hours has passed, the configuration will be considered out of date, and update when a user does a request. You can use background tasks to refresh it before that happens if you'd like.
main.py

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()

app = FastAPI(
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    scopes={
        f'api://{settings.APP_CLIENT_ID}/user_impersonation': 'user_impersonation',
    },
    validate_iss=False
)

@app.on_event('startup')
async def load_config() -> None:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

Adding authentication to our view

There's two ways of adding dependencies in FastAPI. You can use Depends() or Security(). Security() has an extra property called scopes. FastAPI-Azure-Auth support both, but if you use Security() you can also lock down your API views based on the scope.

Let's do that:
main.py

import uvicorn
from fastapi import FastAPI, Security
from fastapi.middleware.cors import CORSMiddleware
from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from fastapi_azure_auth import MultiTenantAzureAuthorizationCodeBearer

class Settings(BaseSettings):
    BACKEND_CORS_ORIGINS: list[str | AnyHttpUrl] = ['http://localhost:8000']
    OPENAPI_CLIENT_ID: str = ""
    APP_CLIENT_ID: str = ""

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=True
    )

settings = Settings()

app = FastAPI(
    swagger_ui_oauth2_redirect_url='/oauth2-redirect',
    swagger_ui_init_oauth={
        'usePkceWithAuthorizationCodeGrant': True,
        'clientId': settings.OPENAPI_CLIENT_ID,
    },
)

if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

azure_scheme = MultiTenantAzureAuthorizationCodeBearer(
    app_client_id=settings.APP_CLIENT_ID,
    scopes={
        f'api://{settings.APP_CLIENT_ID}/user_impersonation': 'user_impersonation',
    },
    validate_iss=False
)

@app.on_event('startup')
async def load_config() -> None:
    """
    Load OpenID config on startup.
    """
    await azure_scheme.openid_config.load_config()

@app.get("/", dependencies=[Security(azure_scheme)])
async def root():
    return {"message": "Hello World"}

if __name__ == '__main__':
    uvicorn.run('main:app', host='localhost', port=8000, reload=True)

Testing it out

Head over to your OpenAPI documentation at <http://localhost:8000/docs> and check out your API documentation. You'll see a new button called Authorize. Before clicking it, try out your API to see that you're unauthorized.

fastapi_1_authorize_button fastapi_2_not_authenticated

Now, let's authenticate. Click the Authorize button. Check your scope, and leave Client secret blank. You do not need that with the PKCE flow.

fastapi_3_authenticate

Consent to the permissions requested:

fastapi_4_consent
info

If you get a warning that your redirect URL is wrong, you're probably using 127.0.0.1 instead of localhost

Try out your API again to see that it works!
Last thing..

As discussed earlier, there is a scope parameter to the Security() version of Depends(). If you'd want to lock down your API to only be accessible by those with certain scopes, you can simply pass it into the dependency.

@app.get("/", dependencies=[Security(azure_scheme, scopes=['wrong_scope'])])

If you do this and try out your API again, you'll see that you're denied.

You're now safe and secure! Good luck! 🔒🚀


# Accessing the user object

You can access your user object in two ways, either with Depends(<schema name>) or with request.state.user.
Depends(<schema name>)

    Python 3.9 or above
    Python 3.8

depends_api_example.py

from fastapi import APIRouter, Depends

from demo_project.api.dependencies import azure_scheme
from fastapi_azure_auth.user import User

router = APIRouter()

@router.get(
    '/hello-user',
    response_model=User,
    operation_id='helloWorldApiKey',
)
async def hello_user(user: User = Depends(azure_scheme)) -> dict[str, bool]:
    """
    Wonder how this auth is done?
    """
    return user.dict()

request.state.user

    Python 3.9 or above
    Python 3.8

request_state_user_api_example.py

from fastapi import APIRouter, Depends, Request

from demo_project.api.dependencies import azure_scheme
from fastapi_azure_auth.user import User

router = APIRouter()

@router.get(
    '/hello-user',
    response_model=User,
    operation_id='helloWorldApiKey',
    dependencies=[Depends(azure_scheme)]
)
async def hello_user(request: Request) -> dict[str, bool]:
    """
    Wonder how this auth is done?
    """
    return request.state.user.dict()

# Calling your APIs from Python 

Calling your APIs from Python
Azure setup

In order to call your APIs from Python (or any other backend), you should use the Client Credential Flow.

    Navigate to Azure -> Azure Active Directory -> App registrations and find your OpenAPI application registration*
    Navigate over to Certificate & secrets
    Click New client secret
    Give it a name and an expiry time
    Click Add

info

In this example, we used the already created OpenAPI app registration in order to keep it short, but in reality you should create a new app registration for every application talking to your backend. In other words, if someone wants to use your API, they should create their own app registration and their own secret.

secret_picture
info

You can use client certificates too, but we won't cover this here.

    Copy the secret and save it for later.

copy_secret
FastAPI setup

The basic process is to first fetch the access token from Azure, and then call your own API endpoint.
Single- and multi-tenant
my_script.py

import asyncio
from httpx import AsyncClient
from demo_project.core.config import settings

async def main():
    async with AsyncClient() as client:
        azure_response = await client.post(
            url=f'<https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/token>',
            data={
                'grant_type': 'client_credentials',
                'client_id': settings.OPENAPI_CLIENT_ID,  # the ID of the app reg you created the secret for
                'client_secret': settings.CLIENT_SECRET,  # the secret you created
                'scope': f'api://{settings.APP_CLIENT_ID}/.default',  # note: NOT .user_impersonation
            }
        )
        token = azure_response.json()['access_token']

        my_api_response = await client.get(
            'http://localhost:8000/api/v1/hello-graph',
            headers={'Authorization': f'Bearer {token}'},
        )
        print(my_api_response.json())

if __name__ == '__main__':
    asyncio.run(main())

B2C

Compared to the above, the only differences are the scope and url parameters:
my_script.py

import asyncio
from httpx import AsyncClient
from demo_project.core.config import settings

async def main():
    async with AsyncClient() as client:
        azure_response = await client.post(
            url=f'https://{settings.TENANT_NAME}.b2clogin.com/{settings.TENANT_NAME}.onmicrosoft.com/{settings.AUTH_POLICY_NAME}/oauth2/v2.0/token',
            data={
                'grant_type': 'client_credentials',
                'client_id': settings.OPENAPI_CLIENT_ID,  # the ID of the app reg you created the secret for
                'client_secret': settings.CLIENT_SECRET,  # the secret you created
                'scope': f'https://{settings.TENANT_NAME}.onmicrosoft.com/{settings.APP_CLIENT_ID}/.default',
            }
        )
        token = azure_response.json()['access_token']

        my_api_response = await client.get(
            'http://localhost:8000/api/v1/hello-graph',
            headers={'Authorization': f'Bearer {token}'},
        )
        print(my_api_response.json())

if __name__ == '__main__':
    asyncio.run(main())

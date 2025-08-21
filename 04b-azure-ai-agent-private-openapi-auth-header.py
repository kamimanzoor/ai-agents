import asyncio
import os
import jsonref
import httpx
from azure.identity.aio import DefaultAzureCredential
from dotenv import load_dotenv
from semantic_kernel.connectors.openapi_plugin.openapi_function_execution_parameters import (
        OpenAPIFunctionExecutionParameters,
    )
from semantic_kernel.agents import AzureAIAgent, AzureAIAgentSettings, AzureAIAgentThread

async def main():
    load_dotenv()
    azure_ai_agent_settings = AzureAIAgentSettings()
    weather_asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "weather_openapi.json"))
    electricity_asset_file_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "electricity_openapi.json"))
    with open(weather_asset_file_path, "r") as f:
        openapi_weather = jsonref.loads(f.read())
    with open(electricity_asset_file_path, "r") as f:
        openapi_electricity = jsonref.loads(f.read())
    async with (
        DefaultAzureCredential(exclude_environment_credential=True,
                               exclude_managed_identity_credential=True) as creds,
                            AzureAIAgent.create_client(credential=creds) as project_client):

        AGENT_NAME = "SKMCPAIAgent"
        AGENT_INSTRUCTIONS = """
        You are an AI assistant designed to answer user questions using only the information retrieved from the tools.
        """
        agent = await project_client.agents.create_agent(
            model=azure_ai_agent_settings.model_deployment_name,  # This model should match your Azure OpenAI deployment.
            name=AGENT_NAME,
            instructions=AGENT_INSTRUCTIONS,
        )

        print(f"Created agent, ID: {agent.id}")

        # Wrap the agent in a Semantic Kernel agent

        agent = AzureAIAgent(
            client=project_client,
            definition=agent,
        )
        # Read API key from environment variable or set directly
        api_key=os.environ["API_ACCESS_TOKEN"]
        # print(f"Using API key: {api_key}")
        agent.kernel.add_plugin_from_openapi(
            plugin_name="WeatherPlugin",
            openapi_parsed_spec=openapi_weather
        )

        # print("✅ Created OpenAPI plugin")

        http_client = httpx.AsyncClient(
            headers={"Authorization": f"Bearer {api_key}"}
        )
        agent.kernel.add_plugin_from_openapi(
            plugin_name="ElectricityPlugin",
            openapi_parsed_spec=openapi_electricity,
            execution_settings=OpenAPIFunctionExecutionParameters(
            http_client=http_client
        ),
        )
        print("✅ Created OpenAPI plugin")

        thread: AzureAIAgentThread | None = None

        # # Example user queries.
        user_inputs = [
            "What was the electricity price in Copenhagen on 2025-01-01?"
        ]
        
        try:
            for user_input in user_inputs:
                print(f"# User: '{user_input}'")
                # Invoke the agent for the specified thread for response
                async for response in agent.invoke(messages=user_input, thread=thread, headers={"Authorization": f"Bearer {api_key}"}):
                    print(f"# {response.name}: {response}")
                    thread = response.thread
        finally:
            # Clean up resources.
            await thread.delete() if thread else None
            await project_client.agents.delete_agent(agent.id)
            print("\nCleaned up agent and thread")
        
if __name__ == "__main__":
    asyncio.run(main())

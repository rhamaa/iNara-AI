[Docs](https://docs.livekit.io/home/)

[GitHub](https://github.com/livekit/livekit) [Slack](https://livekit.io/join-slack)

Search

[Sign in with Cloud](https://cloud.livekit.io/login?r=/login_success?redirect_to=https://docs.livekit.io/agents/build/tools/)

[Home](https://docs.livekit.io/home/) [AI Agents](https://docs.livekit.io/agents/) [Telephony](https://docs.livekit.io/sip/) [Recipes](https://docs.livekit.io/recipes/) [Reference](https://docs.livekit.io/reference/)

On this page

[Overview](https://docs.livekit.io/agents/build/tools/#overview) [Tool definition](https://docs.livekit.io/agents/build/tools/#tool-definition) [Name and description](https://docs.livekit.io/agents/build/tools/#name-and-description) [Arguments and return value](https://docs.livekit.io/agents/build/tools/#arguments-and-return-value) [RunContext](https://docs.livekit.io/agents/build/tools/#runcontext) [Adding tools dynamically](https://docs.livekit.io/agents/build/tools/#adding-tools-dynamically) [Creating tools programmatically](https://docs.livekit.io/agents/build/tools/#creating-tools-programmatically) [Error handling](https://docs.livekit.io/agents/build/tools/#error-handling) [Forwarding to the frontend](https://docs.livekit.io/agents/build/tools/#forwarding) [Agent implementation](https://docs.livekit.io/agents/build/tools/#agent-implementation) [Frontend implementation](https://docs.livekit.io/agents/build/tools/#frontend-implementation) [Slow tool calls](https://docs.livekit.io/agents/build/tools/#slow-tool-calls) [External tools and MCP](https://docs.livekit.io/agents/build/tools/#external-tools-and-mcp) [Examples](https://docs.livekit.io/agents/build/tools/#examples) [Further reading](https://docs.livekit.io/agents/build/tools/#further-reading)

Copy page

## Overview

LiveKit Agents has full support for LLM tool use. This feature allows you to create a custom library of tools to extend your agent's context, create interactive experiences, and overcome LLM limitations. Within a tool, you can:

- Generate [agent speech](https://docs.livekit.io/agents/build/audio/) with `session.say()` or `session.generate_reply()`.
- Call methods on the frontend using [RPC](https://docs.livekit.io/home/client/data/rpc/).
- Handoff control to another agent as part of a [workflow](https://docs.livekit.io/agents/build/workflows/).
- Store and retrieve session data from the `context`.
- Anything else that a Python function can do.
- [Call external APIs or lookup data for RAG](https://docs.livekit.io/agents/build/external-data/).

## Tool definition

Add tools to your agent class with the `@function_tool` decorator. The LLM has access to them automatically.

```

from livekit.agents import function_tool, Agent, RunContext

class MyAgent(Agent):
    @function_tool()
    async def lookup_weather(
        self,
        context: RunContext,
        location: str,
    ) -> dict[str, Any]:
        """Look up weather information for a given location.

        Args:
            location: The location to look up weather information for.
        """

        return {"weather": "sunny", "temperature_f": 70}
```

**Best practices**

A good tool definition is key to reliable tool use from your LLM. Be specific about what the tool does, when it should or should not be used, what the arguments are for, and what type of return value to expect.

### Name and description

By default, the tool name is the name of the function, and the description is its docstring. Override this behavior with the `name` and `description` arguments to the `@function_tool` decorator.

### Arguments and return value

The tool arguments are copied automatically by name from the function arguments. Type hints for arguments and return value are included, if present.

Place additional information about the tool arguments and return value, if needed, in the tool description.

### RunContext

Tools include support for a special `context` argument. This contains access to the current `session`, `function_call`, `speech_handle`, and `userdata`. Consult the documentation on [speech](https://docs.livekit.io/agents/build/audio/) and [state within workflows](https://docs.livekit.io/agents/build/workflows/) for more information about how to use these features.

### Adding tools dynamically

You can exercise more control over the tools available by setting the `tools` argument directly.

To share a tool between multiple agents, define it outside of their class and then provide it to each. The `RunContext` is especially useful for this purpose to access the current session, agent, and state.

Tools set in the `tools` value are available alongside any registered within the class using the `@function_tool` decorator.

```

from livekit.agents import function_tool, Agent, RunContext

@function_tool()
async def lookup_user(
    context: RunContext,
    user_id: str,
) -> dict:
    """Look up a user's information by ID."""

    return {"name": "John Doe", "email": "john.doe@example.com"}

class AgentA(Agent):
    def __init__(self):
        super().__init__(
            tools=[lookup_user],
            # ...
        )

class AgentB(Agent):
    def __init__(self):
        super().__init__(
            tools=[lookup_user],
            # ...
        )
```

Use `agent.update_tools()` to update available tools after creating an agent. This replaces _all_ tools, including those registered automatically within the agent class. To reference existing tools before replacement, access the `agent.tools` property:

```

# add a tool
agent.update_tools(agent.tools + [tool_a])

# remove a tool
agent.update_tools(agent.tools - [tool_a])

# replace all tools
agent.update_tools([tool_a, tool_b])
```

### Creating tools programmatically

To create a tool on the fly, use `function_tool` as a function rather than as a decorator. You must supply a name, description, and callable function. This is useful to compose specific tools based on the same underlying code or load them from external sources such as a database or Model Context Protocol (MCP) server.

In the following example, the app has a single function to set any user profile field but gives the agent one tool per field for improved reliability:

```

from livekit.agents import function_tool, RunContext

class Assistant(Agent):
    def _set_profile_field_func_for(self, field: str):
        async def set_value(context: RunContext, value: str):
            # custom logic to set input
            return f"field {field} was set to {value}"

        return set_value

    def __init__(self):
        super().__init__(
            tools=[\
                function_tool(self._set_profile_field_func_for("phone"),\
                              name="set_phone_number",\
                              description="Call this function when user has provided their phone number."),\
                function_tool(self._set_profile_field_func_for("email"),\
                              name="set_email",\
                              description="Call this function when user has provided their email."),\
                # ... other tools ...\
            ],
            # instructions, etc ...
        )
```

## Error handling

Raise the `ToolError` exception to return an error to the LLM in place of a response. You can include a custom message to describe the error and/or recovery options.

```

@function_tool()
async def lookup_weather(
    self,
    context: RunContext,
    location: str,
) -> dict[str, Any]:
    if location == "mars":
        raise ToolError("This location is coming soon. Please join our mailing list to stay updated.")
    else:
        return {"weather": "sunny", "temperature_f": 70}
```

## Forwarding to the frontend

Forward tool calls to a frontend app using [RPC](https://docs.livekit.io/home/client/data/rpc/). This is useful when the data needed to fulfill the function call is only available at the frontend. You may also use RPC to trigger actions or UI updates in a structured way.

For instance, here's a function that accesses the user's live location from their web browser:

### Agent implementation

```

from livekit.agents import function_tool, get_job_context, RunContext

@function_tool()
async def get_user_location(
    context: RunContext,
    high_accuracy: bool
):
    """Retrieve the user's current geolocation as lat/lng.

    Args:
        high_accuracy: Whether to use high accuracy mode, which is slower but more precise

    Returns:
        A dictionary containing latitude and longitude coordinates
    """
    try:
        room = get_job_context().room
        participant_identity = next(iter(room.remote_participants))
        response = await room.local_participant.perform_rpc(
            destination_identity=participant_identity,
            method="getUserLocation",
            payload=json.dumps({
                "highAccuracy": high_accuracy
            }),
            response_timeout=10.0 if high_accuracy else 5.0,
        )
        return response
    except Exception:
        raise ToolError("Unable to retrieve user location")
```

### Frontend implementation

The following example uses the JavaScript SDK. The same pattern works for other SDKs. For more examples, see the [RPC documentation](https://docs.livekit.io/home/client/data/rpc/).

```

import { RpcError, RpcInvocationData } from 'livekit-client';

localParticipant.registerRpcMethod(
    'getUserLocation',
    async (data: RpcInvocationData) => {
        try {
            let params = JSON.parse(data.payload);
            const position: GeolocationPosition = await new Promise((resolve, reject) => {
                navigator.geolocation.getCurrentPosition(resolve, reject, {
                    enableHighAccuracy: params.highAccuracy ?? false,
                    timeout: data.responseTimeout,
                });
            });

            return JSON.stringify({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
            });
        } catch (error) {
            throw new RpcError(1, "Could not retrieve user location");
        }
    }
);
```

## Slow tool calls

For best practices on providing feedback to the user during long-running tool calls, see the section on [user feedback](https://docs.livekit.io/agents/build/external-data/#user-feedback) in the External data and RAG guide.

## External tools and MCP

To load tools from an external source as a Model Context Protocol (MCP) server, use the `function_tool` function and register the tools with the `tools` property or `update_tools()` method. See the following example for a complete MCP implementation:

[ModelContextProtocol\\
\\
**Agent With MCP Tools** \\
\\
A voice AI agent that can load dynamic tools from one or more Model Context Protocol (MCP) server.](https://github.com/livekit-examples/basic-mcp)

## Examples

The following additional examples show how to use tools in different ways:

[**Use of enum** \\
\\
Example showing how to annotate arguments with enum.](https://github.com/livekit/agents/blob/main/examples/voice_agents/annotated_tool_args.py) [**Dynamic tool creation** \\
\\
Complete example with dynamic tool lists.](https://github.com/livekit/agents/blob/main/examples/voice_agents/dynamic_tool_creation.py) [ModelContextProtocol\\
\\
**Agent With MCP Tools** \\
\\
A voice AI agent that can load dynamic tools from one or more Model Context Protocol (MCP) server.](https://github.com/livekit-examples/basic-mcp) [**LiveKit Docs RAG** \\
\\
An agent that can answer questions about LiveKit with lookups against the docs website.](https://github.com/livekit-examples/python-agents-examples/tree/main/rag)

## Further reading

The following articles provide more information about the topics discussed in this guide:

[**RPC** \\
\\
Complete documentation on function calling between LiveKit participants.](https://docs.livekit.io/home/client/data/rpc/) [**Agent speech** \\
\\
More information about precise control over agent speech output.](https://docs.livekit.io/agents/build/audio/) [**Workflows** \\
\\
Read more about handing off control to other agents.](https://docs.livekit.io/agents/build/workflows/) [**External data and RAG** \\
\\
Best practices for adding context and taking external actions.](https://docs.livekit.io/agents/build/external-data/)

On this page

[Overview](https://docs.livekit.io/agents/build/tools/#overview) [Tool definition](https://docs.livekit.io/agents/build/tools/#tool-definition) [Name and description](https://docs.livekit.io/agents/build/tools/#name-and-description) [Arguments and return value](https://docs.livekit.io/agents/build/tools/#arguments-and-return-value) [RunContext](https://docs.livekit.io/agents/build/tools/#runcontext) [Adding tools dynamically](https://docs.livekit.io/agents/build/tools/#adding-tools-dynamically) [Creating tools programmatically](https://docs.livekit.io/agents/build/tools/#creating-tools-programmatically) [Error handling](https://docs.livekit.io/agents/build/tools/#error-handling) [Forwarding to the frontend](https://docs.livekit.io/agents/build/tools/#forwarding) [Agent implementation](https://docs.livekit.io/agents/build/tools/#agent-implementation) [Frontend implementation](https://docs.livekit.io/agents/build/tools/#frontend-implementation) [Slow tool calls](https://docs.livekit.io/agents/build/tools/#slow-tool-calls) [External tools and MCP](https://docs.livekit.io/agents/build/tools/#external-tools-and-mcp) [Examples](https://docs.livekit.io/agents/build/tools/#examples) [Further reading](https://docs.livekit.io/agents/build/tools/#further-reading)

HomeAI AgentsTelephonyRecipesReference

[GitHub](https://github.com/livekit/livekit) [Slack](https://livekit.io/join-slack)

[Sign in](https://cloud.livekit.io/login?r=/login_success?redirect_to=https://docs.livekit.io/agents/build/tools/)

Search